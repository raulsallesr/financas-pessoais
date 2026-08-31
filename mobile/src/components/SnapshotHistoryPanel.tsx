import { StyleSheet, Text, View } from "react-native";

import {
  comparePublicSnapshots,
  PublicSnapshotHistoryV1,
} from "../domain/snapshotHistory";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, formatSnapshotDate, Surface } from "./Primitives";

export function SnapshotHistoryPanel({
  history,
  loading,
  message,
}: {
  history: PublicSnapshotHistoryV1 | null;
  loading: boolean;
  message?: string;
}) {
  const current = history?.snapshots[0] ?? null;
  const previous = history?.snapshots[1] ?? null;
  const comparison = current ? comparePublicSnapshots(current, previous) : null;
  const materialChangeCount = comparison
    ? comparison.signalChanges.length + (comparison.verdictChanged ? 1 : 0)
    : 0;
  const visibleChanges = comparison?.signalChanges.slice(0, 3) ?? [];

  return (
    <Surface style={styles.panel}>
      <View style={styles.topline}>
        <View style={styles.titleCopy}>
          <Eyebrow>Linha do tempo local</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>
            {loading
              ? "Preparando sua primeira fotografia"
              : !current
                ? "Histórico ainda indisponível"
                : !previous
                  ? "Primeira fotografia salva"
                  : materialChangeCount
                    ? `${materialChangeCount} ${materialChangeCount === 1 ? "mudança encontrada" : "mudanças encontradas"}`
                    : "Sem mudança literal nos sinais"}
          </Text>
        </View>
        {history ? (
          <View
            accessibilityLabel={`${history.snapshots.length} fotografias públicas salvas`}
            style={styles.countPill}
          >
            <Text style={styles.countText}>{history.snapshots.length}/8</Text>
          </View>
        ) : null}
      </View>

      {loading ? (
        <Text style={styles.support}>
          A fotografia pública será registrada sem carteira, posição ou valor.
        </Text>
      ) : current ? (
        <>
          <View style={styles.dateRow}>
            <View style={styles.dateItem}>
              <Text style={styles.dateLabel}>Atual</Text>
              <Text style={styles.dateValue}>{formatSnapshotDate(current.asOf)}</Text>
            </View>
            <View accessibilityElementsHidden style={styles.timelineRule} />
            <View style={[styles.dateItem, styles.dateItemRight]}>
              <Text style={styles.dateLabel}>Anterior</Text>
              <Text style={styles.dateValue}>
                {previous ? formatSnapshotDate(previous.asOf) : "aguardando"}
              </Text>
            </View>
          </View>

          {!previous ? (
            <Text style={styles.support}>
              Quando uma nova fotografia pública chegar, o FocusLens mostrará a
              comparação exata aqui.
            </Text>
          ) : (
            <View style={styles.changeList}>
              {comparison?.verdictChanged ? (
                <View style={styles.changeRow}>
                  <Text style={styles.changeLabel}>Leitura principal</Text>
                  <Text style={styles.changeValue}>{current.verdict}</Text>
                </View>
              ) : null}
              {visibleChanges.map((change) => (
                <View key={change.id} style={styles.changeRow}>
                  <Text style={styles.changeLabel}>{change.label}</Text>
                  <Text style={styles.changeValue}>
                    {change.kind === "added"
                      ? `Novo: ${change.currentValue}`
                      : change.kind === "removed"
                        ? `Saiu da fotografia: ${change.previousValue}`
                        : `${change.previousValue} → ${change.currentValue}`}
                  </Text>
                </View>
              ))}
              {materialChangeCount === 0 ? (
                <Text style={styles.support}>
                  Veredito, valores e sinais mantiveram o mesmo conteúdo entre as
                  duas fotografias.
                </Text>
              ) : null}
              {comparison && comparison.signalChanges.length > visibleChanges.length ? (
                <Text style={styles.moreText}>
                  +{comparison.signalChanges.length - visibleChanges.length} mudanças
                  preservadas no histórico
                </Text>
              ) : null}
            </View>
          )}
        </>
      ) : (
        <Text style={styles.support}>
          {message ?? "Nenhuma fotografia pública compatível foi salva."}
        </Text>
      )}

      <Text style={styles.privacyNote}>
        Somente dados públicos ficam nesta linha do tempo. A carteira nunca entra
        neste arquivo.
      </Text>
    </Surface>
  );
}

const styles = StyleSheet.create({
  panel: {
    backgroundColor: colors.surfaceMuted,
    gap: spacing.md,
  },
  topline: {
    alignItems: "flex-start",
    flexDirection: "row",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  titleCopy: {
    flex: 1,
    gap: spacing.xxs,
  },
  title: {
    color: colors.text,
    fontSize: 19,
    fontWeight: "900",
    letterSpacing: -0.3,
    lineHeight: 25,
  },
  countPill: {
    alignItems: "center",
    backgroundColor: colors.primarySoft,
    borderRadius: radius.pill,
    justifyContent: "center",
    minHeight: 36,
    minWidth: 50,
    paddingHorizontal: spacing.sm,
  },
  countText: {
    color: colors.primaryDark,
    fontSize: 12,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  support: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  dateRow: {
    alignItems: "center",
    flexDirection: "row",
    gap: spacing.sm,
  },
  dateItem: {
    gap: 2,
  },
  dateItemRight: {
    alignItems: "flex-end",
  },
  dateLabel: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.7,
    textTransform: "uppercase",
  },
  dateValue: {
    color: colors.text,
    fontSize: 13,
    fontVariant: ["tabular-nums"],
    fontWeight: "800",
  },
  timelineRule: {
    backgroundColor: colors.primary,
    flex: 1,
    height: 2,
    minWidth: spacing.xl,
  },
  changeList: {
    gap: spacing.xs,
  },
  changeRow: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    gap: 3,
    padding: spacing.sm,
  },
  changeLabel: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.5,
    textTransform: "uppercase",
  },
  changeValue: {
    color: colors.text,
    fontSize: 13,
    fontWeight: "800",
    lineHeight: 19,
  },
  moreText: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: "800",
  },
  privacyNote: {
    color: colors.textMuted,
    fontSize: 11,
    lineHeight: 17,
  },
});
