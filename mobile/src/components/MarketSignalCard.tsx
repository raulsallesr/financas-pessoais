import { Pressable, StyleSheet, Text, View } from "react-native";

import { MarketSignal } from "../domain/types";
import { colors, radius, spacing } from "../theme";
import { formatSnapshotDate, ToneBadge } from "./Primitives";

export function MarketSignalCard({
  signal,
  selected,
  favorite,
  onPress,
}: {
  signal: MarketSignal;
  selected: boolean;
  favorite: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable
      accessibilityHint="Abre a evidência e as relações disponíveis para este sinal"
      accessibilityLabel={`${signal.label}: ${signal.value}. ${signal.headline}${favorite ? ". Favorito" : ""}`}
      accessibilityRole="button"
      accessibilityState={{ selected }}
      onPress={onPress}
      style={({ pressed }) => [
        styles.card,
        selected && styles.cardSelected,
        pressed && styles.cardPressed,
      ]}
    >
      <View style={styles.topline}>
        <Text style={styles.label}>
          {signal.label}{favorite ? " · FAVORITO" : ""}
        </Text>
        <ToneBadge
          tone={signal.tone}
          label={signal.tone === "attention" ? "atenção" : "leitura"}
        />
      </View>
      <Text style={styles.value}>{signal.value}</Text>
      <Text style={styles.change}>{signal.change}</Text>
      <Text style={styles.headline}>
        {signal.headline}
      </Text>
      <Text style={styles.source}>
        {signal.source} · {formatSnapshotDate(signal.updatedAt)}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.xxs,
    minHeight: 158,
    padding: spacing.md,
  },
  cardSelected: {
    backgroundColor: "#F7FBFA",
    borderColor: colors.primary,
    borderWidth: 2,
  },
  cardPressed: {
    opacity: 0.82,
  },
  topline: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
    minHeight: 30,
  },
  label: {
    color: colors.textMuted,
    flex: 1,
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 17,
    paddingRight: spacing.xs,
  },
  value: {
    color: colors.text,
    fontSize: 25,
    fontVariant: ["tabular-nums"],
    fontWeight: "800",
    letterSpacing: -0.8,
    marginTop: spacing.xxs,
  },
  change: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: "700",
  },
  headline: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "700",
    lineHeight: 19,
    marginTop: spacing.xs,
  },
  source: {
    color: colors.textMuted,
    fontSize: 11,
    lineHeight: 16,
    marginTop: "auto",
  },
});
