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
  calculateRequiredMonthlyContribution,
  ChallengeChoice,
  compareDelayedStart,
  compareIntuitionChallenge,
  CompoundGrowthInput,
  CompoundGrowthProjection,
  ExtraContributionCadence,
  HabitFrequency,
  MONEY_LAB_LIMITS,
  simulateCompoundGrowth,
  simulateHabitRedirect,
} from "../domain/moneyLab";
import { parsePositionAmount } from "../domain/privatePortfolio";
import testIds from "../testing/testIds.json";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, formatCurrency, Surface } from "./Primitives";

export type MoneyLabTool =
  | "growth"
  | "goal"
  | "delay"
  | "habit"
  | "challenge";

export type MoneyLabExpansionTool =
  | "time"
  | "income"
  | "reserve"
  | "complete";

export type MoneyLabSession = {
  tool: MoneyLabTool;
  initialAmountText: string;
  monthlyContributionText: string;
  annualRateText: string;
  yearsText: string;
  inflationRateText: string;
  showInflation: boolean;
  targetAmountText: string;
  delayYears: number;
  habitAmountText: string;
  habitFrequency: HabitFrequency;
  challengeGuess: ChallengeChoice | null;
  expansionTool: MoneyLabExpansionTool;
  bonusAmountText: string;
  bonusCadence: ExtraContributionCadence;
  reserveCurrentText: string;
  reserveExpenseText: string;
  reserveContributionText: string;
  reserveTargetMonths: number;
  showAnnualCost: boolean;
  annualCostText: string;
};

export function createMoneyLabSession(): MoneyLabSession {
  return {
    tool: "growth",
    initialAmountText: "1000",
    monthlyContributionText: "300",
    annualRateText: "10",
    yearsText: "10",
    inflationRateText: "4,5",
    showInflation: false,
    targetAmountText: "50000",
    delayYears: 3,
    habitAmountText: "15",
    habitFrequency: "daily",
    challengeGuess: null,
    expansionTool: "time",
    bonusAmountText: "2000",
    bonusCadence: "today",
    reserveCurrentText: "6000",
    reserveExpenseText: "3000",
    reserveContributionText: "750",
    reserveTargetMonths: 6,
    showAnnualCost: false,
    annualCostText: "1",
  };
}

type FieldKey =
  | "initial"
  | "monthly"
  | "rate"
  | "years"
  | "inflation"
  | "target"
  | "habit";
type FieldErrors = Partial<Record<FieldKey, string>>;

const tools: readonly {
  key: MoneyLabTool;
  index: string;
  title: string;
  support: string;
  testID: string;
}[] = [
  {
    key: "growth",
    index: "01",
    title: "Quanto vira?",
    support: "Valor, aporte, taxa e tempo.",
    testID: testIds.moneyLab.tools.growth,
  },
  {
    key: "goal",
    index: "02",
    title: "Quanto guardar?",
    support: "Comece pela meta desejada.",
    testID: testIds.moneyLab.tools.goal,
  },
  {
    key: "delay",
    index: "03",
    title: "E se eu esperar?",
    support: "Compare começar agora ou depois.",
    testID: testIds.moneyLab.tools.delay,
  },
  {
    key: "habit",
    index: "04",
    title: "Um hábito no tempo",
    support: "Converta recorrência sem julgamento.",
    testID: testIds.moneyLab.tools.habit,
  },
  {
    key: "challenge",
    index: "05",
    title: "O que pesa mais?",
    support: "Dê um palpite antes da conta.",
    testID: testIds.moneyLab.tools.challenge,
  },
];

const frequencyLabels: Record<HabitFrequency, string> = {
  daily: "por dia",
  weekly: "por semana",
  monthly: "por mês",
};

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
  const maximumRate =
    session.tool === "challenge"
      ? MONEY_LAB_LIMITS.maxAnnualRatePercent - 1
      : MONEY_LAB_LIMITS.maxAnnualRatePercent;

  if (initialAmount === null) {
    errors.initial = "Use um valor entre zero e R$ 999 bilhões.";
  }
  if (monthlyContribution === null) {
    errors.monthly = "Use um aporte mensal válido, inclusive zero.";
  }
  if (
    annualRatePercent === null ||
    annualRatePercent < 0 ||
    annualRatePercent > maximumRate
  ) {
    errors.rate =
      session.tool === "challenge"
        ? "Use uma taxa entre 0% e 199% para comparar mais 1 p.p."
        : "Use uma taxa entre 0% e 200% ao ano.";
  }
  if (
    years === null ||
    years < 1 ||
    years > MONEY_LAB_LIMITS.maxYears
  ) {
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

function formatPercent(value: number): string {
  return value.toFixed(1).replace(".", ",") + "%";
}

function formatYear(year: number): string {
  return String(year) + " " + (year === 1 ? "ano" : "anos");
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

function ProjectionTimeline({
  hidden,
  projection,
}: {
  hidden: boolean;
  projection: CompoundGrowthProjection;
}) {
  const maxValue = projection.futureValue || 1;
  return (
    <View style={styles.timeline}>
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendMark, styles.legendContributed]} />
          <Text style={styles.legendText}>Colocado por você</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendMark, styles.legendInterest]} />
          <Text style={styles.legendText}>Juros do cenário</Text>
        </View>
      </View>
      {projection.timeline.map((point) => {
        const contributionRatio = point.totalContributed / maxValue;
        const interestRatio = point.interestEarned / maxValue;
        const remainder = Math.max(
          0,
          1 - contributionRatio - interestRatio,
        );
        const accessibilityLabel =
          formatYear(point.year) +
          ": " +
          formatCurrency(point.futureValue, hidden) +
          ", sendo " +
          formatCurrency(point.totalContributed, hidden) +
          " colocados e " +
          formatCurrency(point.interestEarned, hidden) +
          " de juros no cenário";
        return (
          <View
            accessibilityLabel={accessibilityLabel}
            accessible
            key={point.year}
            style={styles.timelineRow}
          >
            <View style={styles.timelineLabels}>
              <Text style={styles.timelineYear}>{formatYear(point.year)}</Text>
              <Text style={styles.timelineValue}>
                {formatCurrency(point.futureValue, hidden)}
              </Text>
            </View>
            <View style={styles.timelineTrack}>
              <View
                style={[
                  styles.timelineSegment,
                  styles.timelineContributed,
                  { flex: contributionRatio },
                ]}
              />
              <View
                style={[
                  styles.timelineSegment,
                  styles.timelineInterest,
                  { flex: interestRatio },
                ]}
              />
              <View style={{ flex: remainder }} />
            </View>
          </View>
        );
      })}
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

export function MoneyLabPanel({
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
  const wide = width >= 700;
  const [touched, setTouched] = useState<Partial<Record<FieldKey, boolean>>>({});
  const { input: growthInput, errors: growthErrors } =
    resolveGrowthInput(session);

  function patch(values: Partial<MoneyLabSession>) {
    onSessionChange({ ...session, ...values });
  }

  function patchGrowth(values: Partial<MoneyLabSession>) {
    patch({ ...values, challengeGuess: null });
  }

  function touch(field: FieldKey) {
    setTouched((current) => ({ ...current, [field]: true }));
  }

  function visibleError(field: FieldKey, error?: string) {
    return touched[field] ? error : undefined;
  }

  function renderCommonFields(includeMonthly = true) {
    return (
      <View style={styles.fieldGrid}>
        <NumericField
          error={visibleError("initial", growthErrors.initial)}
          hiddenAmount={hideAmounts}
          label="Valor inicial"
          onBlur={() => touch("initial")}
          onChangeText={(value) => patchGrowth({ initialAmountText: value })}
          suffix="R$"
          testID={testIds.moneyLab.initialInput}
          value={session.initialAmountText}
        />
        {includeMonthly ? (
          <NumericField
            error={visibleError("monthly", growthErrors.monthly)}
            hiddenAmount={hideAmounts}
            label="Aporte mensal"
            onBlur={() => touch("monthly")}
            onChangeText={(value) =>
              patchGrowth({ monthlyContributionText: value })
            }
            suffix="R$"
            testID={testIds.moneyLab.monthlyInput}
            value={session.monthlyContributionText}
          />
        ) : null}
        <NumericField
          error={visibleError("rate", growthErrors.rate)}
          label="Taxa efetiva anual"
          onBlur={() => touch("rate")}
          onChangeText={(value) => patchGrowth({ annualRateText: value })}
          suffix="% a.a."
          testID={testIds.moneyLab.rateInput}
          value={session.annualRateText}
        />
        <NumericField
          error={visibleError("years", growthErrors.years)}
          label="Prazo"
          onBlur={() => touch("years")}
          onChangeText={(value) => patchGrowth({ yearsText: value })}
          suffix="anos"
          testID={testIds.moneyLab.yearsInput}
          value={session.yearsText}
        />
      </View>
    );
  }

  function renderGrowth() {
    const projection = growthInput
      ? simulateCompoundGrowth(growthInput)
      : null;
    const inflationRate = parseLocalizedNumber(session.inflationRateText);
    const inflationError =
      session.showInflation &&
      (inflationRate === null ||
        inflationRate < 0 ||
        inflationRate > MONEY_LAB_LIMITS.maxAnnualRatePercent)
        ? "Use uma inflação entre 0% e 200% ao ano."
        : undefined;
    const presentValue =
      projection && session.showInflation && !inflationError
        ? adjustForInflation(
            projection.futureValue,
            inflationRate!,
            growthInput!.years,
          )
        : null;
    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>Juros compostos</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            Quanto este dinheiro pode virar?
          </Text>
          <Text style={styles.toolSupport}>
            Exemplo fictício e editável. A conta muda enquanto você digita.
          </Text>
        </View>
        {renderCommonFields()}
        <Pressable
          accessibilityRole="switch"
          accessibilityState={{ checked: session.showInflation }}
          onPress={() => patch({ showInflation: !session.showInflation })}
          style={({ pressed }) => [
            styles.switchRow,
            pressed && styles.pressed,
          ]}
          testID={testIds.moneyLab.inflationToggle}
        >
          <View
            style={[
              styles.switchTrack,
              session.showInflation && styles.switchTrackSelected,
            ]}
          >
            <View
              style={[
                styles.switchThumb,
                session.showInflation && styles.switchThumbSelected,
              ]}
            />
          </View>
          <View style={styles.switchCopy}>
            <Text style={styles.switchTitle}>Traduzir para dinheiro de hoje</Text>
            <Text style={styles.switchSupport}>
              Acrescenta inflação sem alterar o cenário nominal.
            </Text>
          </View>
        </Pressable>
        {session.showInflation ? (
          <NumericField
            error={visibleError("inflation", inflationError)}
            label="Inflação anual hipotética"
            onBlur={() => touch("inflation")}
            onChangeText={(value) => patch({ inflationRateText: value })}
            suffix="% a.a."
            testID={testIds.moneyLab.inflationInput}
            value={session.inflationRateText}
          />
        ) : null}
        {projection ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>NO FIM DO CENÁRIO</Text>
              <Text style={styles.resultHeroValue}>
                {formatCurrency(projection.futureValue, hideAmounts)}
              </Text>
              <Text style={styles.resultHeroSupport}>
                taxa fixa de {formatPercent(growthInput!.annualRatePercent)} por{" "}
                {formatYear(growthInput!.years)}
              </Text>
            </View>
            <View style={styles.metrics}>
              <Metric
                label="Colocado por você"
                value={formatCurrency(projection.totalContributed, hideAmounts)}
              />
              <Metric
                emphasis
                label="Juros do cenário"
                value={formatCurrency(projection.interestEarned, hideAmounts)}
              />
              {presentValue !== null ? (
                <Metric
                  label="Em dinheiro de hoje"
                  value={formatCurrency(presentValue, hideAmounts)}
                />
              ) : null}
            </View>
            <ProjectionTimeline hidden={hideAmounts} projection={projection} />
            <ResultGuardrail>
              A taxa foi mantida constante só para a matemática funcionar. O
              resultado não prevê mercado, imposto, taxa de produto ou poder de
              compra quando a inflação estiver desligada.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderGoal() {
    const targetAmount = parseMoney(session.targetAmountText, false);
    const initialAmount = parseMoney(session.initialAmountText, true);
    const annualRatePercent = parseLocalizedNumber(session.annualRateText);
    const years = parseYears(session.yearsText);
    const targetError =
      targetAmount === null ? "Informe uma meta positiva válida." : undefined;
    const initialError =
      initialAmount === null
        ? "Use um valor entre zero e R$ 999 bilhões."
        : undefined;
    const rateError =
      annualRatePercent === null ||
      annualRatePercent < 0 ||
      annualRatePercent > MONEY_LAB_LIMITS.maxAnnualRatePercent
        ? "Use uma taxa entre 0% e 200% ao ano."
        : undefined;
    const yearsError =
      years === null || years < 1 || years > MONEY_LAB_LIMITS.maxYears
        ? "Use um prazo entre 1 e 50 anos inteiros."
        : undefined;
    const result =
      targetAmount !== null &&
      initialAmount !== null &&
      !rateError &&
      !yearsError
        ? calculateRequiredMonthlyContribution({
            targetAmount,
            initialAmount,
            annualRatePercent: annualRatePercent!,
            years: years!,
          })
        : null;
    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>Meta ao contrário</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            Quanto eu precisaria guardar por mês?
          </Text>
          <Text style={styles.toolSupport}>
            Escolha a meta; a conta encontra o aporte mensal do cenário.
          </Text>
        </View>
        <View style={styles.fieldGrid}>
          <NumericField
            error={visibleError("target", targetError)}
            hiddenAmount={hideAmounts}
            label="Meta desejada"
            onBlur={() => touch("target")}
            onChangeText={(value) => patch({ targetAmountText: value })}
            suffix="R$"
            testID={testIds.moneyLab.targetInput}
            value={session.targetAmountText}
          />
          <NumericField
            error={visibleError("initial", initialError)}
            hiddenAmount={hideAmounts}
            label="Valor inicial"
            onBlur={() => touch("initial")}
            onChangeText={(value) => patchGrowth({ initialAmountText: value })}
            suffix="R$"
            testID={testIds.moneyLab.initialInput}
            value={session.initialAmountText}
          />
          <NumericField
            error={visibleError("rate", rateError)}
            label="Taxa efetiva anual"
            onBlur={() => touch("rate")}
            onChangeText={(value) => patchGrowth({ annualRateText: value })}
            suffix="% a.a."
            testID={testIds.moneyLab.rateInput}
            value={session.annualRateText}
          />
          <NumericField
            error={visibleError("years", yearsError)}
            label="Prazo"
            onBlur={() => touch("years")}
            onChangeText={(value) => patchGrowth({ yearsText: value })}
            suffix="anos"
            testID={testIds.moneyLab.yearsInput}
            value={session.yearsText}
          />
        </View>
        {result ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>
                {result.targetMetByInitial
                  ? "O VALOR INICIAL JÁ ALCANÇARIA A META"
                  : "APORTE MENSAL DO CENÁRIO"}
              </Text>
              <Text style={styles.resultHeroValue}>
                {formatCurrency(result.monthlyContribution, hideAmounts)}
              </Text>
              <Text style={styles.resultHeroSupport}>
                para buscar {formatCurrency(result.targetAmount, hideAmounts)} em{" "}
                {formatYear(years!)}
              </Text>
            </View>
            <View style={styles.metrics}>
              <Metric
                label="Total colocado"
                value={formatCurrency(result.totalContributed, hideAmounts)}
              />
              <Metric
                emphasis
                label="Juros necessários no cenário"
                value={formatCurrency(result.interestEarned, hideAmounts)}
              />
            </View>
            <ResultGuardrail>
              O aporte é consequência da taxa fixa informada. Ele não é plano
              financeiro, garantia de meta ou indicação de investimento.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderDelay() {
    const availableDelays = [1, 3, 5].filter(
      (delay) => growthInput && delay < growthInput.years,
    );
    const effectiveDelay = availableDelays.includes(session.delayYears)
      ? session.delayYears
      : availableDelays[0];
    const comparison =
      growthInput && effectiveDelay
        ? compareDelayedStart(growthInput, effectiveDelay)
        : null;
    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>O preço de esperar</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            E se eu começar mais tarde?
          </Text>
          <Text style={styles.toolSupport}>
            O valor inicial fica parado durante a espera; nenhum aporte é feito.
          </Text>
        </View>
        {renderCommonFields()}
        {availableDelays.length ? (
          <View style={styles.choiceBlock}>
            <Text style={styles.fieldLabel}>Tempo de espera</Text>
            <View accessibilityRole="radiogroup" style={styles.chipRow}>
              {availableDelays.map((delay) => {
                const selected = delay === effectiveDelay;
                return (
                  <Pressable
                    accessibilityRole="radio"
                    accessibilityState={{ selected }}
                    key={delay}
                    onPress={() => patch({ delayYears: delay })}
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
                      {formatYear(delay)}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
        ) : (
          <Text style={styles.inlineNote}>
            Use um prazo total de pelo menos dois anos para comparar a espera.
          </Text>
        )}
        {comparison ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.result}
          >
            <View style={styles.comparisonGrid}>
              <Metric
                emphasis
                label="Começando agora"
                value={formatCurrency(
                  comparison.startNow.futureValue,
                  hideAmounts,
                )}
              />
              <Metric
                label={"Esperando " + formatYear(comparison.delayYears)}
                value={formatCurrency(
                  comparison.startLater.futureValue,
                  hideAmounts,
                )}
              />
            </View>
            <View style={styles.insightCard}>
              <Text style={styles.insightLabel}>DIFERENÇA NO FIM</Text>
              <Text style={styles.insightValue}>
                {formatCurrency(comparison.difference, hideAmounts)}
              </Text>
              <Text style={styles.insightText}>
                A espera também pula{" "}
                {formatCurrency(comparison.contributionsSkipped, hideAmounts)} em
                aportes. O restante vem do tempo menor de capitalização.
              </Text>
            </View>
            <ResultGuardrail>
              Esta comparação isola somente tempo, aporte e taxa fixa. Não
              considera imprevistos, renda disponível ou mudanças de taxa.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderHabit() {
    const amount = parseMoney(session.habitAmountText, false);
    const rate = parseLocalizedNumber(session.annualRateText);
    const years = parseYears(session.yearsText);
    const habitError =
      amount === null ? "Informe um valor recorrente positivo." : undefined;
    const rateError =
      rate === null ||
      rate < 0 ||
      rate > MONEY_LAB_LIMITS.maxAnnualRatePercent
        ? "Use uma taxa entre 0% e 200% ao ano."
        : undefined;
    const yearsError =
      years === null || years < 1 || years > MONEY_LAB_LIMITS.maxYears
        ? "Use um prazo entre 1 e 50 anos inteiros."
        : undefined;
    const result =
      amount !== null && !rateError && !yearsError
        ? simulateHabitRedirect({
            amountPerOccurrence: amount,
            frequency: session.habitFrequency,
            annualRatePercent: rate!,
            years: years!,
          })
        : null;
    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>Transformador de hábitos</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            Quanto uma recorrência representa no tempo?
          </Text>
          <Text style={styles.toolSupport}>
            Você decide o que simular. O app não chama gasto de certo ou errado.
          </Text>
        </View>
        <View style={styles.fieldGrid}>
          <NumericField
            error={visibleError("habit", habitError)}
            hiddenAmount={hideAmounts}
            label="Valor recorrente"
            onBlur={() => touch("habit")}
            onChangeText={(value) => patch({ habitAmountText: value })}
            suffix="R$"
            testID={testIds.moneyLab.habitInput}
            value={session.habitAmountText}
          />
          <NumericField
            error={visibleError("rate", rateError)}
            label="Taxa efetiva anual"
            onBlur={() => touch("rate")}
            onChangeText={(value) => patchGrowth({ annualRateText: value })}
            suffix="% a.a."
            testID={testIds.moneyLab.rateInput}
            value={session.annualRateText}
          />
          <NumericField
            error={visibleError("years", yearsError)}
            label="Prazo"
            onBlur={() => touch("years")}
            onChangeText={(value) => patchGrowth({ yearsText: value })}
            suffix="anos"
            testID={testIds.moneyLab.yearsInput}
            value={session.yearsText}
          />
        </View>
        <View style={styles.choiceBlock}>
          <Text style={styles.fieldLabel}>Frequência</Text>
          <View accessibilityRole="radiogroup" style={styles.chipRow}>
            {(Object.keys(frequencyLabels) as HabitFrequency[]).map(
              (frequency) => {
                const selected = frequency === session.habitFrequency;
                return (
                  <Pressable
                    accessibilityRole="radio"
                    accessibilityState={{ selected }}
                    key={frequency}
                    onPress={() => patch({ habitFrequency: frequency })}
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
                      {frequencyLabels[frequency]}
                    </Text>
                  </Pressable>
                );
              },
            )}
          </View>
        </View>
        {result ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>EQUIVALENTE MÉDIO POR MÊS</Text>
              <Text style={styles.resultHeroValue}>
                {formatCurrency(result.monthlyEquivalent, hideAmounts)}
              </Text>
              <Text style={styles.resultHeroSupport}>
                média de 365 dias ou 52 semanas por ano
              </Text>
            </View>
            <View style={styles.metrics}>
              <Metric
                label="Total redirecionado"
                value={formatCurrency(result.totalDirected, hideAmounts)}
              />
              <Metric
                emphasis
                label="Valor final no cenário"
                value={formatCurrency(result.futureValue, hideAmounts)}
              />
              <Metric
                label="Juros do cenário"
                value={formatCurrency(result.interestEarned, hideAmounts)}
              />
            </View>
            <ResultGuardrail>
              A conta não sugere cortar o hábito. Ela apenas traduz uma escolha
              hipotética recorrente para a mesma taxa fixa do laboratório.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderChallenge() {
    const challenge = growthInput
      ? compareIntuitionChallenge(growthInput)
      : null;
    const revealed = challenge && session.challengeGuess;
    const winnerLabel =
      challenge?.winner === "rate"
        ? "+1 p.p. de taxa"
        : challenge?.winner === "contribution"
          ? "+R$ 150 por mês"
          : "as duas mudanças";
    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>Desafio de intuição</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            O que acrescenta mais ao valor final?
          </Text>
          <Text style={styles.toolSupport}>
            Use o mesmo cenário-base e dê seu palpite antes de revelar.
          </Text>
        </View>
        {renderCommonFields()}
        {challenge ? (
          <View style={styles.guessBlock}>
            <Text style={styles.guessQuestion}>
              Qual mudança pesa mais em {formatYear(growthInput!.years)}?
            </Text>
            <View style={styles.guessButtons}>
              <Pressable
                accessibilityRole="button"
                onPress={() => patch({ challengeGuess: "rate" })}
                style={({ pressed }) => [
                  styles.guessButton,
                  session.challengeGuess === "rate" &&
                    styles.guessButtonSelected,
                  pressed && styles.pressed,
                ]}
                testID={testIds.moneyLab.guessRate}
              >
                <Text style={styles.guessButtonTitle}>+1 p.p. de taxa</Text>
                <Text style={styles.guessButtonSupport}>
                  {formatPercent(growthInput!.annualRatePercent)} para{" "}
                  {formatPercent(growthInput!.annualRatePercent + 1)} a.a.
                </Text>
              </Pressable>
              <Pressable
                accessibilityRole="button"
                onPress={() => patch({ challengeGuess: "contribution" })}
                style={({ pressed }) => [
                  styles.guessButton,
                  session.challengeGuess === "contribution" &&
                    styles.guessButtonSelected,
                  pressed && styles.pressed,
                ]}
                testID={testIds.moneyLab.guessContribution}
              >
                <Text style={styles.guessButtonTitle}>+R$ 150 por mês</Text>
                <Text style={styles.guessButtonSupport}>
                  mantém a taxa e aumenta somente o aporte
                </Text>
              </Pressable>
            </View>
          </View>
        ) : null}
        {revealed ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.challengeResult}
          >
            <View style={styles.insightCard}>
              <Text style={styles.insightLabel}>NESTE CENÁRIO, PESOU MAIS</Text>
              <Text style={styles.insightValue}>{winnerLabel}</Text>
              <Text style={styles.insightText}>
                Seu palpite foi{" "}
                {session.challengeGuess === challenge.winner
                  ? "igual ao resultado."
                  : "diferente do resultado — e essa é a graça do teste."}
              </Text>
            </View>
            <View style={styles.comparisonGrid}>
              <Metric
                label="Ganho com +1 p.p."
                value={formatCurrency(challenge.rateGain, hideAmounts)}
              />
              <Metric
                label="Ganho com +R$ 150/mês"
                value={formatCurrency(challenge.contributionGain, hideAmounts)}
              />
            </View>
            <Pressable
              accessibilityRole="button"
              onPress={() => patch({ challengeGuess: null })}
              style={({ pressed }) => [
                styles.secondaryButton,
                pressed && styles.pressed,
              ]}
            >
              <Text style={styles.secondaryButtonText}>Dar outro palpite</Text>
            </Pressable>
            <ResultGuardrail>
              O vencedor muda conforme valor, aporte e prazo. A comparação não
              diz que buscar mais taxa é possível, adequado ou preferível.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  return (
    <Surface style={styles.panel} testID={testIds.moneyLab.panel}>
      <View style={styles.heading}>
        <Eyebrow>Laboratório do dinheiro</Eyebrow>
        <Text accessibilityRole="header" style={styles.title}>
          Brinque com números antes de olhar produtos
        </Text>
        <Text style={styles.support}>
          Cinco perguntas rápidas, sempre locais. Os valores ficam apenas na
          sessão e não tocam sua carteira.
        </Text>
        {hideAmounts ? (
          <Text style={styles.privateNote}>
            Modo discreto ativo: entradas e resultados monetários estão ocultos.
          </Text>
        ) : null}
      </View>

      <View accessibilityRole="radiogroup" style={styles.toolGrid}>
        {tools.map((tool) => {
          const selected = tool.key === session.tool;
          return (
            <Pressable
              accessibilityLabel={tool.title + " " + tool.support}
              accessibilityRole="radio"
              accessibilityState={{ selected }}
              key={tool.key}
              onPress={() => patch({ tool: tool.key })}
              style={({ pressed }) => [
                styles.toolOption,
                compact && styles.toolOptionCompact,
                wide && styles.toolOptionWide,
                selected && styles.toolOptionSelected,
                pressed && styles.pressed,
              ]}
              testID={tool.testID}
            >
              <Text
                style={[
                  styles.toolIndex,
                  selected && styles.toolIndexSelected,
                ]}
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

      {session.tool === "growth" ? renderGrowth() : null}
      {session.tool === "goal" ? renderGoal() : null}
      {session.tool === "delay" ? renderDelay() : null}
      {session.tool === "habit" ? renderHabit() : null}
      {session.tool === "challenge" ? renderChallenge() : null}
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
    flexBasis: 150,
    flexGrow: 1,
    gap: 3,
    minHeight: 96,
    minWidth: 140,
    padding: spacing.sm,
  },
  toolOptionCompact: { flexBasis: 132, minWidth: 126 },
  toolOptionWide: { flexBasis: 118, minWidth: 116 },
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
  comparisonGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
  },
  metric: {
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    flexBasis: 150,
    flexGrow: 1,
    gap: 4,
    minHeight: 72,
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
  timeline: { gap: spacing.sm },
  legend: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  legendItem: {
    alignItems: "center",
    flexDirection: "row",
    gap: spacing.xs,
  },
  legendMark: { borderRadius: 2, height: 8, width: 16 },
  legendContributed: { backgroundColor: colors.primary },
  legendInterest: { backgroundColor: colors.gold },
  legendText: { color: colors.textMuted, fontSize: 11, fontWeight: "700" },
  timelineRow: { gap: spacing.xs },
  timelineLabels: {
    flexDirection: "row",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  timelineYear: { color: colors.text, fontSize: 11, fontWeight: "800" },
  timelineValue: {
    color: colors.textMuted,
    fontSize: 11,
    fontVariant: ["tabular-nums"],
  },
  timelineTrack: {
    backgroundColor: colors.neutralSoft,
    borderRadius: radius.pill,
    flexDirection: "row",
    height: 12,
    overflow: "hidden",
  },
  timelineSegment: { minWidth: 0 },
  timelineContributed: { backgroundColor: colors.primary },
  timelineInterest: { backgroundColor: colors.gold },
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
  choiceBlock: { gap: spacing.xs },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  chip: {
    alignItems: "center",
    borderColor: colors.border,
    borderRadius: radius.pill,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    minWidth: 92,
    paddingHorizontal: spacing.md,
  },
  chipSelected: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
  },
  chipText: { color: colors.textMuted, fontSize: 12, fontWeight: "800" },
  chipTextSelected: { color: colors.primaryDark },
  inlineNote: {
    backgroundColor: colors.attentionSoft,
    borderRadius: radius.sm,
    color: colors.attention,
    fontSize: 12,
    lineHeight: 18,
    padding: spacing.sm,
  },
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
  guessBlock: { gap: spacing.sm },
  guessQuestion: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "900",
    lineHeight: 21,
  },
  guessButtons: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  guessButton: {
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    flexBasis: 170,
    flexGrow: 1,
    gap: 4,
    minHeight: 72,
    padding: spacing.sm,
  },
  guessButtonSelected: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
  },
  guessButtonTitle: { color: colors.text, fontSize: 14, fontWeight: "900" },
  guessButtonSupport: {
    color: colors.textMuted,
    fontSize: 11,
    lineHeight: 16,
  },
  secondaryButton: {
    alignItems: "center",
    borderColor: colors.primary,
    borderRadius: radius.sm,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  secondaryButtonText: {
    color: colors.primaryDark,
    fontSize: 13,
    fontWeight: "900",
  },
  pressed: { opacity: 0.65 },
});
