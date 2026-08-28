import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, View } from "react-native";

import { B3ImportError, B3ImportResult } from "../domain/b3Import";
import { Position } from "../domain/types";
import { pickAndParseB3Document } from "../storage/b3DocumentPicker";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, formatCurrency, Surface } from "./Primitives";

type B3ImportPanelProps = {
  existingCount: number;
  mode: "demo" | "local";
  onReplacePositions: (positions: readonly Position[]) => Promise<void>;
};

type Selection = {
  fileName: string;
  result: B3ImportResult;
};

function importErrorMessage(error: unknown): string {
  if (error instanceof B3ImportError) {
    return error.message;
  }
  return "Não foi possível preparar a importação. A carteira atual foi preservada.";
}

export function B3ImportPanel({
  existingCount,
  mode,
  onReplacePositions,
}: B3ImportPanelProps) {
  const [selection, setSelection] = useState<Selection | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [busy, setBusy] = useState<"reading" | "saving" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  async function chooseDocument() {
    if (busy) {
      return;
    }
    setBusy("reading");
    setError(null);
    setFeedback(null);
    try {
      const picked = await pickAndParseB3Document();
      if (picked.kind === "selected") {
        setSelection({ fileName: picked.fileName, result: picked.result });
        setShowAll(false);
      }
    } catch (caught) {
      setError(importErrorMessage(caught));
    } finally {
      setBusy(null);
    }
  }

  async function replacePortfolio() {
    if (!selection || busy) {
      return;
    }
    setBusy("saving");
    setError(null);
    setFeedback(null);
    try {
      await onReplacePositions(selection.result.positions);
      setFeedback(
        `${selection.result.positions.length} ${selection.result.positions.length === 1 ? "posição foi importada" : "posições foram importadas"} para o cofre local.`,
      );
      setSelection(null);
      setShowAll(false);
    } catch {
      setError(
        "Não foi possível gravar a importação no cofre. A carteira anterior foi preservada.",
      );
    } finally {
      setBusy(null);
    }
  }

  function confirmReplacement() {
    if (!selection || busy) {
      return;
    }
    const currentCopy =
      mode === "demo"
        ? "A demonstração fictícia sairá de cena."
        : `As ${existingCount} ${existingCount === 1 ? "posição atual" : "posições atuais"} serão substituídas.`;
    Alert.alert(
      "Substituir carteira local?",
      `${currentCopy} A prévia com ${selection.result.positions.length} ${selection.result.positions.length === 1 ? "posição" : "posições"} será gravada somente neste aparelho.`,
      [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Substituir",
          onPress: () => void replacePortfolio(),
        },
      ],
    );
  }

  const previewPositions = selection
    ? showAll
      ? selection.result.positions
      : selection.result.positions.slice(0, 5)
    : [];

  return (
    <Surface style={styles.panel}>
      <View style={styles.headingRow}>
        <View style={styles.headingCopy}>
          <Eyebrow>Entrada local</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>
            Importar posição da B3
          </Text>
        </View>
        <View accessibilityLabel="Processamento somente no aparelho" style={styles.localPill}>
          <View style={styles.localDot} />
          <Text style={styles.localPillText}>LOCAL</Text>
        </View>
      </View>

      <Text style={styles.support}>
        Escolha o XLSX da Área do Investidor. O app lê apenas ativo, classe e valor, apaga a cópia temporária e pede sua confirmação antes de trocar a carteira.
      </Text>

      <View style={styles.privacyStrip}>
        <Text style={styles.privacyText}>
          Sem upload · sem CPF ou conta · original não é alterado
        </Text>
      </View>

      <Pressable
        accessibilityHint="Abre o seletor de documentos do aparelho"
        accessibilityLabel={selection ? "Escolher outra planilha B3" : "Escolher planilha B3"}
        accessibilityRole="button"
        accessibilityState={{ busy: busy === "reading", disabled: busy !== null }}
        disabled={busy !== null}
        onPress={() => void chooseDocument()}
        style={({ pressed }) => [
          styles.secondaryButton,
          pressed && styles.pressed,
          busy && styles.disabled,
        ]}
      >
        <Text style={styles.secondaryButtonText}>
          {busy === "reading"
            ? "Lendo e sanitizando…"
            : selection
              ? "Escolher outra planilha"
              : "Escolher planilha XLSX"}
        </Text>
      </Pressable>

      {error ? (
        <Text accessibilityLiveRegion="assertive" style={styles.errorText}>
          {error}
        </Text>
      ) : null}
      {feedback ? (
        <Text accessibilityLiveRegion="polite" style={styles.feedbackText}>
          {feedback}
        </Text>
      ) : null}

      {selection ? (
        <View style={styles.preview}>
          <View style={styles.previewHeading}>
            <View style={styles.previewHeadingCopy}>
              <Eyebrow>Prévia — nada salvo ainda</Eyebrow>
              <Text style={styles.fileName}>
                {selection.fileName}
              </Text>
            </View>
            <View style={styles.readyPill}>
              <Text style={styles.readyPillText}>REVISAR</Text>
            </View>
          </View>

          <View style={styles.metrics}>
            <View style={styles.metric}>
              <Text style={styles.metricValue}>{selection.result.positions.length}</Text>
              <Text style={styles.metricLabel}>posições</Text>
            </View>
            <View style={styles.metric}>
              <Text style={styles.metricValue}>
                {formatCurrency(selection.result.totalAmount, false)}
              </Text>
              <Text style={styles.metricLabel}>total identificado</Text>
            </View>
          </View>

          <Text style={styles.sheetSupport}>
            Abas lidas: {selection.result.sheetsRead.join(" · ")}
          </Text>

          {selection.result.unsupportedRows > 0 ? (
            <Text accessibilityLiveRegion="polite" style={styles.warningText}>
              {selection.result.unsupportedRows} {selection.result.unsupportedRows === 1 ? "linha ficou" : "linhas ficaram"} fora da importação por usar classe ainda não coberta, como cripto ou ouro.
            </Text>
          ) : null}
          {selection.result.ignoredRows > 0 ? (
            <Text style={styles.ignoredText}>
              {selection.result.ignoredRows} {selection.result.ignoredRows === 1 ? "linha sem posição válida foi ignorada" : "linhas sem posição válida foram ignoradas"}, incluindo subtotais.
            </Text>
          ) : null}

          <View style={styles.positionList}>
            {previewPositions.map((position) => (
              <View key={position.id} style={styles.positionRow}>
                <View style={styles.positionCopy}>
                  <Text style={styles.positionName}>{position.shortName}</Text>
                  <Text style={styles.positionClass}>{position.assetClass}</Text>
                </View>
                <Text style={styles.positionAmount}>
                  {formatCurrency(position.amount, false)}
                </Text>
              </View>
            ))}
          </View>

          {selection.result.positions.length > 5 ? (
            <Pressable
              accessibilityRole="button"
              accessibilityState={{ expanded: showAll }}
              disabled={busy !== null}
              onPress={() => setShowAll((current) => !current)}
              style={({ pressed }) => [styles.linkButton, pressed && styles.pressed]}
            >
              <Text style={styles.linkButtonText}>
                {showAll
                  ? "Recolher posições"
                  : `Ver todas as ${selection.result.positions.length} posições`}
              </Text>
            </Pressable>
          ) : null}

          <View style={styles.actions}>
            <Pressable
              accessibilityRole="button"
              accessibilityState={{ busy: busy === "saving", disabled: busy !== null }}
              disabled={busy !== null}
              onPress={confirmReplacement}
              style={({ pressed }) => [
                styles.primaryButton,
                pressed && styles.primaryButtonPressed,
                busy && styles.disabled,
              ]}
            >
              <Text style={styles.primaryButtonText}>
                {busy === "saving"
                  ? "Gravando no cofre…"
                  : `Substituir por ${selection.result.positions.length} ${selection.result.positions.length === 1 ? "posição" : "posições"}`}
              </Text>
            </Pressable>
            <Pressable
              accessibilityRole="button"
              disabled={busy !== null}
              onPress={() => {
                setSelection(null);
                setShowAll(false);
                setError(null);
              }}
              style={({ pressed }) => [styles.cancelButton, pressed && styles.pressed]}
            >
              <Text style={styles.cancelButtonText}>Descartar prévia</Text>
            </Pressable>
          </View>
        </View>
      ) : null}
    </Surface>
  );
}

const styles = StyleSheet.create({
  panel: { gap: spacing.md },
  headingRow: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  headingCopy: { flex: 1, gap: spacing.xxs, minWidth: 210 },
  title: { color: colors.text, fontSize: 20, fontWeight: "900" },
  support: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  localPill: {
    alignItems: "center",
    backgroundColor: colors.primarySoft,
    borderRadius: radius.pill,
    flexDirection: "row",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  localDot: {
    backgroundColor: colors.primary,
    borderRadius: radius.pill,
    height: 6,
    width: 6,
  },
  localPillText: {
    color: colors.primaryDark,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.7,
  },
  privacyStrip: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  privacyText: {
    color: colors.primaryDark,
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 18,
  },
  secondaryButton: {
    alignItems: "center",
    borderColor: colors.primary,
    borderRadius: radius.md,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 52,
    paddingHorizontal: spacing.md,
  },
  secondaryButtonText: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: "800",
    textAlign: "center",
  },
  errorText: {
    backgroundColor: colors.dangerSoft,
    borderRadius: radius.sm,
    color: colors.danger,
    fontSize: 13,
    fontWeight: "700",
    lineHeight: 20,
    padding: spacing.sm,
  },
  feedbackText: {
    backgroundColor: colors.positiveSoft,
    borderRadius: radius.sm,
    color: colors.primaryDark,
    fontSize: 13,
    fontWeight: "700",
    lineHeight: 20,
    padding: spacing.sm,
  },
  preview: {
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.md,
    padding: spacing.md,
  },
  previewHeading: {
    alignItems: "flex-start",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  previewHeadingCopy: { flex: 1, gap: spacing.xxs, minWidth: 190 },
  fileName: { color: colors.text, fontSize: 15, fontWeight: "800" },
  readyPill: {
    backgroundColor: colors.goldSoft,
    borderRadius: radius.pill,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  readyPillText: {
    color: colors.gold,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.7,
  },
  metrics: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  metric: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.sm,
    flexGrow: 1,
    gap: spacing.xxs,
    minWidth: 135,
    padding: spacing.sm,
  },
  metricValue: {
    color: colors.primaryDark,
    fontSize: 18,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  metricLabel: { color: colors.textMuted, fontSize: 11, fontWeight: "700" },
  sheetSupport: { color: colors.textMuted, fontSize: 12, lineHeight: 18 },
  warningText: {
    backgroundColor: colors.attentionSoft,
    borderRadius: radius.sm,
    color: colors.attention,
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 18,
    padding: spacing.sm,
  },
  ignoredText: { color: colors.textMuted, fontSize: 12, lineHeight: 18 },
  positionList: { gap: spacing.sm },
  positionRow: {
    alignItems: "flex-start",
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
    paddingBottom: spacing.sm,
  },
  positionCopy: { flex: 1, gap: 2, minWidth: 150 },
  positionName: { color: colors.text, fontSize: 14, fontWeight: "800" },
  positionClass: { color: colors.textMuted, fontSize: 11 },
  positionAmount: {
    color: colors.text,
    fontSize: 13,
    fontVariant: ["tabular-nums"],
    fontWeight: "800",
  },
  linkButton: {
    alignItems: "center",
    alignSelf: "flex-start",
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.xs,
  },
  linkButtonText: { color: colors.primary, fontSize: 13, fontWeight: "800" },
  actions: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  primaryButton: {
    alignItems: "center",
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    flexGrow: 1,
    justifyContent: "center",
    minHeight: 52,
    minWidth: 210,
    paddingHorizontal: spacing.md,
  },
  primaryButtonPressed: { backgroundColor: colors.primaryDark },
  primaryButtonText: {
    color: colors.white,
    fontSize: 14,
    fontWeight: "800",
    textAlign: "center",
  },
  cancelButton: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 52,
    paddingHorizontal: spacing.md,
  },
  cancelButtonText: { color: colors.textMuted, fontSize: 13, fontWeight: "800" },
  pressed: { opacity: 0.65 },
  disabled: { opacity: 0.45 },
});
