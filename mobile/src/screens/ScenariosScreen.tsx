import { useState } from "react";
import {
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { ContributionSimulatorPanel } from "../components/ContributionSimulatorPanel";
import { ImpactCard } from "../components/ImpactCard";
import {
  AmountVisibilityButton,
  Eyebrow,
  PortfolioModePill,
  PortfolioPresentationMode,
  SectionHeading,
  Surface,
} from "../components/Primitives";
import {
  buildRateScenario,
  summarizeScenarioAllocation,
  toneLabel,
} from "../domain/insights";
import { MarketSnapshot } from "../domain/types";
import { colors, radius, spacing } from "../theme";

const shocks = [-100, -50, 0, 50, 100] as const;

function formatShock(value: number): string {
  if (value === 0) {
    return "0";
  }
  return `${value > 0 ? "+" : "−"}${Math.abs(value)}`;
}

function formatShockChoice(value: number): string {
  if (value === 0) {
    return "Atual";
  }
  const points = (Math.abs(value) / 100).toFixed(value % 100 === 0 ? 0 : 1);
  return `${value > 0 ? "+" : "−"}${points.replace(".", ",")} p.p.`;
}

function formatPercent(value: number): string {
  return `${value.toFixed(1).replace(".", ",")}%`;
}

export function ScenariosScreen({
  snapshot,
  shockBps,
  onShockChange,
  portfolioMode,
  hideAmounts,
  onToggleAmounts,
}: {
  snapshot: MarketSnapshot;
  shockBps: number;
  onShockChange: (value: number) => void;
  portfolioMode: PortfolioPresentationMode;
  hideAmounts: boolean;
  onToggleAmounts: () => void;
}) {
  const [showAllImpacts, setShowAllImpacts] = useState(false);
  const scenario = buildRateScenario(snapshot, shockBps);
  const summary = summarizeScenarioAllocation(snapshot, scenario.impacts);
  const visibleImpacts = showAllImpacts
    ? scenario.impacts
    : scenario.impacts.slice(0, 4);

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.headerRow}>
        <View style={styles.headerCopy}>
          <Eyebrow>Cenários</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>
            Teste hipóteses sem mexer na carteira
          </Text>
        </View>
        <PortfolioModePill mode={portfolioMode} />
      </View>

      <ContributionSimulatorPanel
        hideAmounts={hideAmounts}
        snapshot={snapshot}
      />

      <SectionHeading
        title="E se os juros mudarem?"
        support="Explore a sensibilidade educacional das posições ao nível das taxas."
      />

      <View style={styles.scenarioHero}>
        <Eyebrow inverse>Cenário educacional</Eyebrow>
        <View style={styles.scenarioValueRow}>
          <Text style={styles.scenarioValue}>{formatShock(shockBps)}</Text>
          <Text style={styles.scenarioUnit}>bps</Text>
        </View>
        <Text style={styles.scenarioTitle}>{scenario.title}</Text>
        <Text style={styles.scenarioSupport}>{scenario.explanation}</Text>
      </View>

      <Surface style={styles.controlCard}>
        <Text style={styles.controlLabel}>ESCOLHA UMA HIPÓTESE</Text>
        <View style={styles.controlTrack}>
          <View style={styles.trackLine} />
          {shocks.map((value) => {
            const selected = value === shockBps;
            return (
              <Pressable
                accessibilityLabel={`Aplicar choque de ${formatShock(value)} pontos-base`}
                accessibilityRole="button"
                accessibilityState={{ selected }}
                key={value}
                onPress={() => onShockChange(value)}
                style={({ pressed }) => [
                  styles.shockButton,
                  selected && styles.shockButtonSelected,
                  pressed && styles.pressed,
                ]}
              >
                <View style={[styles.shockDot, selected && styles.shockDotSelected]} />
                <Text style={[styles.shockText, selected && styles.shockTextSelected]}>
                  {formatShockChoice(value)}
                </Text>
              </Pressable>
            );
          })}
        </View>
        <Text style={styles.controlHint}>
          1 p.p. equivale a 100 bps. A régua não estima probabilidade ou retorno.
        </Text>
      </Surface>

      {shockBps !== 0 ? (
        <Surface style={styles.summaryCard}>
          <Eyebrow>Leitura rápida</Eyebrow>
          <Text style={styles.summaryTitle}>
            {summary.byTone
              .map(
                (item) =>
                  `${formatPercent(item.allocationPercent)} ${toneLabel(item.tone).toLocaleLowerCase("pt-BR")}`,
              )
              .join(" · ") || "Sem sensibilidade classificada"}
          </Text>
          <Text style={styles.summarySupport}>
            {formatPercent(summary.coveredAllocationPercent)} da carteira possui
            uma relação educacional mapeada para este choque.
          </Text>
          <View style={styles.summaryRows}>
            {summary.byTone.map((item) => (
              <View key={item.tone} style={styles.summaryRow}>
                <View style={styles.summaryCopy}>
                  <Text style={styles.summaryRowTitle}>{toneLabel(item.tone)}</Text>
                  <Text style={styles.summaryRowMeta}>
                    {item.positionCount} {item.positionCount === 1 ? "posição" : "posições"}
                  </Text>
                </View>
                <Text style={styles.summaryPercent}>
                  {formatPercent(item.allocationPercent)}
                </Text>
              </View>
            ))}
          </View>
          {summary.uncoveredAllocationPercent > 0 ? (
            <Text style={styles.uncoveredText}>
              {formatPercent(summary.uncoveredAllocationPercent)} fica sem relação
              classificada neste cenário; o app não preenche essa lacuna por
              aproximação.
            </Text>
          ) : null}
        </Surface>
      ) : null}

      <View style={styles.positionHeading}>
        <View style={styles.positionHeadingCopy}>
          <SectionHeading
            title="Posição por posição"
            support="Abra o detalhe sem expor valores quando estiver em público."
          />
        </View>
        <AmountVisibilityButton
          hidden={hideAmounts}
          onPress={onToggleAmounts}
        />
      </View>
      {scenario.impacts.length ? (
        <View style={styles.impactList}>
          {visibleImpacts.map((impact) => (
            <ImpactCard
              hideAmount={hideAmounts}
              impact={impact}
              key={impact.position.id}
            />
          ))}
          {scenario.impacts.length > 4 ? (
            <Pressable
              accessibilityRole="button"
              onPress={() => setShowAllImpacts((current) => !current)}
              style={({ pressed }) => [
                styles.impactToggle,
                pressed && styles.pressed,
              ]}
            >
              <Text style={styles.impactToggleText}>
                {showAllImpacts
                  ? "Recolher posições"
                  : `Ver todas as ${scenario.impacts.length} posições`}
              </Text>
            </Pressable>
          ) : null}
        </View>
      ) : (
        <Surface style={styles.neutralCard}>
          <Text style={styles.neutralTitle}>Sem choque aplicado</Text>
          <Text style={styles.neutralSupport}>
            A fotografia observada continua como referência. Escolha outro ponto
            da régua para comparar sensibilidades.
          </Text>
        </Surface>
      )}

      <View style={styles.guardrailCard}>
        <View style={styles.guardrailMark}>
          <View style={styles.guardrailLine} />
          <View style={styles.guardrailLine} />
          <View style={styles.guardrailLine} />
        </View>
        <View style={styles.guardrailCopy}>
          <Text style={styles.guardrailTitle}>O simulador não decide por você</Text>
          <Text style={styles.guardrailText}>
            Ele organiza relações conhecidas. Prazo, tributação, crédito, liquidez,
            taxa contratada e objetivo pessoal continuam fora desta conta.
          </Text>
        </View>
      </View>
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
  headerRow: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  headerCopy: { flex: 1, gap: spacing.xxs, minWidth: 220 },
  title: {
    color: colors.text,
    fontSize: 31,
    fontWeight: "900",
    letterSpacing: -1,
  },
  scenarioHero: {
    backgroundColor: colors.primaryDark,
    borderRadius: radius.lg,
    gap: spacing.xs,
    padding: spacing.lg,
  },
  scenarioValueRow: {
    alignItems: "baseline",
    flexDirection: "row",
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  scenarioValue: {
    color: colors.white,
    fontSize: 48,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
    letterSpacing: -2,
  },
  scenarioUnit: {
    color: "#A9D2CA",
    fontSize: 16,
    fontWeight: "700",
  },
  scenarioTitle: {
    color: colors.white,
    fontSize: 20,
    fontWeight: "800",
    lineHeight: 27,
  },
  scenarioSupport: {
    color: "#C9E8E2",
    fontSize: 13,
    lineHeight: 20,
  },
  controlCard: { gap: spacing.md },
  controlLabel: {
    color: colors.gold,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1.3,
  },
  controlTrack: {
    flexDirection: "row",
    justifyContent: "space-between",
    minHeight: 64,
    position: "relative",
  },
  trackLine: {
    backgroundColor: colors.border,
    height: 3,
    left: 22,
    position: "absolute",
    right: 22,
    top: 19,
  },
  shockButton: {
    alignItems: "center",
    borderRadius: radius.sm,
    flex: 1,
    gap: spacing.xs,
    justifyContent: "flex-start",
    minHeight: 56,
    minWidth: 0,
    paddingTop: 11,
    zIndex: 1,
  },
  shockButtonSelected: { backgroundColor: colors.primarySoft },
  shockDot: {
    backgroundColor: colors.surface,
    borderColor: colors.textMuted,
    borderRadius: radius.pill,
    borderWidth: 2,
    height: 18,
    width: 18,
  },
  shockDotSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
    borderWidth: 5,
  },
  shockText: {
    color: colors.textMuted,
    fontSize: 10,
    fontVariant: ["tabular-nums"],
    fontWeight: "700",
  },
  shockTextSelected: { color: colors.primaryDark },
  controlHint: {
    color: colors.textMuted,
    fontSize: 11,
    lineHeight: 17,
  },
  summaryCard: {
    gap: spacing.md,
    ...Platform.select({
      web: { boxShadow: "none" },
      default: { elevation: 0, shadowOpacity: 0 },
    }),
  },
  summaryTitle: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "900",
    letterSpacing: -0.3,
    lineHeight: 27,
  },
  summarySupport: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  summaryRows: { gap: spacing.xs },
  summaryRow: {
    alignItems: "center",
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    flexDirection: "row",
    gap: spacing.sm,
    justifyContent: "space-between",
    minHeight: 62,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  summaryCopy: { flex: 1, gap: 2 },
  summaryRowTitle: { color: colors.text, fontSize: 13, fontWeight: "800" },
  summaryRowMeta: { color: colors.textMuted, fontSize: 11 },
  summaryPercent: {
    color: colors.primaryDark,
    fontSize: 18,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  uncoveredText: {
    color: colors.textMuted,
    fontSize: 12,
    lineHeight: 19,
  },
  positionHeading: {
    alignItems: "flex-start",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
    justifyContent: "space-between",
  },
  positionHeadingCopy: { flex: 1, minWidth: 220 },
  impactList: { gap: spacing.sm },
  impactToggle: {
    alignItems: "center",
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  impactToggleText: {
    color: colors.primary,
    fontSize: 13,
    fontWeight: "800",
  },
  neutralCard: { gap: spacing.xs },
  neutralTitle: { color: colors.text, fontSize: 16, fontWeight: "900" },
  neutralSupport: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  guardrailCard: {
    backgroundColor: colors.goldSoft,
    borderColor: "#EBCB91",
    borderRadius: radius.md,
    borderWidth: 1,
    flexDirection: "row",
    gap: spacing.md,
    padding: spacing.md,
  },
  guardrailMark: {
    alignItems: "center",
    borderColor: colors.gold,
    borderRadius: 9,
    borderWidth: 2,
    gap: 4,
    height: 42,
    justifyContent: "center",
    width: 36,
  },
  guardrailLine: {
    backgroundColor: colors.gold,
    borderRadius: 2,
    height: 2,
    width: 17,
  },
  guardrailCopy: { flex: 1, gap: 4 },
  guardrailTitle: { color: colors.text, fontSize: 15, fontWeight: "900" },
  guardrailText: { color: colors.textMuted, fontSize: 12, lineHeight: 19 },
  pressed: { opacity: 0.65 },
});
