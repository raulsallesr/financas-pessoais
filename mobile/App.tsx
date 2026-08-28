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
import { currentSnapshot } from "./src/data/currentSnapshot";
import { ALL_CLASSES, ClassFilter } from "./src/domain/insights";
import {
  createPrivatePortfolio,
  PrivatePortfolioV1,
} from "./src/domain/privatePortfolio";
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
import { colors } from "./src/theme";

type PortfolioState =
  | { kind: "loading" }
  | { kind: "demo" }
  | { kind: "local"; document: PrivatePortfolioV1 }
  | { kind: "unavailable"; message: string }
  | { kind: "error"; message: string };

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
  const [shockBps, setShockBps] = useState(0);
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

  const renderScreen = () => {
    if (activeTab === "portfolio") {
      return (
        <PortfolioScreen
          mode={portfolioState.kind}
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
          onShockChange={setShockBps}
          portfolioMode={portfolioState.kind}
          shockBps={shockBps}
          snapshot={effectiveSnapshot}
        />
      );
    }
    if (activeTab === "learn") {
      return <LearnScreen />;
    }
    return (
      <TodayScreen
        classFilter={classFilter}
        onClassFilter={setClassFilter}
        onNavigate={setActiveTab}
        onSelectSignal={setSelectedSignalId}
        portfolioMode={portfolioState.kind}
        selectedSignalId={selectedSignalId}
        snapshot={effectiveSnapshot}
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
