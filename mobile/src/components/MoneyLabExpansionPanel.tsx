import { useState } from "react";
import {
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  useWindowDimensions,
  View,
} from "react-native";

import {
  adjustForInflation,
  calculateDoublingTime,
  calculateMilestoneTimeline,
  calculateMonthlyYieldEquivalent,
  calculateReserveJourney,
  compareAnnualCostDrag,
  compareContributionImpact,
  CompoundGrowthInput,
  MONEY_LAB_LIMITS,
  simulateCompoundGrowth,
  simulateExtraContribution,
} from "../domain/moneyLab";
import { parsePositionAmount } from "../domain/privatePortfolio";
import testIds from "../testing/testIds.json";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, formatCurrency, Surface } from "./Primitives";
import {
  MoneyLabExpansionTool,
  MoneyLabSession,
} from "./MoneyLabPanel";

type FieldKey =
  | "initial"
  | "monthly"
  | "rate"
  | "years"
  | "bonus"
  | "reserveCurrent"
  | "reserveExpense"
  | "reserveContribution"
  | "cost"
  | "inflation";

type FieldErrors = Partial<Record<FieldKey, string>>;

const tools: readonly {
  key: MoneyLabExpansionTool;
  index: string;
  title: string;
  support: string;
  testID: string;
}[] = [
  {
    key: "time",
    index: "06",
    title: "O poder do tempo",
    support: "Dobra, marcos e régua interativa.",
    testID: testIds.moneyLab.expansion.tools.time,
  },
  {
    key: "income",
    index: "07",
    title: "Dinheiro que entra",
    support: "Mês, bônus e 13º hipotético.",
    testID: testIds.moneyLab.expansion.tools.income,
  },
  {
    key: "reserve",
    index: "08",
    title: "Minha segurança",
    support: "Meses cobertos e caminho da reserva.",
    testID: testIds.moneyLab.expansion.tools.reserve,
  },
  {
    key: "complete",
    index: "09",
    title: "Compare completo",
    support: "Aportes, inflação e custo hipotético.",
    testID: testIds.moneyLab.expansion.tools.complete,
  },
];

const yearStops = [1, 5, 10, 20, 30, 50] as const;
const reserveTargets = [3, 6, 12] as const;

function parseMoney(value: string, allowZero: boolean): number | null {
  const normalized = value
    .trim()
    .replace(/^R\$\s*/i, "")
    .replace(/\s/g, "");
  if (allowZero && /^0+(?:[,.]0+)?$/.test(normalized)) {
    return 0;
  }
  return parsePositionAmount(value);
}

function parseLocalizedNumber(value: string): number | null {
  const normalized = value.trim().replace(/%/g, "").replace(/\s/g, "");
  if (!normalized || !/^\d+(?:[,.]\d+)?$/.test(normalized)) {
    return null;
  }
  const parsed = Number(normalized.replace(",", "."));
  return Number.isFinite(parsed) ? parsed : null;
}

function parseYears(value: string): number | null {
  const parsed = parseLocalizedNumber(value);
  return parsed !== null && Number.isInteger(parsed) ? parsed : null;
}

function resolveGrowthInput(session: MoneyLabSession): {
  input: CompoundGrowthInput | null;
  errors: FieldErrors;
} {
  const initialAmount = parseMoney(session.initialAmountText, true);
  const monthlyContribution = parseMoney(
    session.monthlyContributionText,
    true,
  );
  const annualRatePercent = parseLocalizedNumber(session.annualRateText);
  const years = parseYears(session.yearsText);
  const errors: FieldErrors = {};

  if (initialAmount === null) {
    errors.initial = "Use um valor entre zero e R$ 999 bilhões.";
  }
  if (monthlyContribution === null) {
    errors.monthly = "Use um aporte mensal válido, inclusive zero.";
  }
  if (
    annualRatePercent === null ||
    annualRatePercent < 0 ||
    annualRatePercent > MONEY_LAB_LIMITS.maxAnnualRatePercent
  ) {
    errors.rate = "Use uma taxa entre 0% e 200% ao ano.";
  }
  if (years === null || years < 1 || years > MONEY_LAB_LIMITS.maxYears) {
    errors.years = "Use um prazo entre 1 e 50 anos inteiros.";
  }
  if (initialAmount === 0 && monthlyContribution === 0) {
    errors.initial = "Informe um valor inicial ou um aporte mensal.";
    errors.monthly = "Informe um valor inicial ou um aporte mensal.";
  }
  if (Object.keys(errors).length) {
    return { input: null, errors };
  }
  return {
    input: {
      initialAmount: initialAmount!,
      monthlyContribution: monthlyContribution!,
      annualRatePercent: annualRatePercent!,
      years: years!,
    },
    errors,
  };
}

function formatPercent(value: number, digits = 1): string {
  return value.toFixed(digits).replace(".", ",") + "%";
}

function formatDuration(months: number | null, horizonYears = 50): string {
  if (months === null) {
    return `Não chegou em ${horizonYears} anos`;
  }
  if (months === 0) {
    return "Já alcançado";
  }
  const years = Math.floor(months / 12);
  const remainingMonths = months % 12;
  const parts: string[] = [];
  if (years) {
    parts.push(`${years} ${years === 1 ? "ano" : "anos"}`);
  }
  if (remainingMonths) {
    parts.push(
      `${remainingMonths} ${remainingMonths === 1 ? "mês" : "meses"}`,
    );
  }
  return parts.join(" e ");
}

function NumericField({
  error,
  hiddenAmount = false,
  label,
  onBlur,
  onChangeText,
  suffix,
  testID,
  value,
}: {
  error?: string;
  hiddenAmount?: boolean;
  label: string;
  onBlur?: () => void;
  onChangeText: (value: string) => void;
  suffix?: string;
  testID: string;
  value: string;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <View style={[styles.inputFrame, error && styles.inputFrameError]}>
        <TextInput
          accessibilityLabel={label}
          inputMode="decimal"
          keyboardType={Platform.OS === "ios" ? "decimal-pad" : "numeric"}
          onBlur={onBlur}
          onChangeText={onChangeText}
          placeholder="0"
          placeholderTextColor={colors.textMuted}
          returnKeyType="done"
          secureTextEntry={hiddenAmount}
          style={styles.input}
          testID={testID}
          value={value}
        />
        {suffix ? <Text style={styles.inputSuffix}>{suffix}</Text> : null}
      </View>
      {error ? (
        <Text accessibilityLiveRegion="polite" style={styles.errorText}>
          {error}
        </Text>
      ) : null}
    </View>
  );
}

function Metric({
  emphasis = false,
  label,
  value,
}: {
  emphasis?: boolean;
  label: string;
  value: string;
}) {
  return (
    <View style={[styles.metric, emphasis && styles.metricEmphasis]}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={[styles.metricValue, emphasis && styles.metricValueEmphasis]}>
        {value}
      </Text>
    </View>
  );
}

function ResultGuardrail({ children }: { children: string }) {
  return (
    <View style={styles.guardrail}>
      <Text style={styles.guardrailTitle}>O que esta conta não prova</Text>
      <Text style={styles.guardrailText}>{children}</Text>
    </View>
  );
}

function ToggleRow({
  checked,
  onPress,
  support,
  testID,
  title,
}: {
  checked: boolean;
  onPress: () => void;
  support: string;
  testID: string;
  title: string;
}) {
  return (
    <Pressable
      accessibilityRole="switch"
      accessibilityState={{ checked }}
      onPress={onPress}
      style={({ pressed }) => [styles.switchRow, pressed && styles.pressed]}
      testID={testID}
    >
      <View style={[styles.switchTrack, checked && styles.switchTrackSelected]}>
        <View style={[styles.switchThumb, checked && styles.switchThumbSelected]} />
      </View>
      <View style={styles.switchCopy}>
        <Text style={styles.switchTitle}>{title}</Text>
        <Text style={styles.switchSupport}>{support}</Text>
      </View>
    </Pressable>
  );
}

export function MoneyLabExpansionPanel({
  hideAmounts,
  onSessionChange,
  session,
}: {
  hideAmounts: boolean;
  onSessionChange: (session: MoneyLabSession) => void;
  session: MoneyLabSession;
}) {
  const { width } = useWindowDimensions();
  const compact = width < 420;
  const [touched, setTouched] = useState<Partial<Record<FieldKey, boolean>>>({});
  const { input: growthInput, errors: growthErrors } =
    resolveGrowthInput(session);

  function patch(values: Partial<MoneyLabSession>) {
    onSessionChange({ ...session, ...values });
  }

  function touch(field: FieldKey) {
    setTouched((current) => ({ ...current, [field]: true }));
  }

  function visibleError(field: FieldKey, error?: string) {
    return touched[field] ? error : undefined;
  }

  function renderCommonFields(includeYears = true) {
    return (
      <View style={styles.fieldGrid}>
        <NumericField
          error={visibleError("initial", growthErrors.initial)}
          hiddenAmount={hideAmounts}
          label="Valor inicial"
          onBlur={() => touch("initial")}
          onChangeText={(value) => patch({ initialAmountText: value })}
          suffix="R$"
          testID={testIds.moneyLab.expansion.initialInput}
          value={session.initialAmountText}
        />
        <NumericField
          error={visibleError("monthly", growthErrors.monthly)}
          hiddenAmount={hideAmounts}
          label="Aporte mensal"
          onBlur={() => touch("monthly")}
          onChangeText={(value) => patch({ monthlyContributionText: value })}
          suffix="R$"
          testID={testIds.moneyLab.expansion.monthlyInput}
          value={session.monthlyContributionText}
        />
        <NumericField
          error={visibleError("rate", growthErrors.rate)}
          label="Taxa efetiva anual"
          onBlur={() => touch("rate")}
          onChangeText={(value) => patch({ annualRateText: value })}
          suffix="% a.a."
          testID={testIds.moneyLab.expansion.rateInput}
          value={session.annualRateText}
        />
        {includeYears ? (
          <NumericField
            error={visibleError("years", growthErrors.years)}
            label="Prazo"
            onBlur={() => touch("years")}
            onChangeText={(value) => patch({ yearsText: value })}
            suffix="anos"
            testID={testIds.moneyLab.expansion.yearsInput}
            value={session.yearsText}
          />
        ) : null}
      </View>
    );
  }

  function renderTime() {
    const projection = growthInput ? simulateCompoundGrowth(growthInput) : null;
    const doubling =
      growthInput && growthInput.initialAmount > 0
        ? calculateDoublingTime({
            initialAmount: growthInput.initialAmount,
            monthlyContribution: growthInput.monthlyContribution,
            annualRatePercent: growthInput.annualRatePercent,
          })
        : null;
    const milestones = growthInput
      ? calculateMilestoneTimeline(growthInput)
      : [];
    const currentYears = parseYears(session.yearsText);

    function stepYears(delta: number) {
      const safeCurrent = currentYears ?? 1;
      patch({
        yearsText: String(
          Math.min(
            MONEY_LAB_LIMITS.maxYears,
            Math.max(1, safeCurrent + delta),
          ),
        ),
      });
    }

    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>v0.5.7 · O poder do tempo</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            Toque no tempo e veja a história mudar
          </Text>
          <Text style={styles.toolSupport}>
            A mesma hipótese responde quando dobra e quando cruza três marcos.
          </Text>
        </View>
        {renderCommonFields(false)}
        <View style={styles.rulerBlock}>
          <View style={styles.rulerHeading}>
            <View style={styles.rulerCopy}>
              <Text style={styles.fieldLabel}>Régua de tempo</Text>
              <Text style={styles.rulerHint}>
                Toque um marco ou use menos e mais para avançar ano a ano.
              </Text>
            </View>
            <View style={styles.stepper}>
              <Pressable
                accessibilityLabel="Diminuir um ano"
                accessibilityRole="button"
                accessibilityState={{ disabled: currentYears === 1 }}
                disabled={currentYears === 1}
                onPress={() => stepYears(-1)}
                style={({ pressed }) => [
                  styles.stepButton,
                  currentYears === 1 && styles.disabled,
                  pressed && styles.pressed,
                ]}
                testID={testIds.moneyLab.expansion.yearMinus}
              >
                <Text style={styles.stepButtonText}>−</Text>
              </Pressable>
              <Text accessibilityLiveRegion="polite" style={styles.stepValue}>
                {currentYears ?? "—"} {currentYears === 1 ? "ano" : "anos"}
              </Text>
              <Pressable
                accessibilityLabel="Aumentar um ano"
                accessibilityRole="button"
                accessibilityState={{
                  disabled: currentYears === MONEY_LAB_LIMITS.maxYears,
                }}
                disabled={currentYears === MONEY_LAB_LIMITS.maxYears}
                onPress={() => stepYears(1)}
                style={({ pressed }) => [
                  styles.stepButton,
                  currentYears === MONEY_LAB_LIMITS.maxYears && styles.disabled,
                  pressed && styles.pressed,
                ]}
                testID={testIds.moneyLab.expansion.yearPlus}
              >
                <Text style={styles.stepButtonText}>+</Text>
              </Pressable>
            </View>
          </View>
          <View accessibilityRole="radiogroup" style={styles.rulerStops}>
            {yearStops.map((year) => {
              const selected = currentYears === year;
              return (
                <Pressable
                  accessibilityLabel={`${year} ${year === 1 ? "ano" : "anos"}`}
                  accessibilityRole="radio"
                  accessibilityState={{ selected }}
                  key={year}
                  onPress={() => patch({ yearsText: String(year) })}
                  style={({ pressed }) => [
                    styles.rulerStop,
                    selected && styles.rulerStopSelected,
                    pressed && styles.pressed,
                  ]}
                >
                  <View
                    style={[
                      styles.rulerDot,
                      selected && styles.rulerDotSelected,
                    ]}
                  />
                  <Text
                    style={[
                      styles.rulerStopText,
                      selected && styles.rulerStopTextSelected,
                    ]}
                  >
                    {year}
                  </Text>
                </Pressable>
              );
            })}
          </View>
          {visibleError("years", growthErrors.years) ? (
            <Text style={styles.errorText}>
              {visibleError("years", growthErrors.years)}
            </Text>
          ) : null}
        </View>
        {projection ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.expansion.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>
                NO PONTO ESCOLHIDO DA RÉGUA
              </Text>
              <Text style={styles.resultHeroValue}>
                {formatCurrency(projection.futureValue, hideAmounts)}
              </Text>
              <Text style={styles.resultHeroSupport}>
                {growthInput!.years} {growthInput!.years === 1 ? "ano" : "anos"}
                , com capital e juros separados na conta
              </Text>
            </View>
            <View style={styles.sectionBlock}>
              <Text style={styles.sectionTitle}>Quando o valor inicial dobra?</Text>
              {doubling ? (
                <View style={styles.metrics}>
                  <Metric
                    emphasis
                    label="Com os aportes mensais"
                    value={formatDuration(doubling.withContributionsMonths)}
                  />
                  <Metric
                    label="Sem novos aportes"
                    value={formatDuration(doubling.withoutContributionsMonths)}
                  />
                </View>
              ) : (
                <Text style={styles.inlineNote}>
                  Informe um valor inicial acima de zero para acompanhar a dobra.
                </Text>
              )}
            </View>
            <View style={styles.sectionBlock}>
              <Text style={styles.sectionTitle}>Marcos da jornada</Text>
              <View style={styles.milestoneList}>
                {milestones.map((milestone) => (
                  <View
                    accessibilityLabel={`${formatCurrency(milestone.amount, hideAmounts)}: ${formatDuration(milestone.reachedAtMonths, growthInput!.years)}`}
                    accessible
                    key={milestone.amount}
                    style={styles.milestoneRow}
                  >
                    <View style={styles.milestoneMark} />
                    <View style={styles.milestoneCopy}>
                      <Text style={styles.milestoneAmount}>
                        {formatCurrency(milestone.amount, hideAmounts)}
                      </Text>
                      <Text style={styles.milestoneSupport}>
                        {milestone.point
                          ? `${formatDuration(milestone.reachedAtMonths)} · ${formatCurrency(milestone.point.interestEarned, hideAmounts)} em juros do cenário`
                          : `Ainda não aparece em ${growthInput!.years} ${growthInput!.years === 1 ? "ano" : "anos"}`}
                      </Text>
                    </View>
                  </View>
                ))}
              </View>
            </View>
            <ResultGuardrail>
              Dobrar e cruzar marcos depende de taxa constante e aportes sem
              interrupção. A régua não prevê datas de mercado nem garante metas.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderIncome() {
    const bonusAmount = parseMoney(session.bonusAmountText, false);
    const bonusError =
      bonusAmount === null ? "Informe um aporte extra positivo." : undefined;
    const monthlyYield =
      growthInput && growthInput.initialAmount > 0
        ? calculateMonthlyYieldEquivalent(
            growthInput.initialAmount,
            growthInput.annualRatePercent,
          )
        : null;
    const extra =
      growthInput && bonusAmount !== null
        ? simulateExtraContribution({
            input: growthInput,
            extraAmount: bonusAmount,
            cadence: session.bonusCadence,
          })
        : null;
    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>v0.5.8 · Dinheiro que entra</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            Quanto rende no mês e o que um extra muda?
          </Text>
          <Text style={styles.toolSupport}>
            Converta a taxa corretamente e experimente um bônus sem prometer renda.
          </Text>
        </View>
        {renderCommonFields()}
        <NumericField
          error={visibleError("bonus", bonusError)}
          hiddenAmount={hideAmounts}
          label="Aporte extra hipotético"
          onBlur={() => touch("bonus")}
          onChangeText={(value) => patch({ bonusAmountText: value })}
          suffix="R$"
          testID={testIds.moneyLab.expansion.bonusInput}
          value={session.bonusAmountText}
        />
        <View style={styles.choiceBlock}>
          <Text style={styles.fieldLabel}>Quando o extra entra?</Text>
          <View accessibilityRole="radiogroup" style={styles.chipRow}>
            {([
              ["today", "Uma vez, hoje"],
              ["yearly", "Todo fim de ano"],
            ] as const).map(([cadence, label]) => {
              const selected = session.bonusCadence === cadence;
              return (
                <Pressable
                  accessibilityRole="radio"
                  accessibilityState={{ selected }}
                  key={cadence}
                  onPress={() => patch({ bonusCadence: cadence })}
                  style={({ pressed }) => [
                    styles.chip,
                    selected && styles.chipSelected,
                    pressed && styles.pressed,
                  ]}
                >
                  <Text
                    style={[
                      styles.chipText,
                      selected && styles.chipTextSelected,
                    ]}
                  >
                    {label}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </View>
        {extra ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.expansion.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>EFEITO DO APORTE EXTRA</Text>
              <Text style={styles.resultHeroValue}>
                +{formatCurrency(extra.difference, hideAmounts)}
              </Text>
              <Text style={styles.resultHeroSupport}>
                diferença contra o mesmo cenário sem esse valor extra
              </Text>
            </View>
            <View style={styles.metrics}>
              <Metric
                label="Sem o extra"
                value={formatCurrency(extra.base.futureValue, hideAmounts)}
              />
              <Metric
                emphasis
                label="Com o extra"
                value={formatCurrency(extra.withExtra.futureValue, hideAmounts)}
              />
              <Metric
                label="Extra colocado"
                value={formatCurrency(extra.extraContributed, hideAmounts)}
              />
            </View>
            <View style={styles.insightCard}>
              <Text style={styles.insightLabel}>EQUIVALENTE DE UM MÊS</Text>
              {monthlyYield ? (
                <>
                  <Text style={styles.insightValue}>
                    {formatCurrency(monthlyYield.oneMonthInterest, hideAmounts)}
                  </Text>
                  <Text style={styles.insightText}>
                    sobre o valor inicial, usando taxa mensal equivalente de{" "}
                    {formatPercent(monthlyYield.monthlyRatePercent, 2)} — não a
                    taxa anual dividida por 12.
                  </Text>
                </>
              ) : (
                <Text style={styles.insightText}>
                  Informe valor inicial acima de zero para ver o equivalente mensal.
                </Text>
              )}
            </View>
            <ResultGuardrail>
              Equivalente mensal não significa pagamento mensal, renda garantida
              ou liquidez. O extra não representa produto, 13º real ou obrigação.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderReserve() {
    const currentReserve = parseMoney(session.reserveCurrentText, true);
    const monthlyExpenses = parseMoney(session.reserveExpenseText, false);
    const monthlyContribution = parseMoney(
      session.reserveContributionText,
      true,
    );
    const currentError =
      currentReserve === null ? "Informe uma reserva atual válida." : undefined;
    const expenseError =
      monthlyExpenses === null ? "Informe um gasto mensal positivo." : undefined;
    const contributionError =
      monthlyContribution === null
        ? "Informe um aporte mensal válido, inclusive zero."
        : undefined;
    const result =
      currentReserve !== null &&
      monthlyExpenses !== null &&
      monthlyContribution !== null
        ? calculateReserveJourney({
            currentReserve,
            monthlyEssentialExpenses: monthlyExpenses,
            monthlyContribution,
            targetMonths: session.reserveTargetMonths,
          })
        : null;
    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>v0.5.9 · Minha segurança</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            Quantos meses minha reserva cobre?
          </Text>
          <Text style={styles.toolSupport}>
            Você escolhe a meta. A conta não define o número certo para sua vida.
          </Text>
        </View>
        <View style={styles.fieldGrid}>
          <NumericField
            error={visibleError("reserveCurrent", currentError)}
            hiddenAmount={hideAmounts}
            label="Reserva atual"
            onBlur={() => touch("reserveCurrent")}
            onChangeText={(value) => patch({ reserveCurrentText: value })}
            suffix="R$"
            testID={testIds.moneyLab.expansion.reserveCurrentInput}
            value={session.reserveCurrentText}
          />
          <NumericField
            error={visibleError("reserveExpense", expenseError)}
            hiddenAmount={hideAmounts}
            label="Gasto essencial mensal"
            onBlur={() => touch("reserveExpense")}
            onChangeText={(value) => patch({ reserveExpenseText: value })}
            suffix="R$"
            testID={testIds.moneyLab.expansion.reserveExpenseInput}
            value={session.reserveExpenseText}
          />
          <NumericField
            error={visibleError("reserveContribution", contributionError)}
            hiddenAmount={hideAmounts}
            label="Aporte mensal à reserva"
            onBlur={() => touch("reserveContribution")}
            onChangeText={(value) => patch({ reserveContributionText: value })}
            suffix="R$"
            testID={testIds.moneyLab.expansion.reserveContributionInput}
            value={session.reserveContributionText}
          />
        </View>
        <View style={styles.choiceBlock}>
          <Text style={styles.fieldLabel}>Meta escolhida por você</Text>
          <View accessibilityRole="radiogroup" style={styles.chipRow}>
            {reserveTargets.map((months) => {
              const selected = session.reserveTargetMonths === months;
              return (
                <Pressable
                  accessibilityRole="radio"
                  accessibilityState={{ selected }}
                  key={months}
                  onPress={() => patch({ reserveTargetMonths: months })}
                  style={({ pressed }) => [
                    styles.chip,
                    selected && styles.chipSelected,
                    pressed && styles.pressed,
                  ]}
                >
                  <Text
                    style={[
                      styles.chipText,
                      selected && styles.chipTextSelected,
                    ]}
                  >
                    {months} meses
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </View>
        {result ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.expansion.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>COBERTURA ATUAL</Text>
              <Text style={styles.resultHeroValue}>
                {result.currentMonthsCovered.toFixed(1).replace(".", ",")} meses
              </Text>
              <Text style={styles.resultHeroSupport}>
                reserva atual dividida pelo gasto essencial informado
              </Text>
            </View>
            <View style={styles.metrics}>
              <Metric
                label={`Meta de ${result.targetMonths} meses`}
                value={formatCurrency(result.targetAmount, hideAmounts)}
              />
              <Metric
                label="Quanto falta"
                value={formatCurrency(result.missingAmount, hideAmounts)}
              />
              <Metric
                emphasis
                label="Prazo mecânico"
                value={
                  result.alreadyReached
                    ? "Meta já alcançada"
                    : result.monthsToTarget === null
                      ? "Sem prazo com aporte zero"
                      : formatDuration(result.monthsToTarget)
                }
              />
            </View>
            <ResultGuardrail>
              A conta não inclui rendimento, inflação, seguro, estabilidade de
              renda ou imprevistos. A meta é escolhida por você, não recomendada.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderComplete() {
    const contributionComparison = growthInput
      ? compareContributionImpact(growthInput)
      : null;
    const inflationRate = parseLocalizedNumber(session.inflationRateText);
    const inflationError =
      session.showInflation &&
      (inflationRate === null ||
        inflationRate < 0 ||
        inflationRate > MONEY_LAB_LIMITS.maxAnnualRatePercent)
        ? "Use uma inflação entre 0% e 200% ao ano."
        : undefined;
    const annualCost = parseLocalizedNumber(session.annualCostText);
    const costError =
      session.showAnnualCost &&
      (annualCost === null ||
        annualCost < 0 ||
        annualCost > MONEY_LAB_LIMITS.maxAnnualRatePercent)
        ? "Use um custo entre 0% e 200% ao ano."
        : session.showAnnualCost &&
            growthInput &&
            annualCost !== null &&
            annualCost > growthInput.annualRatePercent
          ? "Use um custo menor ou igual à taxa do cenário."
          : undefined;
    const presentValue =
      contributionComparison && session.showInflation && !inflationError
        ? adjustForInflation(
            contributionComparison.withContributions.futureValue,
            inflationRate!,
            growthInput!.years,
          )
        : null;
    const costComparison =
      growthInput && session.showAnnualCost && !costError
        ? compareAnnualCostDrag(growthInput, annualCost!)
        : null;
    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>v0.6.0 · Laboratório completo</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            O que muda com aporte, inflação e custo?
          </Text>
          <Text style={styles.toolSupport}>
            Abra somente as camadas que quiser e compare sempre a mesma base.
          </Text>
        </View>
        {renderCommonFields()}
        <ToggleRow
          checked={session.showInflation}
          onPress={() => patch({ showInflation: !session.showInflation })}
          support="Traduz o resultado para poder de compra do início."
          testID={testIds.moneyLab.expansion.inflationToggle}
          title="Considerar inflação hipotética"
        />
        {session.showInflation ? (
          <NumericField
            error={visibleError("inflation", inflationError)}
            label="Inflação anual hipotética"
            onBlur={() => touch("inflation")}
            onChangeText={(value) => patch({ inflationRateText: value })}
            suffix="% a.a."
            testID={testIds.moneyLab.expansion.inflationInput}
            value={session.inflationRateText}
          />
        ) : null}
        <ToggleRow
          checked={session.showAnnualCost}
          onPress={() => patch({ showAnnualCost: !session.showAnnualCost })}
          support="Desconta um custo anual mecânico da taxa, sem representar produto."
          testID={testIds.moneyLab.expansion.costToggle}
          title="Simular custo anual"
        />
        {session.showAnnualCost ? (
          <NumericField
            error={visibleError("cost", costError)}
            label="Custo anual hipotético"
            onBlur={() => touch("cost")}
            onChangeText={(value) => patch({ annualCostText: value })}
            suffix="% a.a."
            testID={testIds.moneyLab.expansion.costInput}
            value={session.annualCostText}
          />
        ) : null}
        {contributionComparison ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.expansion.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>COM APORTES MENSAIS</Text>
              <Text style={styles.resultHeroValue}>
                {formatCurrency(
                  contributionComparison.withContributions.futureValue,
                  hideAmounts,
                )}
              </Text>
              <Text style={styles.resultHeroSupport}>
                +
                {formatCurrency(contributionComparison.difference, hideAmounts)}
                {" "}contra manter apenas o valor inicial na mesma taxa
              </Text>
            </View>
            <View style={styles.metrics}>
              <Metric
                label="Sem novos aportes"
                value={formatCurrency(
                  contributionComparison.withoutContributions.futureValue,
                  hideAmounts,
                )}
              />
              <Metric
                emphasis
                label="Com aportes"
                value={formatCurrency(
                  contributionComparison.withContributions.futureValue,
                  hideAmounts,
                )}
              />
              {presentValue !== null ? (
                <Metric
                  label="Com aportes, em dinheiro de hoje"
                  value={formatCurrency(presentValue, hideAmounts)}
                />
              ) : null}
              {costComparison ? (
                <>
                  <Metric
                    label={`Após custo · taxa líquida ${formatPercent(costComparison.netAnnualRatePercent, 2)}`}
                    value={formatCurrency(
                      costComparison.afterCost.futureValue,
                      hideAmounts,
                    )}
                  />
                  <Metric
                    label="Efeito acumulado do custo"
                    value={formatCurrency(costComparison.difference, hideAmounts)}
                  />
                </>
              ) : null}
            </View>
            <View style={styles.explainGrid}>
              <View style={styles.explainCard}>
                <Text style={styles.explainTitle}>Por que acelera?</Text>
                <Text style={styles.explainText}>
                  Cada aporte entra na base que pode gerar juros nos meses seguintes.
                </Text>
              </View>
              <View style={styles.explainCard}>
                <Text style={styles.explainTitle}>Por que o custo cresce?</Text>
                <Text style={styles.explainText}>
                  Uma diferença pequena de taxa também se repete sobre a base acumulada.
                </Text>
              </View>
            </View>
            <ResultGuardrail>
              Custo é uma hipótese matemática, não taxa real de produto. Imposto,
              liquidez, volatilidade, retorno previsto e recomendação ficam fora.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  return (
    <Surface style={styles.panel} testID={testIds.moneyLab.expansion.panel}>
      <View style={styles.heading}>
        <Eyebrow>Continue explorando</Eyebrow>
        <Text accessibilityRole="header" style={styles.title}>
          Tempo, entradas e segurança em perguntas simples
        </Text>
        <Text style={styles.support}>
          Quatro caminhos novos. Tudo continua somente nesta sessão e separado
          da carteira local.
        </Text>
        {hideAmounts ? (
          <Text style={styles.privateNote}>
            Modo discreto ativo: entradas e resultados monetários estão ocultos.
          </Text>
        ) : null}
      </View>
      <View accessibilityRole="radiogroup" style={styles.toolGrid}>
        {tools.map((tool) => {
          const selected = session.expansionTool === tool.key;
          return (
            <Pressable
              accessibilityLabel={`${tool.title}. ${tool.support}`}
              accessibilityRole="radio"
              accessibilityState={{ selected }}
              key={tool.key}
              onPress={() => patch({ expansionTool: tool.key })}
              style={({ pressed }) => [
                styles.toolOption,
                compact && styles.toolOptionCompact,
                selected && styles.toolOptionSelected,
                pressed && styles.pressed,
              ]}
              testID={tool.testID}
            >
              <Text
                style={[styles.toolIndex, selected && styles.toolIndexSelected]}
              >
                {tool.index}
              </Text>
              <Text
                style={[
                  styles.toolOptionTitle,
                  selected && styles.toolOptionTitleSelected,
                ]}
              >
                {tool.title}
              </Text>
              <Text style={styles.toolOptionSupport}>{tool.support}</Text>
            </Pressable>
          );
        })}
      </View>
      {session.expansionTool === "time" ? renderTime() : null}
      {session.expansionTool === "income" ? renderIncome() : null}
      {session.expansionTool === "reserve" ? renderReserve() : null}
      {session.expansionTool === "complete" ? renderComplete() : null}
    </Surface>
  );
}

const styles = StyleSheet.create({
  panel: { gap: spacing.lg, overflow: "hidden" },
  heading: { gap: spacing.xs },
  title: {
    color: colors.text,
    fontSize: 24,
    fontWeight: "900",
    letterSpacing: -0.5,
    lineHeight: 30,
  },
  support: { color: colors.textMuted, fontSize: 14, lineHeight: 21 },
  privateNote: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.sm,
    color: colors.primaryDark,
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 18,
    padding: spacing.sm,
  },
  toolGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  toolOption: {
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    boxSizing: "border-box",
    flexBasis: 155,
    flexGrow: 1,
    gap: 3,
    minHeight: 96,
    minWidth: 145,
    padding: spacing.sm,
  },
  toolOptionCompact: { flexBasis: 132, minWidth: 126 },
  toolOptionSelected: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
  },
  toolIndex: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1,
  },
  toolIndexSelected: { color: colors.primary },
  toolOptionTitle: { color: colors.text, fontSize: 14, fontWeight: "900" },
  toolOptionTitleSelected: { color: colors.primaryDark },
  toolOptionSupport: { color: colors.textMuted, fontSize: 11, lineHeight: 16 },
  toolBody: {
    borderTopColor: colors.border,
    borderTopWidth: 1,
    gap: spacing.md,
    paddingTop: spacing.lg,
  },
  toolHeading: { gap: spacing.xs },
  toolTitle: {
    color: colors.text,
    fontSize: 21,
    fontWeight: "900",
    letterSpacing: -0.3,
    lineHeight: 27,
  },
  toolSupport: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  fieldGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  field: { flexBasis: 145, flexGrow: 1, gap: spacing.xs, minWidth: 130 },
  fieldLabel: { color: colors.text, fontSize: 13, fontWeight: "800" },
  inputFrame: {
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    flexDirection: "row",
    minHeight: 52,
    overflow: "hidden",
  },
  inputFrameError: { borderColor: colors.danger },
  input: {
    color: colors.text,
    flex: 1,
    fontSize: 16,
    fontVariant: ["tabular-nums"],
    minHeight: 50,
    minWidth: 52,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  inputSuffix: {
    color: colors.textMuted,
    fontSize: 11,
    fontWeight: "800",
    paddingRight: spacing.sm,
  },
  errorText: { color: colors.danger, fontSize: 11, lineHeight: 16 },
  rulerBlock: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.md,
    gap: spacing.md,
    padding: spacing.md,
  },
  rulerHeading: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
    justifyContent: "space-between",
  },
  rulerCopy: { flex: 1, gap: 3, minWidth: 180 },
  rulerHint: { color: colors.textMuted, fontSize: 11, lineHeight: 16 },
  stepper: { alignItems: "center", flexDirection: "row", gap: spacing.xs },
  stepButton: {
    alignItems: "center",
    borderColor: colors.primary,
    borderRadius: radius.sm,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    minWidth: 48,
  },
  stepButtonText: { color: colors.primaryDark, fontSize: 22, fontWeight: "800" },
  stepValue: {
    color: colors.text,
    fontSize: 14,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
    minWidth: 72,
    textAlign: "center",
  },
  disabled: { opacity: 0.38 },
  rulerStops: {
    flexDirection: "row",
    justifyContent: "space-between",
    minHeight: 56,
  },
  rulerStop: {
    alignItems: "center",
    borderRadius: radius.sm,
    flex: 1,
    gap: 4,
    justifyContent: "center",
    minHeight: 48,
    minWidth: 0,
  },
  rulerStopSelected: { backgroundColor: colors.primarySoft },
  rulerDot: {
    backgroundColor: colors.surface,
    borderColor: colors.textMuted,
    borderRadius: radius.pill,
    borderWidth: 2,
    height: 14,
    width: 14,
  },
  rulerDotSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
    borderWidth: 4,
  },
  rulerStopText: {
    color: colors.textMuted,
    fontSize: 10,
    fontVariant: ["tabular-nums"],
    fontWeight: "800",
  },
  rulerStopTextSelected: { color: colors.primaryDark },
  result: { gap: spacing.md },
  resultHero: {
    backgroundColor: colors.primaryDark,
    borderRadius: radius.md,
    gap: spacing.xs,
    padding: spacing.lg,
  },
  resultEyebrow: {
    color: "#C9E8E2",
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1.2,
  },
  resultHeroValue: {
    color: colors.white,
    fontSize: 34,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
    letterSpacing: -1,
    lineHeight: 42,
  },
  resultHeroSupport: { color: "#C9E8E2", fontSize: 12, lineHeight: 18 },
  metrics: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  metric: {
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    flexBasis: 150,
    flexGrow: 1,
    gap: 4,
    minHeight: 76,
    padding: spacing.sm,
  },
  metricEmphasis: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
  },
  metricLabel: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "800",
    lineHeight: 15,
  },
  metricValue: {
    color: colors.text,
    fontSize: 17,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  metricValueEmphasis: { color: colors.primaryDark },
  sectionBlock: { gap: spacing.sm },
  sectionTitle: { color: colors.text, fontSize: 15, fontWeight: "900" },
  milestoneList: { gap: spacing.xs },
  milestoneRow: {
    alignItems: "center",
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    flexDirection: "row",
    gap: spacing.sm,
    minHeight: 64,
    padding: spacing.sm,
  },
  milestoneMark: {
    backgroundColor: colors.gold,
    borderRadius: radius.pill,
    height: 12,
    width: 12,
  },
  milestoneCopy: { flex: 1, gap: 2 },
  milestoneAmount: {
    color: colors.text,
    fontSize: 14,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  milestoneSupport: { color: colors.textMuted, fontSize: 11, lineHeight: 16 },
  choiceBlock: { gap: spacing.xs },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  chip: {
    alignItems: "center",
    borderColor: colors.border,
    borderRadius: radius.pill,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    minWidth: 100,
    paddingHorizontal: spacing.md,
  },
  chipSelected: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
  },
  chipText: { color: colors.textMuted, fontSize: 12, fontWeight: "800" },
  chipTextSelected: { color: colors.primaryDark },
  insightCard: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    gap: spacing.xs,
    padding: spacing.md,
  },
  insightLabel: {
    color: colors.primary,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1,
  },
  insightValue: {
    color: colors.primaryDark,
    fontSize: 23,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
    lineHeight: 29,
  },
  insightText: { color: colors.textMuted, fontSize: 12, lineHeight: 18 },
  inlineNote: {
    backgroundColor: colors.attentionSoft,
    borderRadius: radius.sm,
    color: colors.attention,
    fontSize: 12,
    lineHeight: 18,
    padding: spacing.sm,
  },
  switchRow: {
    alignItems: "center",
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    flexDirection: "row",
    gap: spacing.sm,
    minHeight: 64,
    padding: spacing.sm,
  },
  switchTrack: {
    backgroundColor: colors.neutralSoft,
    borderColor: colors.neutral,
    borderRadius: radius.pill,
    borderWidth: 1,
    height: 28,
    justifyContent: "center",
    paddingHorizontal: 3,
    width: 48,
  },
  switchTrackSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  switchThumb: {
    backgroundColor: colors.neutral,
    borderRadius: radius.pill,
    height: 20,
    width: 20,
  },
  switchThumbSelected: {
    alignSelf: "flex-end",
    backgroundColor: colors.white,
  },
  switchCopy: { flex: 1, gap: 2 },
  switchTitle: { color: colors.text, fontSize: 13, fontWeight: "900" },
  switchSupport: { color: colors.textMuted, fontSize: 11, lineHeight: 16 },
  explainGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  explainCard: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    flexBasis: 160,
    flexGrow: 1,
    gap: 4,
    padding: spacing.sm,
  },
  explainTitle: { color: colors.text, fontSize: 12, fontWeight: "900" },
  explainText: { color: colors.textMuted, fontSize: 11, lineHeight: 17 },
  guardrail: {
    backgroundColor: colors.goldSoft,
    borderColor: "#EBCB91",
    borderRadius: radius.sm,
    borderWidth: 1,
    gap: 4,
    padding: spacing.sm,
  },
  guardrailTitle: { color: colors.text, fontSize: 12, fontWeight: "900" },
  guardrailText: { color: colors.textMuted, fontSize: 11, lineHeight: 17 },
  pressed: { opacity: 0.65 },
});
