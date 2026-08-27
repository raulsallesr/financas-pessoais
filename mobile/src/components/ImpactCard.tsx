import { StyleSheet, Text, View } from "react-native";

import { PortfolioImpact } from "../domain/types";
import { colors, radius, spacing } from "../theme";
import { formatCurrency, ToneBadge } from "./Primitives";

export function ImpactCard({
  impact,
  hideAmount = false,
}: {
  impact: PortfolioImpact;
  hideAmount?: boolean;
}) {
  return (
    <View
      accessible
      accessibilityLabel={`${impact.position.name}, ${impact.allocationPercent.toFixed(
        1,
      )}% da carteira. ${impact.effect.headline}. ${impact.effect.explanation}`}
      style={styles.card}
    >
      <View style={styles.topline}>
        <View style={styles.titleBlock}>
          <Text style={styles.title}>{impact.position.shortName}</Text>
          <Text style={styles.assetClass}>{impact.position.assetClass}</Text>
        </View>
        <View style={styles.valueBlock}>
          <Text style={styles.amount}>
            {formatCurrency(impact.position.amount, hideAmount)}
          </Text>
          <Text style={styles.allocation}>
            {impact.allocationPercent.toFixed(1).replace(".", ",")}%
          </Text>
        </View>
      </View>
      <ToneBadge tone={impact.effect.tone} label={impact.effect.headline} />
      <Text style={styles.explanation}>{impact.effect.explanation}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.sm,
    padding: spacing.md,
  },
  topline: {
    alignItems: "flex-start",
    flexDirection: "row",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  titleBlock: {
    flex: 1,
    gap: 3,
  },
  title: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "800",
  },
  assetClass: {
    color: colors.textMuted,
    fontSize: 12,
    lineHeight: 17,
  },
  valueBlock: {
    alignItems: "flex-end",
  },
  amount: {
    color: colors.text,
    fontSize: 14,
    fontVariant: ["tabular-nums"],
    fontWeight: "700",
  },
  allocation: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: "700",
  },
  explanation: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
});
