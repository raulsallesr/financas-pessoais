import { useEffect, useMemo, useState } from "react";
import {
  BackHandler,
  Platform,
  StyleSheet,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import {
  initialWindowMetrics,
  SafeAreaProvider,
  SafeAreaView,
} from "react-native-safe-area-context";

import { BottomNav, TabKey } from "./src/components/BottomNav";
import { WeeklyReviewStep } from "./src/components/WeeklyReviewPanel";
import {
  currentPublicSnapshot,
  currentSnapshot,
} from "./src/data/currentSnapshot";
import {
  createFavoriteSignals,
  FavoriteSignalsV1,
  toggleFavoriteSignal,
} from "./src/domain/favorites";
import { ALL_CLASSES, ClassFilter } from "./src/domain/insights";
import {
  createPrivatePortfolio,
  PrivatePortfolioV1,
} from "./src/domain/privatePortfolio";
import {
  createPublicSnapshotHistory,
  PublicSnapshotHistoryV1,
  recordPublicSnapshot,
} from "./src/domain/snapshotHistory";
import { Position } from "./src/domain/types";
import { LearnScreen } from "./src/screens/LearnScreen";
import { PortfolioScreen } from "./src/screens/PortfolioScreen";
import { ScenariosScreen } from "./src/screens/ScenariosScreen";
import { TodayScreen } from "./src/screens/TodayScreen";
import {
  clearSecurePortfolio,
  isSecurePortfolioStorageAvailable,
  loadSecurePortfolio,
  saveSecurePortfolio,
  SecurePortfolioStorageError,
} from "./src/storage/securePortfolioStorage";
import {
  isFavoriteSignalsStorageAvailable,
  loadFavoriteSignals,
  saveFavoriteSignals,
} from "./src/storage/favoriteSignalsStorage";
import {
  loadPublicSnapshotHistory,
  savePublicSnapshotHistory,
} from "./src/storage/publicSnapshotHistoryStorage";
import { colors } from "./src/theme";

type PortfolioState =
  | { kind: "loading" }
  | { kind: "demo" }
  | { kind: "local"; document: PrivatePortfolioV1 }
  | { kind: "unavailable"; message: string }
  | { kind: "error"; message: string };

type SnapshotHistoryState =
  | { kind: "loading" }
  | { kind: "ready"; history: PublicSnapshotHistoryV1 }
  | { kind: "unavailable"; message: string }
  | { kind: "error"; message: string };

type WeeklyReviewSession = {
  signalId: string;
  step: WeeklyReviewStep;
  scenarioVisited: boolean;
};

function storageErrorMessage(error: unknown): string {
  if (error instanceof SecurePortfolioStorageError) {
    return error.message;
  }
  return "Não foi possível abrir o cofre local. Seus dados não foram substituídos.";
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("today");
  const [selectedSignalId, setSelectedSignalId] = useState(
    currentSnapshot.signals[0].id,
  );
  const [classFilter, setClassFilter] = useState<ClassFilter>(ALL_CLASSES);
  const [shockBps, setShockBps] = useState(50);
  const [valuesHidden, setValuesHidden] = useState(false);
  const [favoriteSignals, setFavoriteSignals] = useState<FavoriteSignalsV1>(
    createFavoriteSignals(),
  );
  const [favoriteReady, setFavoriteReady] = useState(false);
  const [favoriteSaving, setFavoriteSaving] = useState(false);
  const [favoritePersistence, setFavoritePersistence] = useState<
    "native" | "session"
  >("session");
  const [favoriteMessage, setFavoriteMessage] = useState<string>();
  const [snapshotHistoryState, setSnapshotHistoryState] =
    useState<SnapshotHistoryState>({ kind: "loading" });
  const [weeklyReview, setWeeklyReview] =
    useState<WeeklyReviewSession | null>(null);
  const [portfolioState, setPortfolioState] = useState<PortfolioState>({
    kind: "loading",
  });

  useEffect(() => {
    let active = true;

    async function hydratePortfolio() {
      if (Platform.OS === "web") {
        if (active) {
          setPortfolioState({
            kind: "unavailable",
            message:
              "A bancada web mantém somente a carteira fictícia. O cofre privado está disponível nos apps Android e iOS.",
          });
        }
        return;
      }

      try {
        if (!(await isSecurePortfolioStorageAvailable())) {
          if (active) {
            setPortfolioState({
              kind: "unavailable",
              message: "O cofre nativo não está disponível neste dispositivo.",
            });
          }
          return;
        }
        const document = await loadSecurePortfolio();
        if (active) {
          setPortfolioState(document ? { kind: "local", document } : { kind: "demo" });
        }
      } catch (error) {
        if (active) {
          setPortfolioState({ kind: "error", message: storageErrorMessage(error) });
        }
      }
    }

    void hydratePortfolio();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function hydrateFavorites() {
      if (Platform.OS === "web") {
        if (active) {
          setFavoritePersistence("session");
          setFavoriteMessage(
            "Na bancada web, os favoritos duram somente nesta sessão.",
          );
          setFavoriteReady(true);
        }
        return;
      }
      try {
        if (!(await isFavoriteSignalsStorageAvailable())) {
          if (active) {
            setFavoritePersistence("session");
            setFavoriteMessage(
              "O armazenamento nativo não está disponível; favoritos ficam nesta sessão.",
            );
            setFavoriteReady(true);
          }
          return;
        }
        const stored = await loadFavoriteSignals();
        if (active) {
          setFavoriteSignals(stored ?? createFavoriteSignals());
          setFavoritePersistence("native");
          setFavoriteReady(true);
        }
      } catch {
        if (active) {
          setFavoritePersistence("session");
          setFavoriteMessage(
            "Os favoritos locais não puderam ser abertos; as mudanças valem nesta sessão.",
          );
          setFavoriteReady(true);
        }
      }
    }

    void hydrateFavorites();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function hydrateSnapshotHistory() {
      if (Platform.OS === "web") {
        if (active) {
          setSnapshotHistoryState({
            kind: "unavailable",
            message:
              "A bancada web não grava histórico. Use o app Android ou iOS para manter a linha do tempo local.",
          });
        }
        return;
      }
      if (!currentPublicSnapshot) {
        if (active) {
          setSnapshotHistoryState({
            kind: "unavailable",
            message:
              "A fotografia atual está em demonstração e não será adicionada ao histórico público.",
          });
        }
        return;
      }
      try {
        const stored =
          (await loadPublicSnapshotHistory()) ?? createPublicSnapshotHistory();
        const updated = recordPublicSnapshot(stored, currentPublicSnapshot);
        if (updated !== stored) {
          await savePublicSnapshotHistory(updated);
        }
        if (active) {
          setSnapshotHistoryState({ kind: "ready", history: updated });
        }
      } catch {
        if (active) {
          setSnapshotHistoryState({
            kind: "error",
            message:
              "A linha do tempo local não pôde ser aberta. A fotografia atual continua disponível sem histórico.",
          });
        }
      }
    }

    void hydrateSnapshotHistory();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (Platform.OS !== "android") {
      return undefined;
    }
    const subscription = BackHandler.addEventListener(
      "hardwareBackPress",
      () => {
        if (activeTab === "today") {
          return false;
        }
        setActiveTab("today");
        return true;
      },
    );
    return () => subscription.remove();
  }, [activeTab]);

  const effectiveSnapshot = useMemo(() => {
    const positions =
      portfolioState.kind === "local"
        ? portfolioState.document.positions
        : portfolioState.kind === "error"
          ? []
          : currentSnapshot.positions;
    return { ...currentSnapshot, positions };
  }, [portfolioState]);

  async function savePortfolioPositions(positions: readonly Position[]) {
    const document = createPrivatePortfolio(positions);
    await saveSecurePortfolio(document);
    setPortfolioState({ kind: "local", document });
  }

  async function resetPortfolio() {
    await clearSecurePortfolio();
    setPortfolioState({ kind: "demo" });
  }

  async function toggleSignalFavorite(signalId: string) {
    if (!favoriteReady || favoriteSaving) {
      return;
    }
    let next: FavoriteSignalsV1;
    try {
      next = toggleFavoriteSignal(favoriteSignals, signalId);
    } catch (error) {
      setFavoriteMessage(
        error instanceof Error ? error.message : "Não foi possível atualizar o favorito.",
      );
      return;
    }

    const previous = favoriteSignals;
    setFavoriteSignals(next);
    if (favoritePersistence === "session") {
      setFavoriteMessage("Favorito atualizado somente para esta sessão.");
      return;
    }

    setFavoriteSaving(true);
    setFavoriteMessage("Salvando favorito somente neste aparelho…");
    try {
      await saveFavoriteSignals(next);
      setFavoriteMessage(
        next.signalIds.includes(signalId)
          ? "Sinal salvo e movido para o início da lista."
          : "Sinal removido dos favoritos.",
      );
    } catch {
      setFavoriteSignals(previous);
      setFavoriteMessage(
        "Não foi possível salvar o favorito; a seleção anterior foi preservada.",
      );
    } finally {
      setFavoriteSaving(false);
    }
  }

  function startOrResumeWeeklyReview() {
    if (!weeklyReview) {
      setWeeklyReview({
        signalId: selectedSignalId,
        step: 0,
        scenarioVisited: false,
      });
    }
    setActiveTab("learn");
  }

  function changeWeeklyReviewStep(step: WeeklyReviewStep) {
    setWeeklyReview((current) =>
      current ? { ...current, step, scenarioVisited: false } : current,
    );
  }

  function exploreScenariosFromReview() {
    setWeeklyReview((current) =>
      current ? { ...current, step: 4, scenarioVisited: true } : current,
    );
    setActiveTab("scenarios");
  }

  function finishWeeklyReview() {
    if (weeklyReview) {
      setSelectedSignalId(weeklyReview.signalId);
    }
    setWeeklyReview(null);
    setActiveTab("today");
  }

  const snapshotHistory =
    snapshotHistoryState.kind === "ready"
      ? snapshotHistoryState.history
      : null;
  const reviewSignalLabel = weeklyReview
    ? effectiveSnapshot.signals.find(
        (signal) => signal.id === weeklyReview.signalId,
      )?.label ?? "Sinal selecionado"
    : undefined;

  const renderScreen = () => {
    if (activeTab === "portfolio") {
      return (
        <PortfolioScreen
          hidden={valuesHidden}
          mode={portfolioState.kind}
          onHiddenChange={setValuesHidden}
          onReset={resetPortfolio}
          onSavePositions={savePortfolioPositions}
          snapshot={effectiveSnapshot}
          storageMessage={
            portfolioState.kind === "unavailable" || portfolioState.kind === "error"
              ? portfolioState.message
              : undefined
          }
        />
      );
    }
    if (activeTab === "scenarios") {
      return (
        <ScenariosScreen
          hideAmounts={valuesHidden}
          onShockChange={setShockBps}
          onToggleAmounts={() => setValuesHidden((hidden) => !hidden)}
          portfolioMode={portfolioState.kind}
          reviewContext={
            weeklyReview?.scenarioVisited
              ? {
                  signalLabel: reviewSignalLabel ?? "Sinal selecionado",
                  onReturn: () => setActiveTab("learn"),
                }
              : undefined
          }
          shockBps={shockBps}
          snapshot={effectiveSnapshot}
        />
      );
    }
    if (activeTab === "learn") {
      return (
        <LearnScreen
          favoriteSignalIds={favoriteSignals.signalIds}
          onCancelReview={() => setWeeklyReview(null)}
          onExploreScenarios={exploreScenariosFromReview}
          onFinishReview={finishWeeklyReview}
          onStartReview={startOrResumeWeeklyReview}
          onStepChange={changeWeeklyReviewStep}
          reviewSignalId={weeklyReview?.signalId ?? selectedSignalId}
          reviewStep={weeklyReview?.step ?? null}
          snapshot={effectiveSnapshot}
          snapshotHistory={snapshotHistory}
        />
      );
    }
    return (
      <TodayScreen
        classFilter={classFilter}
        hideAmounts={valuesHidden}
        onClassFilter={setClassFilter}
        onNavigate={setActiveTab}
        onReviewWeek={startOrResumeWeeklyReview}
        onSelectSignal={setSelectedSignalId}
        portfolioMode={portfolioState.kind}
        selectedSignalId={selectedSignalId}
        snapshot={effectiveSnapshot}
        favoriteMessage={favoriteMessage}
        favoriteSaving={!favoriteReady || favoriteSaving}
        favoriteSignalIds={favoriteSignals.signalIds}
        onToggleFavorite={(signalId) => {
          void toggleSignalFavorite(signalId);
        }}
        reviewSignalId={weeklyReview?.signalId}
        snapshotHistory={snapshotHistory}
        snapshotHistoryLoading={snapshotHistoryState.kind === "loading"}
        snapshotHistoryMessage={
          snapshotHistoryState.kind === "unavailable" ||
          snapshotHistoryState.kind === "error"
            ? snapshotHistoryState.message
            : undefined
        }
      />
    );
  };

  return (
    <SafeAreaProvider initialMetrics={initialWindowMetrics}>
      <SafeAreaView
        edges={["top", "right", "bottom", "left"]}
        style={styles.safeArea}
      >
        <StatusBar style="dark" />
        <View accessibilityLanguage="pt-BR" style={styles.app}>
          <View style={styles.screen}>{renderScreen()}</View>
          <BottomNav activeTab={activeTab} onChange={setActiveTab} />
        </View>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.background,
  },
  app: {
    backgroundColor: colors.background,
    flex: 1,
  },
  screen: {
    flex: 1,
  },
});
