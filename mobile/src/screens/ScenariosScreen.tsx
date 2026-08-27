import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { ImpactCard } from "../components/ImpactCard";
import {
  DemoPill,
  Eyebrow,
  SectionHeading,
  Surface,
} from "../components/Primitives";
import { buildRateScenario, impactedAllocation } from "../domain/insights";
import { MarketSnapshot } from "../domain/types";
import { colors, radius, spacing } from "../theme";

const shocks = [-100, -50, 0, 50, 100] as const;

function formatShock(value: number): string {
  if (value === 0) {
    return "0";
  }
  return `${value > 0 ? "+" : "−"}${Math.abs(value)}`;
}

export function ScenariosScreen({
  snapshot,
  shockBps,
  onShockChange,
}: {
  snapshot: MarketSnapshot;
  shockBps: number;
  onShockChange: (value: number) => void;
}) {
  const scenario = buildRateScenario(snapshot, shockBps);
  const allocation = impactedAllocation(scenario.impacts);

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.headerRow}>
        <View style={styles.headerCopy}>
          <Eyebrow>Laboratório</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>
            Cenários
          </Text>
        </View>
        <DemoPill />
      </View>

      <View style={styles.scenarioHero}>
        <Eyebrow inverse>Choque paralelo da curva</Eyebrow>
        <View style={styles.scenarioValueRow}>
          <Text style={styles.scenarioValue}>{formatShock(shockBps)}</Text>
          <Text style={styles.scenarioUnit}>bps</Text>
        </View>
        <Text style={styles.scenarioTitle}>{scenario.title}</Text>
        <Text style={styles.scenarioSupport}>{scenario.explanation}</Text>
      </View>

      <Surface style={styles.controlCard}>
        <Text style={styles.controlLabel}>MOVA A HIPÓTESE</Text>
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
                  {formatShock(value)}
                </Text>
              </Pressable>
            );
          })}
        </View>
        <Text style={styles.controlHint}>
          Taxas simuladas mantêm a inclinação; isto não estima probabilidade.
        </Text>
      </Surface>

      <View style={styles.statsRow}>
        <Surface style={styles.statCard}>
          <Text style={styles.statValue}>{scenario.impacts.length}</Text>
          <Text style={styles.statLabel}>posições sensíveis</Text>
        </Surface>
        <Surface style={styles.statCard}>
          <Text style={styles.statValue}>{allocation.toFixed(0)}%</Text>
          <Text style={styles.statLabel}>da carteira demo</Text>
        </Surface>
      </View>

      <SectionHeading
        title="O que mudaria na leitura"
        support="Cada cartão separa direção provável de certeza inexistente."
      />
      {scenario.impacts.length ? (
        <View style={styles.impactList}>
          {scenario.impacts.map((impact) => (
            <ImpactCard impact={impact} key={impact.position.id} />
          ))}
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
    justifyContent: "space-between",
  },
  headerCopy: { gap: spacing.xxs },
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
    gap: spacing.xs,
    justifyContent: "flex-start",
    minHeight: 56,
    minWidth: 48,
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
    fontSize: 11,
    fontVariant: ["tabular-nums"],
    fontWeight: "700",
  },
  shockTextSelected: { color: colors.primaryDark },
  controlHint: {
    color: colors.textMuted,
    fontSize: 11,
    lineHeight: 17,
  },
  statsRow: { flexDirection: "row", gap: spacing.sm },
  statCard: { flex: 1, gap: 2, shadowOpacity: 0 },
  statValue: {
    color: colors.primaryDark,
    fontSize: 25,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  statLabel: {
    color: colors.textMuted,
    fontSize: 11,
    fontWeight: "700",
  },
  impactList: { gap: spacing.sm },
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
