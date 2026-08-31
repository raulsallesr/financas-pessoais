import { useState } from "react";
import {
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from "react-native";

import { ImpactCard } from "../components/ImpactCard";
import { ExplainableAlertPanel } from "../components/ExplainableAlertPanel";
import { MarketSignalCard } from "../components/MarketSignalCard";
import { SnapshotHistoryPanel } from "../components/SnapshotHistoryPanel";
import {
  DataModePill,
  Eyebrow,
  formatSnapshotDate,
  PortfolioModePill,
  PortfolioPresentationMode,
  SectionHeading,
  Surface,
} from "../components/Primitives";
import { TabKey } from "../components/BottomNav";
import { buildExplainableAlert } from "../domain/explainableAlerts";
import { orderSignalsByFavorites } from "../domain/favorites";
import {
  ALL_CLASSES,
  allocationByClass,
  availableClasses,
  ClassFilter,
  impactedAllocation,
  impactsForSignal,
  largestPosition,
  signalCoverage,
  signalById,
} from "../domain/insights";
import { PublicSnapshotHistoryV1 } from "../domain/snapshotHistory";
import { MarketSnapshot } from "../domain/types";
import testIds from "../testing/testIds.json";
import { colors, radius, spacing } from "../theme";

export function TodayScreen({
  snapshot,
  selectedSignalId,
  onSelectSignal,
  classFilter,
  onClassFilter,
  onNavigate,
  portfolioMode,
  hideAmounts,
  favoriteSignalIds,
  favoriteMessage,
  favoriteSaving,
  onToggleFavorite,
  snapshotHistory,
  snapshotHistoryLoading,
  snapshotHistoryMessage,
}: {
  snapshot: MarketSnapshot;
  selectedSignalId: string;
  onSelectSignal: (signalId: string) => void;
  classFilter: ClassFilter;
  onClassFilter: (filter: ClassFilter) => void;
  onNavigate: (tab: TabKey) => void;
  portfolioMode: PortfolioPresentationMode;
  hideAmounts: boolean;
  favoriteSignalIds: readonly string[];
  favoriteMessage?: string;
  favoriteSaving: boolean;
  onToggleFavorite: (signalId: string) => void;
  snapshotHistory: PublicSnapshotHistoryV1 | null;
  snapshotHistoryLoading: boolean;
  snapshotHistoryMessage?: string;
}) {
  const [showAllSignals, setShowAllSignals] = useState(false);
  const { width } = useWindowDimensions();
  const isWide = width >= 720;
  const selectedSignal = signalById(snapshot, selectedSignalId);
  const impacts = impactsForSignal(snapshot, selectedSignalId, classFilter);
  const allocation = impactedAllocation(impacts);
  const classAllocation = allocationByClass(snapshot);
  const largest = largestPosition(snapshot);
  const coverage = signalCoverage(snapshot);
  const orderedSignals = orderSignalsByFavorites(
    snapshot.signals,
    favoriteSignalIds,
  );
  const visibleSignals = showAllSignals
    ? orderedSignals
    : orderedSignals.slice(0, 2);
  const explainableAlert = buildExplainableAlert(snapshot, selectedSignalId);
  const selectedSignalIsFavorite = favoriteSignalIds.includes(selectedSignalId);
  const isLocalPortfolio = portfolioMode === "local";
  const portfolioKind = isLocalPortfolio ? "carteira local" : "demonstração";
  const selectedSignalHasEffects = Object.keys(selectedSignal.effects).length > 0;
  const filters = [ALL_CLASSES, ...availableClasses(snapshot)] as const;
  const availableSources = snapshot.sources
    .filter((source) => source.available)
    .map((source) => source.label)
    .join(" · ");

  return (
    <ScrollView
      contentContainerStyle={[
        styles.content,
        isWide && styles.contentWide,
      ]}
      showsVerticalScrollIndicator={false}
      testID={testIds.screens.today}
    >
      <View style={styles.headerRow}>
        <View>
          <Text style={styles.brand}>FocusLens</Text>
          <Text style={styles.brandSupport}>INTELIGÊNCIA PARA SUA CARTEIRA</Text>
        </View>
        <DataModePill mode={snapshot.mode} />
      </View>

      {snapshot.fallbackReason ? (
        <Surface style={styles.fallbackNotice}>
          <Eyebrow>Demonstração local</Eyebrow>
          <Text style={styles.fallbackText}>{snapshot.fallbackReason}</Text>
        </Surface>
      ) : null}

      <Surface style={styles.portfolioPulse}>
        <View style={styles.portfolioPulseTopline}>
          <Eyebrow>Seu recorte</Eyebrow>
          <PortfolioModePill mode={portfolioMode} />
        </View>
        <Text style={styles.portfolioPulseTitle}>
          {snapshot.positions.length
            ? `${snapshot.positions.length} ${snapshot.positions.length === 1 ? "posição" : "posições"} em ${classAllocation.length} ${classAllocation.length === 1 ? "classe" : "classes"}`
            : "Sua carteira ainda não tem posições"}
        </Text>
        {snapshot.positions.length ? (
          <View style={styles.portfolioFacts}>
            <View style={styles.portfolioFact}>
              <View style={styles.portfolioFactCopy}>
                <Text style={styles.portfolioFactLabel}>Maior classe</Text>
                <Text style={styles.portfolioFactValue}>
                  {classAllocation[0]?.assetClass ?? "Sem classe"}
                </Text>
              </View>
              <Text style={styles.portfolioFactPercent}>
                {classAllocation[0]?.allocationPercent.toFixed(0) ?? "0"}%
              </Text>
            </View>
            <View style={styles.portfolioFactDivider} />
            <View style={styles.portfolioFact}>
              <View style={styles.portfolioFactCopy}>
                <Text style={styles.portfolioFactLabel}>Maior posição</Text>
                <Text style={styles.portfolioFactValue}>
                  {largest?.position.shortName ?? "Sem posição"}
                </Text>
              </View>
              <Text style={styles.portfolioFactPercent}>
                {largest?.allocationPercent.toFixed(0) ?? "0"}%
              </Text>
            </View>
            <View style={styles.portfolioFactDivider} />
            <View style={styles.portfolioFact}>
              <View style={styles.portfolioFactCopy}>
                <Text style={styles.portfolioFactLabel}>Relações atuais</Text>
                <Text style={styles.portfolioFactValue}>
                  {coverage.positionCount} de {snapshot.positions.length}{" "}
                  {snapshot.positions.length === 1 ? "posição" : "posições"}
                </Text>
              </View>
              <Text style={styles.portfolioFactPercent}>
                {coverage.allocationPercent.toFixed(0)}%
              </Text>
            </View>
          </View>
        ) : null}
        <Text style={styles.portfolioPulseSupport}>
          {coverage.positionCount
            ? `${coverage.allocationPercent.toFixed(0)}% da ${portfolioKind} possui uma relação direta já classificada pelos sinais públicos atuais.`
            : snapshot.positions.length
              ? `Os sinais atuais não têm relação direta classificada com a ${portfolioKind}. O FocusLens não força um impacto quando o motor não fornece esse elo.`
              : "Monte uma carteira local para enxergar concentração, classes e relações com os sinais públicos."}
        </Text>
        <Pressable
          accessibilityHint={
            isLocalPortfolio
              ? "Abre o simulador de sensibilidade sem alterar sua carteira"
              : "Abre a área para montar uma carteira somente neste aparelho"
          }
          accessibilityRole="button"
          onPress={() =>
            onNavigate(isLocalPortfolio ? "scenarios" : "portfolio")
          }
          style={({ pressed }) => [
            styles.portfolioAction,
            pressed && styles.pressed,
          ]}
        >
          <Text style={styles.portfolioActionText}>
            {isLocalPortfolio ? "Explorar sensibilidade" : "Usar minha carteira"}
          </Text>
          <Text accessibilityElementsHidden style={styles.portfolioActionArrow}>
            →
          </Text>
        </Pressable>
      </Surface>

      <SectionHeading
        title="Mercado em uma frase"
        support="Contexto público para interpretar o recorte, sem substituir sua carteira."
      />
      <View style={styles.hero}>
        <Eyebrow inverse>
          {snapshot.mode === "live"
            ? "Leitura com dados públicos"
            : "Fotografia de demonstração"}
        </Eyebrow>
        <Text accessibilityRole="header" style={styles.heroTitle}>
          {snapshot.verdict}
        </Text>
        <Text style={styles.heroSupport}>{snapshot.verdictSupport}</Text>
        <View style={styles.heroDivider} />
        <View style={styles.healthRow}>
          <View style={styles.healthPrimary}>
            <Text style={styles.healthValue}>
              {snapshot.sourcesAvailable}/{snapshot.sourcesTotal}
            </Text>
            <Text style={styles.healthLabel}>fontes com data</Text>
          </View>
          <View style={styles.healthSecondary}>
            <Text style={styles.healthMeta}>Fotografia</Text>
            <Text style={styles.healthDate}>{formatSnapshotDate(snapshot.asOf)}</Text>
          </View>
        </View>
        <Text style={styles.sourceList}>
          Fontes disponíveis: {availableSources || "nenhuma"}
        </Text>
      </View>

      <SnapshotHistoryPanel
        history={snapshotHistory}
        loading={snapshotHistoryLoading}
        message={snapshotHistoryMessage}
      />

      <SectionHeading
        title="Acompanhe o que mudou"
        support="Favoritos aparecem primeiro; cada sinal abre evidência, relação e limite."
      />
      <View style={[styles.signalGrid, isWide && styles.signalGridWide]}>
        {visibleSignals.map((signal) => (
          <View key={signal.id} style={isWide ? styles.signalGridItemWide : undefined}>
            <MarketSignalCard
              favorite={favoriteSignalIds.includes(signal.id)}
              onPress={() => onSelectSignal(signal.id)}
              selected={signal.id === selectedSignalId}
              signal={signal}
            />
          </View>
        ))}
      </View>
      {snapshot.signals.length > 2 ? (
        <Pressable
          accessibilityRole="button"
          onPress={() => setShowAllSignals((current) => !current)}
          style={({ pressed }) => [styles.signalToggle, pressed && styles.pressed]}
        >
          <Text style={styles.signalToggleText}>
            {showAllSignals
              ? "Recolher sinais"
              : `Ver mais ${snapshot.signals.length - 2} sinais`}
          </Text>
        </Pressable>
      ) : null}

      <ExplainableAlertPanel
        alert={explainableAlert}
        favorite={selectedSignalIsFavorite}
        favoriteMessage={favoriteMessage}
        favoriteSaving={favoriteSaving}
        onToggleFavorite={() => onToggleFavorite(selectedSignalId)}
      />

      <SectionHeading
        title="Como isso toca sua carteira"
        support="O filtro cruza a classe de cada posição com o sinal selecionado."
      />
      <View style={styles.filterGrid}>
        {filters.map((filter) => {
          const selected = classFilter === filter;
          return (
            <Pressable
              accessibilityRole="button"
              accessibilityState={{ selected }}
              key={filter}
              onPress={() => onClassFilter(filter)}
              style={({ pressed }) => [
                styles.filterChip,
                selected && styles.filterChipSelected,
                pressed && styles.pressed,
              ]}
            >
              <Text
                numberOfLines={1}
                style={[
                  styles.filterText,
                  selected && styles.filterTextSelected,
                ]}
              >
                {filter}
              </Text>
            </Pressable>
          );
        })}
      </View>

      <View style={styles.impactSummary}>
        <View>
          <Text style={styles.impactValue}>{impacts.length}</Text>
          <Text style={styles.impactLabel}>posições relacionadas</Text>
        </View>
        <View style={styles.impactSummaryRight}>
          <Text style={styles.impactValue}>
            {allocation.toFixed(0)}%
          </Text>
          <Text style={styles.impactLabel}>
            {isLocalPortfolio ? "da carteira local" : "da demonstração"}
          </Text>
        </View>
      </View>

      {impacts.length ? (
        <View style={[styles.impactList, isWide && styles.impactListWide]}>
          {impacts.map((impact) => (
            <View
              key={impact.position.id}
              style={isWide ? styles.impactItemWide : undefined}
            >
              <ImpactCard hideAmount={hideAmounts} impact={impact} />
            </View>
          ))}
        </View>
      ) : (
        <Surface style={styles.emptyState}>
          <Text style={styles.emptyTitle}>
            {selectedSignalHasEffects
              ? "Nenhuma posição neste recorte"
              : "Sem relação direta classificada"}
          </Text>
          <Text style={styles.emptyText}>
            {selectedSignalHasEffects
              ? "Troque o filtro ou selecione outro sinal para continuar explorando."
              : "Este sinal continua útil como contexto de mercado, mas o motor não fornece um elo direto com classes da carteira. Nenhum impacto foi inventado."}
          </Text>
        </Surface>
      )}

      {!isLocalPortfolio ? (
        <Pressable
          accessibilityHint="Abre o simulador de sensibilidade a juros"
          accessibilityRole="button"
          onPress={() => onNavigate("scenarios")}
          style={({ pressed }) => [styles.scenarioCta, pressed && styles.pressed]}
        >
          <View style={styles.ctaCopy}>
            <Text style={styles.ctaEyebrow}>EXPLORE A DEMONSTRAÇÃO</Text>
            <Text style={styles.ctaTitle}>E se as taxas mudarem?</Text>
            <Text style={styles.ctaSupport}>
              Explore choques de −100 a +100 bps sem alterar a carteira.
            </Text>
          </View>
          <Text accessibilityElementsHidden style={styles.ctaArrow}>
            →
          </Text>
        </Pressable>
      ) : null}

      <Text style={styles.guardrail}>
        {snapshot.mode === "live" ? "Mercado vindo de dados públicos; " : "Mercado em demonstração; "}
        {isLocalPortfolio ? "carteira privada somente neste aparelho" : "carteira sintética local"}. As relações mostram sensibilidade, não
        recomendação, promessa ou retorno futuro.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    alignSelf: "center",
    boxSizing: "border-box",
    gap: spacing.lg,
    maxWidth: 820,
    paddingBottom: spacing.xl,
    paddingHorizontal: spacing.md,
    paddingTop: spacing.md,
    width: "100%",
  },
  contentWide: {
    paddingHorizontal: spacing.xl,
  },
  headerRow: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
    justifyContent: "space-between",
  },
  brand: {
    color: colors.text,
    fontSize: 24,
    fontWeight: "900",
    letterSpacing: -0.8,
  },
  brandSupport: {
    color: colors.textMuted,
    fontSize: 9,
    fontWeight: "800",
    letterSpacing: 1.1,
    marginTop: 1,
  },
  hero: {
    backgroundColor: colors.primaryDark,
    borderRadius: radius.lg,
    gap: spacing.sm,
    overflow: "hidden",
    padding: spacing.lg,
  },
  fallbackNotice: {
    backgroundColor: colors.goldSoft,
    borderColor: "#EBCB91",
    gap: spacing.xs,
    ...Platform.select({
      web: { boxShadow: "none" },
      default: { elevation: 0, shadowOpacity: 0 },
    }),
  },
  fallbackText: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  heroTitle: {
    color: colors.white,
    fontSize: 28,
    fontWeight: "800",
    letterSpacing: -0.8,
    lineHeight: 34,
  },
  heroSupport: {
    color: "#D7E9E5",
    fontSize: 15,
    lineHeight: 23,
  },
  heroDivider: {
    backgroundColor: "rgba(255,255,255,0.18)",
    height: 1,
    marginVertical: spacing.xs,
  },
  healthRow: {
    alignItems: "flex-end",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  healthPrimary: {
    alignItems: "baseline",
    flexDirection: "row",
    gap: spacing.xs,
  },
  healthValue: {
    color: colors.white,
    fontSize: 25,
    fontVariant: ["tabular-nums"],
    fontWeight: "800",
  },
  healthLabel: {
    color: "#D7E9E5",
    fontSize: 12,
  },
  healthSecondary: {
    alignItems: "flex-end",
    gap: 2,
  },
  healthMeta: {
    color: "#9FC9C1",
    fontSize: 10,
    fontWeight: "700",
    textTransform: "uppercase",
  },
  healthDate: {
    color: colors.white,
    fontSize: 13,
    fontVariant: ["tabular-nums"],
    fontWeight: "700",
  },
  sourceList: {
    color: "#B8DAD4",
    fontSize: 11,
    lineHeight: 17,
  },
  portfolioPulse: {
    backgroundColor: colors.primarySoft,
    gap: spacing.md,
  },
  portfolioPulseTopline: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  portfolioPulseTitle: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "900",
    letterSpacing: -0.4,
    lineHeight: 26,
  },
  portfolioFacts: {
    backgroundColor: colors.surface,
    borderRadius: radius.sm,
    padding: spacing.sm,
  },
  portfolioFact: {
    alignItems: "center",
    flexDirection: "row",
    gap: spacing.sm,
    justifyContent: "space-between",
    minHeight: 56,
  },
  portfolioFactCopy: {
    flex: 1,
    gap: 2,
  },
  portfolioFactLabel: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.6,
    textTransform: "uppercase",
  },
  portfolioFactValue: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "800",
    lineHeight: 19,
  },
  portfolioFactPercent: {
    color: colors.primaryDark,
    fontSize: 20,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  portfolioFactDivider: {
    backgroundColor: colors.border,
    height: 1,
  },
  portfolioPulseSupport: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  portfolioAction: {
    alignItems: "center",
    alignSelf: "stretch",
    backgroundColor: colors.primary,
    borderRadius: radius.sm,
    flexDirection: "row",
    gap: spacing.xs,
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  portfolioActionText: {
    color: colors.white,
    fontSize: 13,
    fontWeight: "900",
  },
  portfolioActionArrow: {
    color: colors.white,
    fontSize: 18,
  },
  signalGrid: {
    gap: spacing.sm,
  },
  signalGridWide: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  signalGridItemWide: {
    width: "49%",
  },
  signalToggle: {
    alignItems: "center",
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  signalToggleText: {
    color: colors.primary,
    fontSize: 13,
    fontWeight: "800",
  },
  filterGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
  },
  filterChip: {
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.pill,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  filterChipSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  filterText: {
    color: colors.textMuted,
    fontSize: 13,
    fontWeight: "700",
  },
  filterTextSelected: {
    color: colors.white,
  },
  pressed: {
    opacity: 0.72,
  },
  impactSummary: {
    alignItems: "center",
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    flexDirection: "row",
    justifyContent: "space-between",
    padding: spacing.md,
  },
  impactSummaryRight: {
    alignItems: "flex-end",
  },
  impactValue: {
    color: colors.primaryDark,
    fontSize: 24,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  impactLabel: {
    color: colors.textMuted,
    fontSize: 11,
    fontWeight: "700",
  },
  impactList: {
    gap: spacing.sm,
  },
  impactListWide: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  impactItemWide: {
    width: "49%",
  },
  emptyState: {
    gap: spacing.xs,
  },
  emptyTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "800",
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 14,
    lineHeight: 21,
  },
  scenarioCta: {
    alignItems: "center",
    backgroundColor: colors.goldSoft,
    borderColor: "#EBCB91",
    borderRadius: radius.lg,
    borderWidth: 1,
    flexDirection: "row",
    gap: spacing.md,
    justifyContent: "space-between",
    minHeight: 118,
    padding: spacing.lg,
  },
  ctaCopy: {
    flex: 1,
    gap: 4,
  },
  ctaEyebrow: {
    color: colors.gold,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1.2,
  },
  ctaTitle: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "900",
  },
  ctaSupport: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 19,
  },
  ctaArrow: {
    color: colors.gold,
    fontSize: 28,
    fontWeight: "500",
  },
  guardrail: {
    color: colors.textMuted,
    fontSize: 11,
    lineHeight: 17,
    textAlign: "center",
  },
});
