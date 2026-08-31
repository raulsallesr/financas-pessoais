import { useState } from "react";
import {
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import {
  ContributionSimulation,
  simulateClassContribution,
} from "../domain/contributionSimulator";
import { ASSET_CLASSES, parsePositionAmount } from "../domain/privatePortfolio";
import { AssetClass, MarketSnapshot } from "../domain/types";
import testIds from "../testing/testIds.json";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, formatCurrency, Surface } from "./Primitives";

type SubmittedContribution = {
  amount: number;
  targetClass: AssetClass;
};

const classTestIds: Record<AssetClass, string> = {
  "Renda fixa pós-fixada": testIds.contribution.classes.postFixed,
  "Renda fixa prefixada": testIds.contribution.classes.fixedRate,
  "Títulos IPCA+": testIds.contribution.classes.inflationLinked,
  "Fundos imobiliários / FIAGRO": testIds.contribution.classes.realEstate,
  "Bolsa brasileira": testIds.contribution.classes.brazilEquity,
  "Exterior / dólar": testIds.contribution.classes.international,
};

function formatPercent(value: number): string {
  return `${value.toFixed(1).replace(".", ",")}%`;
}

function formatDelta(value: number): string {
  const rounded = Math.abs(value) < 0.05 ? 0 : value;
  const signal = rounded > 0 ? "+" : rounded < 0 ? "−" : "";
  return `${signal}${Math.abs(rounded).toFixed(1).replace(".", ",")} p.p.`;
}

export function ContributionSimulatorPanel({
  hideAmounts,
  snapshot,
}: {
  hideAmounts: boolean;
  snapshot: MarketSnapshot;
}) {
  const [amountText, setAmountText] = useState("");
  const [targetClass, setTargetClass] = useState<AssetClass | null>(null);
  const [amountError, setAmountError] = useState<string | null>(null);
  const [classError, setClassError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<SubmittedContribution | null>(null);

  const simulation: ContributionSimulation | null = submitted
    ? simulateClassContribution(
        snapshot,
        submitted.amount,
        submitted.targetClass,
      )
    : null;

  function changeAmount(value: string) {
    setAmountText(value);
    setAmountError(null);
    setSubmitted(null);
  }

  function chooseClass(value: AssetClass) {
    setTargetClass(value);
    setClassError(null);
    setSubmitted(null);
  }

  function submit() {
    const amount = parsePositionAmount(amountText);
    const nextAmountError = amount
      ? null
      : "Informe um valor positivo, por exemplo 1.250,50.";
    const nextClassError = targetClass
      ? null
      : "Escolha a classe que receberia o aporte.";
    setAmountError(nextAmountError);
    setClassError(nextClassError);
    if (!amount || !targetClass) {
      setSubmitted(null);
      return;
    }
    setSubmitted({ amount, targetClass });
  }

  return (
    <Surface style={styles.panel}>
      <View style={styles.heading}>
        <Eyebrow>Simulação local</Eyebrow>
        <Text accessibilityRole="header" style={styles.title}>
          E se eu aportar nesta classe?
        </Text>
        <Text style={styles.support}>
          Informe um valor e escolha uma classe para comparar os pesos da carteira.
          Nada será salvo ou aplicado.
        </Text>
      </View>

      <View style={styles.fieldGroup}>
        <Text style={styles.fieldLabel}>Valor hipotético em reais</Text>
        <TextInput
          accessibilityHint="Aceita formatos como 1250,50 ou 1.250,50"
          accessibilityLabel="Valor hipotético em reais"
          inputMode="decimal"
          keyboardType={Platform.OS === "ios" ? "decimal-pad" : "numeric"}
          onBlur={() => {
            if (amountText && !parsePositionAmount(amountText)) {
              setAmountError("Informe um valor positivo, por exemplo 1.250,50.");
            }
          }}
          onChangeText={changeAmount}
          placeholder="Ex.: 1.250,50"
          placeholderTextColor={colors.textMuted}
          returnKeyType="done"
          style={[styles.input, amountError && styles.inputError]}
          testID={testIds.contribution.amountInput}
          value={amountText}
        />
        {amountError ? (
          <Text accessibilityLiveRegion="polite" style={styles.errorText}>
            {amountError}
          </Text>
        ) : null}
      </View>

      <View style={styles.fieldGroup}>
        <Text style={styles.fieldLabel}>Classe que receberia o aporte</Text>
        <Text style={styles.fieldHelper}>
          A escolha é sua; o app não indica classe, ativo ou produto.
        </Text>
        <View accessibilityRole="radiogroup" style={styles.classGrid}>
          {ASSET_CLASSES.map((assetClass) => {
            const selected = targetClass === assetClass;
            return (
              <Pressable
                accessibilityLabel={assetClass}
                accessibilityRole="radio"
                accessibilityState={{ selected }}
                key={assetClass}
                onPress={() => chooseClass(assetClass)}
                style={({ pressed }) => [
                  styles.classOption,
                  selected && styles.classOptionSelected,
                  pressed && styles.pressed,
                ]}
                testID={classTestIds[assetClass]}
              >
                <View style={[styles.classDot, selected && styles.classDotSelected]} />
                <Text
                  style={[
                    styles.classOptionText,
                    selected && styles.classOptionTextSelected,
                  ]}
                >
                  {assetClass}
                </Text>
              </Pressable>
            );
          })}
        </View>
        {classError ? (
          <Text accessibilityLiveRegion="polite" style={styles.errorText}>
            {classError}
          </Text>
        ) : null}
      </View>

      <Pressable
        accessibilityRole="button"
        onPress={submit}
        style={({ pressed }) => [styles.submitButton, pressed && styles.submitPressed]}
        testID={testIds.contribution.submit}
      >
        <Text style={styles.submitText}>Comparar distribuição</Text>
      </Pressable>

      {simulation ? (
        <View
          accessibilityLiveRegion="polite"
          style={styles.resultBlock}
          testID={testIds.contribution.result}
        >
          <View style={styles.resultSummary}>
            <Text style={styles.resultEyebrow}>CENÁRIO HIPOTÉTICO</Text>
            <Text style={styles.resultTitle}>
              {formatCurrency(simulation.contributionAmount, hideAmounts)} em{" "}
              {simulation.targetClass}
            </Text>
            <View style={styles.totalGrid}>
              <View style={styles.totalCard}>
                <Text style={styles.totalLabel}>Carteira antes</Text>
                <Text style={styles.totalValue}>
                  {formatCurrency(simulation.portfolioBefore, hideAmounts)}
                </Text>
              </View>
              <View style={[styles.totalCard, styles.totalCardAfter]}>
                <Text style={styles.totalLabel}>Carteira depois</Text>
                <Text style={styles.totalValue}>
                  {formatCurrency(simulation.portfolioAfter, hideAmounts)}
                </Text>
              </View>
            </View>
          </View>

          <View style={styles.allocationList}>
            {simulation.allocations.map((item) => (
              <View
                accessibilityLabel={`${item.assetClass}: antes ${formatPercent(item.allocationBeforePercent)}, depois ${formatPercent(item.allocationAfterPercent)}, variação ${formatDelta(item.deltaPercentagePoints)}${item.receivesContribution ? ", recebe o aporte" : ""}`}
                accessible
                key={item.assetClass}
                style={[
                  styles.allocationRow,
                  item.receivesContribution && styles.allocationRowTarget,
                ]}
              >
                <View style={styles.allocationCopy}>
                  <Text style={styles.allocationName}>{item.assetClass}</Text>
                  {item.receivesContribution ? (
                    <Text style={styles.targetLabel}>RECEBE O APORTE</Text>
                  ) : null}
                </View>
                <View style={styles.comparison}>
                  <Text style={styles.beforePercent}>
                    {formatPercent(item.allocationBeforePercent)}
                  </Text>
                  <Text accessibilityElementsHidden style={styles.arrow}>→</Text>
                  <Text style={styles.afterPercent}>
                    {formatPercent(item.allocationAfterPercent)}
                  </Text>
                  <Text
                    style={[
                      styles.delta,
                      item.deltaPercentagePoints > 0 && styles.deltaPositive,
                    ]}
                  >
                    {formatDelta(item.deltaPercentagePoints)}
                  </Text>
                </View>
              </View>
            ))}
          </View>

          <Text style={styles.resultGuardrail}>
            Esta conta mostra apenas distribuição por classe. Não estima retorno,
            risco, imposto ou melhor investimento.
          </Text>
        </View>
      ) : null}
    </Surface>
  );
}

const styles = StyleSheet.create({
  panel: { gap: spacing.lg },
  heading: { gap: spacing.xs },
  title: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: -0.4,
    lineHeight: 28,
  },
  support: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  fieldGroup: { gap: spacing.xs },
  fieldLabel: { color: colors.text, fontSize: 14, fontWeight: "800" },
  fieldHelper: { color: colors.textMuted, fontSize: 12, lineHeight: 18 },
  input: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    color: colors.text,
    fontSize: 16,
    minHeight: 52,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
  },
  inputError: { borderColor: colors.danger, borderWidth: 2 },
  errorText: {
    color: colors.danger,
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 18,
  },
  classGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  classOption: {
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    flexDirection: "row",
    gap: spacing.xs,
    minHeight: 48,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  classOptionSelected: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderWidth: 2,
  },
  classDot: {
    borderColor: colors.textMuted,
    borderRadius: radius.pill,
    borderWidth: 1,
    height: 12,
    width: 12,
  },
  classDotSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  classOptionText: {
    color: colors.textMuted,
    flexShrink: 1,
    fontSize: 12,
    fontWeight: "700",
  },
  classOptionTextSelected: { color: colors.primaryDark },
  submitButton: {
    alignItems: "center",
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    justifyContent: "center",
    minHeight: 52,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  submitPressed: { backgroundColor: colors.primaryDark },
  submitText: { color: colors.white, fontSize: 15, fontWeight: "800" },
  resultBlock: { gap: spacing.md },
  resultSummary: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    gap: spacing.sm,
    padding: spacing.md,
  },
  resultEyebrow: {
    color: colors.primary,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1.2,
  },
  resultTitle: {
    color: colors.primaryDark,
    fontSize: 17,
    fontWeight: "900",
    lineHeight: 23,
  },
  totalGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  totalCard: {
    backgroundColor: "rgba(255,255,255,0.64)",
    borderRadius: radius.sm,
    flex: 1,
    gap: spacing.xxs,
    minWidth: 135,
    padding: spacing.sm,
  },
  totalCardAfter: { backgroundColor: colors.surface },
  totalLabel: { color: colors.textMuted, fontSize: 11, fontWeight: "700" },
  totalValue: {
    color: colors.text,
    fontSize: 16,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  allocationList: { gap: spacing.xs },
  allocationRow: {
    alignItems: "center",
    backgroundColor: colors.surfaceMuted,
    borderColor: "transparent",
    borderRadius: radius.sm,
    borderWidth: 1,
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
    minHeight: 64,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  allocationRowTarget: {
    backgroundColor: colors.goldSoft,
    borderColor: "#EBCB91",
  },
  allocationCopy: { flex: 1, gap: 3, minWidth: 150 },
  allocationName: { color: colors.text, fontSize: 13, fontWeight: "800" },
  targetLabel: {
    color: colors.gold,
    fontSize: 9,
    fontWeight: "900",
    letterSpacing: 0.7,
  },
  comparison: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
    justifyContent: "flex-end",
  },
  beforePercent: {
    color: colors.textMuted,
    fontSize: 13,
    fontVariant: ["tabular-nums"],
    fontWeight: "700",
  },
  arrow: { color: colors.textMuted, fontSize: 13 },
  afterPercent: {
    color: colors.primaryDark,
    fontSize: 15,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  delta: {
    color: colors.textMuted,
    fontSize: 10,
    fontVariant: ["tabular-nums"],
    fontWeight: "800",
  },
  deltaPositive: { color: colors.primary },
  resultGuardrail: {
    backgroundColor: colors.goldSoft,
    borderRadius: radius.sm,
    color: colors.textMuted,
    fontSize: 12,
    lineHeight: 19,
    padding: spacing.sm,
  },
  pressed: { opacity: 0.65 },
});
