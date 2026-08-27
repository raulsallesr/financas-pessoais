import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from "react-native";

import { ImpactCard } from "../components/ImpactCard";
import { MarketSignalCard } from "../components/MarketSignalCard";
import {
  DemoPill,
  Eyebrow,
  SectionHeading,
  Surface,
} from "../components/Primitives";
import { TabKey } from "../components/BottomNav";
import {
  ALL_CLASSES,
  availableClasses,
  ClassFilter,
  impactedAllocation,
  impactsForSignal,
  signalById,
} from "../domain/insights";
import { MarketSnapshot } from "../domain/types";
import { colors, radius, spacing } from "../theme";

export function TodayScreen({
  snapshot,
  selectedSignalId,
  onSelectSignal,
  classFilter,
  onClassFilter,
  onNavigate,
}: {
  snapshot: MarketSnapshot;
  selectedSignalId: string;
  onSelectSignal: (signalId: string) => void;
  classFilter: ClassFilter;
  onClassFilter: (filter: ClassFilter) => void;
  onNavigate: (tab: TabKey) => void;
}) {
  const { width } = useWindowDimensions();
  const isWide = width >= 720;
  const selectedSignal = signalById(snapshot, selectedSignalId);
  const impacts = impactsForSignal(snapshot, selectedSignalId, classFilter);
  const allocation = impactedAllocation(impacts);
  const filters = [ALL_CLASSES, ...availableClasses(snapshot)] as const;

  return (
    <ScrollView
      contentContainerStyle={[
        styles.content,
        isWide && styles.contentWide,
      ]}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.headerRow}>
        <View>
          <Text style={styles.brand}>FocusLens</Text>
          <Text style={styles.brandSupport}>INTELIGÊNCIA PARA SUA CARTEIRA</Text>
        </View>
        <DemoPill />
      </View>

      <View style={styles.hero}>
        <Eyebrow inverse>Leitura de hoje</Eyebrow>
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
            <Text style={styles.healthDate}>{snapshot.asOf}</Text>
          </View>
        </View>
      </View>

      <SectionHeading
        title="O mercado está dizendo"
        support="Toque em um sinal para revelar onde ele encosta na carteira."
      />
      <ScrollView
        contentContainerStyle={styles.signalRail}
        decelerationRate="fast"
        horizontal
        showsHorizontalScrollIndicator={false}
      >
        {snapshot.signals.map((signal) => (
          <MarketSignalCard
            key={signal.id}
            onPress={() => onSelectSignal(signal.id)}
            selected={signal.id === selectedSignalId}
            signal={signal}
          />
        ))}
      </ScrollView>

      <Surface style={styles.signalDetail}>
        <Eyebrow>Leitura selecionada</Eyebrow>
        <Text style={styles.signalTitle}>{selectedSignal.headline}</Text>
        <Text style={styles.signalExplanation}>
          {selectedSignal.explanation}
        </Text>
        <Text style={styles.signalSource}>
          Evidência: {selectedSignal.source} · {selectedSignal.updatedAt}
        </Text>
      </Surface>

      <SectionHeading
        title="Como isso toca sua carteira"
        support="O filtro cruza a classe de cada posição com o sinal selecionado."
      />
      <ScrollView
        contentContainerStyle={styles.filterRail}
        horizontal
        showsHorizontalScrollIndicator={false}
      >
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
      </ScrollView>

      <View style={styles.impactSummary}>
        <View>
          <Text style={styles.impactValue}>{impacts.length}</Text>
          <Text style={styles.impactLabel}>posições relacionadas</Text>
        </View>
        <View style={styles.impactSummaryRight}>
          <Text style={styles.impactValue}>
            {allocation.toFixed(0)}%
          </Text>
          <Text style={styles.impactLabel}>da carteira demo</Text>
        </View>
      </View>

      {impacts.length ? (
        <View style={[styles.impactList, isWide && styles.impactListWide]}>
          {impacts.map((impact) => (
            <View
              key={impact.position.id}
              style={isWide ? styles.impactItemWide : undefined}
            >
              <ImpactCard impact={impact} />
            </View>
          ))}
        </View>
      ) : (
        <Surface style={styles.emptyState}>
          <Text style={styles.emptyTitle}>Nenhuma posição neste recorte</Text>
          <Text style={styles.emptyText}>
            Troque o filtro ou selecione outro sinal para continuar explorando.
          </Text>
        </Surface>
      )}

      <Pressable
        accessibilityHint="Abre o simulador de sensibilidade a juros"
        accessibilityRole="button"
        onPress={() => onNavigate("scenarios")}
        style={({ pressed }) => [styles.scenarioCta, pressed && styles.pressed]}
      >
        <View style={styles.ctaCopy}>
          <Text style={styles.ctaEyebrow}>EXPERIMENTE</Text>
          <Text style={styles.ctaTitle}>E se as taxas mudarem?</Text>
          <Text style={styles.ctaSupport}>
            Explore choques de −100 a +100 bps sem alterar sua carteira.
          </Text>
        </View>
        <Text accessibilityElementsHidden style={styles.ctaArrow}>
          →
        </Text>
      </Pressable>

      <Text style={styles.guardrail}>
        Demonstração educacional com carteira sintética. As relações mostram
        sensibilidade, não recomendação, promessa ou retorno futuro.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    alignSelf: "center",
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
  signalRail: {
    gap: spacing.sm,
    paddingRight: spacing.md,
  },
  signalDetail: {
    gap: spacing.xs,
  },
  signalTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "800",
    lineHeight: 24,
  },
  signalExplanation: {
    color: colors.textMuted,
    fontSize: 14,
    lineHeight: 22,
  },
  signalSource: {
    color: colors.primary,
    fontSize: 11,
    fontWeight: "700",
    marginTop: spacing.xxs,
  },
  filterRail: {
    gap: spacing.xs,
    paddingRight: spacing.md,
  },
  filterChip: {
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.pill,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 46,
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
