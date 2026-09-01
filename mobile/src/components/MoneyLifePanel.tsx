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
  compareCashAndInstallments,
  CompoundGrowthInput,
  MONEY_LAB_LIMITS,
  simulateFlexibleContributionPlan,
  simulateWithdrawalLongevity,
} from "../domain/moneyLab";
import { parsePositionAmount } from "../domain/privatePortfolio";
import testIds from "../testing/testIds.json";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, formatCurrency, Surface } from "./Primitives";
import { MoneyLabSession, MoneyLifeTool } from "./MoneyLabPanel";

type FieldKey =
  | "initial"
  | "monthly"
  | "rate"
  | "years"
  | "increase"
  | "cash"
  | "installment"
  | "withdrawalInitial"
  | "withdrawalMonthly"
  | "withdrawalRate"
  | "withdrawalYears"
  | "withdrawalInflation";

type FieldErrors = Partial<Record<FieldKey, string>>;

const tools: readonly {
  key: MoneyLifeTool;
  index: string;
  title: string;
  support: string;
  testID: string;
}[] = [
  {
    key: "flexible",
    index: "10",
    title: "A vida acontece",
    support: "Aporte crescente e uma pausa no caminho.",
    testID: testIds.moneyLab.life.tools.flexible,
  },
  {
    key: "installments",
    index: "11",
    title: "Parcelado sem mistério",
    support: "Preço à vista, total e custo implícito.",
    testID: testIds.moneyLab.life.tools.installments,
  },
  {
    key: "longevity",
    index: "12",
    title: "Quanto tempo dura?",
    support: "Retiradas, rendimento e inflação.",
    testID: testIds.moneyLab.life.tools.longevity,
  },
];

const pauseOptions = [0, 3, 6, 12] as const;
const installmentOptions = [3, 6, 12, 24] as const;

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
  return `${value.toFixed(digits).replace(".", ",")}%`;
}

function formatSignedCurrency(value: number, hidden: boolean): string {
  if (hidden || Math.abs(value) < 0.005) {
    return formatCurrency(Math.abs(value), hidden);
  }
  return `${value > 0 ? "+" : "−"}${formatCurrency(Math.abs(value), false)}`;
}

function formatDuration(months: number): string {
  const years = Math.floor(months / 12);
  const remainingMonths = months % 12;
  const parts: string[] = [];
  if (years > 0) {
    parts.push(`${years} ${years === 1 ? "ano" : "anos"}`);
  }
  if (remainingMonths > 0) {
    parts.push(
      `${remainingMonths} ${remainingMonths === 1 ? "mês" : "meses"}`,
    );
  }
  return parts.join(" e ") || "menos de um mês";
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

export function MoneyLifePanel({
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

  function renderCommonFields() {
    return (
      <View style={styles.fieldGrid}>
        <NumericField
          error={visibleError("initial", growthErrors.initial)}
          hiddenAmount={hideAmounts}
          label="Valor inicial"
          onBlur={() => touch("initial")}
          onChangeText={(value) => patch({ initialAmountText: value })}
          suffix="R$"
          testID={testIds.moneyLab.life.initialInput}
          value={session.initialAmountText}
        />
        <NumericField
          error={visibleError("monthly", growthErrors.monthly)}
          hiddenAmount={hideAmounts}
          label="Aporte mensal inicial"
          onBlur={() => touch("monthly")}
          onChangeText={(value) => patch({ monthlyContributionText: value })}
          suffix="R$"
          testID={testIds.moneyLab.life.monthlyInput}
          value={session.monthlyContributionText}
        />
        <NumericField
          error={visibleError("rate", growthErrors.rate)}
          label="Taxa efetiva anual"
          onBlur={() => touch("rate")}
          onChangeText={(value) => patch({ annualRateText: value })}
          suffix="% a.a."
          testID={testIds.moneyLab.life.rateInput}
          value={session.annualRateText}
        />
        <NumericField
          error={visibleError("years", growthErrors.years)}
          label="Prazo"
          onBlur={() => touch("years")}
          onChangeText={(value) => patch({ yearsText: value })}
          suffix="anos"
          testID={testIds.moneyLab.life.yearsInput}
          value={session.yearsText}
        />
      </View>
    );
  }

  function renderFlexible() {
    const annualIncrease = parseLocalizedNumber(
      session.annualContributionIncreaseText,
    );
    const increaseError =
      annualIncrease === null || annualIncrease < 0 || annualIncrease > 200
        ? "Use um aumento entre 0% e 200% ao ano."
        : undefined;
    const pauseStartMonth = growthInput
      ? Math.floor((growthInput.years * 12) / 2) + 1
      : 1;
    const result =
      growthInput && !increaseError
        ? simulateFlexibleContributionPlan({
            input: growthInput,
            annualIncreasePercent: annualIncrease!,
            pauseStartMonth,
            pauseMonths: session.pauseMonths,
          })
        : null;

    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>v0.6.2 · Plano que respira</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            E se meu aporte crescer e depois precisar parar?
          </Text>
          <Text style={styles.toolSupport}>
            Compare o aporte fixo com um aumento anual e uma pausa no meio do
            prazo. A pausa não vira dívida nem é reposta automaticamente.
          </Text>
        </View>
        {renderCommonFields()}
        <NumericField
          error={visibleError("increase", increaseError)}
          label="Aumento do aporte a cada ano"
          onBlur={() => touch("increase")}
          onChangeText={(value) =>
            patch({ annualContributionIncreaseText: value })
          }
          suffix="% a.a."
          testID={testIds.moneyLab.life.increaseInput}
          value={session.annualContributionIncreaseText}
        />
        <View style={styles.choiceBlock}>
          <Text style={styles.fieldLabel}>Pausa no meio do caminho</Text>
          <Text style={styles.choiceSupport}>
            Escolha por quantos meses o aporte fica zerado.
          </Text>
          <View accessibilityRole="radiogroup" style={styles.chipRow}>
            {pauseOptions.map((months) => {
              const selected = session.pauseMonths === months;
              const label = months === 0 ? "Sem pausa" : `${months} meses`;
              return (
                <Pressable
                  accessibilityLabel={label}
                  accessibilityRole="radio"
                  accessibilityState={{ selected }}
                  key={months}
                  onPress={() => patch({ pauseMonths: months })}
                  style={({ pressed }) => [
                    styles.chip,
                    selected && styles.chipSelected,
                    pressed && styles.pressed,
                  ]}
                >
                  <Text style={[styles.chipText, selected && styles.chipTextSelected]}>
                    {label}
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
            testID={testIds.moneyLab.life.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>COM O PLANO FLEXÍVEL</Text>
              <Text style={styles.resultHeroValue}>
                {formatCurrency(result.flexible.futureValue, hideAmounts)}
              </Text>
              <Text style={styles.resultHeroSupport}>
                {formatPercent(result.annualIncreasePercent)} de aumento anual e{" "}
                {result.pauseMonths === 0
                  ? "sem pausa"
                  : `${result.pauseMonths} meses sem aporte no meio do prazo`}
              </Text>
            </View>
            <View style={styles.metrics}>
              <Metric
                label="Com aporte fixo"
                value={formatCurrency(result.base.futureValue, hideAmounts)}
              />
              <Metric
                emphasis
                label="Diferença mecânica"
                value={formatSignedCurrency(result.difference, hideAmounts)}
              />
              <Metric
                label="Total colocado"
                value={formatCurrency(result.flexible.totalContributed, hideAmounts)}
              />
              <Metric
                label="Aportes pulados"
                value={formatCurrency(result.skippedContributions, hideAmounts)}
              />
              <Metric
                label="Aporte mensal no último ano"
                value={formatCurrency(
                  result.finalScheduledMonthlyContribution,
                  hideAmounts,
                )}
              />
              <Metric
                label="Juros do cenário"
                value={formatCurrency(result.flexible.interestEarned, hideAmounts)}
              />
            </View>
            <Text style={styles.inlineNote}>
              A pausa começa aproximadamente na metade do prazo. O aumento anual
              continua no calendário mesmo durante a pausa.
            </Text>
            <ResultGuardrail>
              Renda, imprevistos e capacidade de aporte não são previstos. A
              taxa fixa, os aumentos e a pausa são hipóteses editáveis, não um
              plano financeiro ou promessa de resultado.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderInstallments() {
    const cashPrice = parseMoney(session.cashPriceText, false);
    const installmentAmount = parseMoney(
      session.installmentAmountText,
      false,
    );
    const cashError =
      cashPrice === null ? "Informe um preço à vista positivo." : undefined;
    const installmentError =
      installmentAmount === null
        ? "Informe o valor positivo de cada parcela."
        : undefined;
    const result =
      cashPrice !== null && installmentAmount !== null
        ? compareCashAndInstallments({
            cashPrice,
            installmentAmount,
            installmentCount: session.installmentCount,
          })
        : null;

    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>v0.6.3 · Compra em partes</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            Quanto o parcelamento soma de verdade?
          </Text>
          <Text style={styles.toolSupport}>
            Digite os dois preços. O app soma as parcelas e, quando elas custam
            mais, estima a taxa implícita supondo a primeira em um mês.
          </Text>
        </View>
        <View style={styles.fieldGrid}>
          <NumericField
            error={visibleError("cash", cashError)}
            hiddenAmount={hideAmounts}
            label="Preço à vista"
            onBlur={() => touch("cash")}
            onChangeText={(value) => patch({ cashPriceText: value })}
            suffix="R$"
            testID={testIds.moneyLab.life.cashInput}
            value={session.cashPriceText}
          />
          <NumericField
            error={visibleError("installment", installmentError)}
            hiddenAmount={hideAmounts}
            label="Valor de cada parcela"
            onBlur={() => touch("installment")}
            onChangeText={(value) => patch({ installmentAmountText: value })}
            suffix="R$"
            testID={testIds.moneyLab.life.installmentInput}
            value={session.installmentAmountText}
          />
        </View>
        <View style={styles.choiceBlock}>
          <Text style={styles.fieldLabel}>Quantidade de parcelas</Text>
          <View accessibilityRole="radiogroup" style={styles.chipRow}>
            {installmentOptions.map((count) => {
              const selected = session.installmentCount === count;
              return (
                <Pressable
                  accessibilityLabel={`${count} parcelas`}
                  accessibilityRole="radio"
                  accessibilityState={{ selected }}
                  key={count}
                  onPress={() => patch({ installmentCount: count })}
                  style={({ pressed }) => [
                    styles.chip,
                    selected && styles.chipSelected,
                    pressed && styles.pressed,
                  ]}
                >
                  <Text style={[styles.chipText, selected && styles.chipTextSelected]}>
                    {count}x
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
            testID={testIds.moneyLab.life.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>TOTAL DAS PARCELAS</Text>
              <Text style={styles.resultHeroValue}>
                {formatCurrency(result.installmentTotal, hideAmounts)}
              </Text>
              <Text style={styles.resultHeroSupport}>
                {result.installmentCount} vezes de{" "}
                {formatCurrency(result.installmentAmount, hideAmounts)}
              </Text>
            </View>
            <View style={styles.metrics}>
              <Metric
                label="Preço à vista"
                value={formatCurrency(result.cashPrice, hideAmounts)}
              />
              <Metric
                emphasis
                label="Diferença para o à vista"
                value={formatSignedCurrency(result.difference, hideAmounts)}
              />
              <Metric
                label="Taxa implícita ao mês"
                value={
                  result.impliedMonthlyRatePercent === null
                    ? "Sem taxa positiva"
                    : formatPercent(result.impliedMonthlyRatePercent, 2)
                }
              />
              <Metric
                label="Equivalente efetivo ao ano"
                value={
                  result.impliedAnnualRatePercent === null
                    ? "Não se aplica"
                    : formatPercent(result.impliedAnnualRatePercent, 1)
                }
              />
            </View>
            {result.impliedMonthlyRatePercent === null ? (
              <Text style={styles.inlineNote}>
                Pelos números informados, parcelar não custa mais que pagar à
                vista. Por isso não existe uma taxa positiva implícita nesta conta.
              </Text>
            ) : (
              <Text style={styles.inlineNote}>
                A taxa implícita é a que iguala hoje o preço à vista às parcelas
                mensais informadas. Ela não é uma taxa anunciada pela loja.
              </Text>
            )}
            <ResultGuardrail>
              A conta não escolhe a forma de pagamento. Data real da primeira
              parcela, tarifas, desconto negociável, inflação, limite de cartão,
              atraso e uso alternativo do dinheiro ficam fora.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  function renderLongevity() {
    const initialAmount = parseMoney(
      session.withdrawalInitialAmountText,
      false,
    );
    const monthlyWithdrawal = parseMoney(session.withdrawalMonthlyText, false);
    const annualRatePercent = parseLocalizedNumber(
      session.withdrawalAnnualRateText,
    );
    const years = parseYears(session.withdrawalYearsText);
    const inflationRate = parseLocalizedNumber(
      session.withdrawalInflationText,
    );
    const errors: FieldErrors = {};

    if (initialAmount === null) {
      errors.withdrawalInitial = "Informe um saldo inicial positivo.";
    }
    if (monthlyWithdrawal === null) {
      errors.withdrawalMonthly = "Informe uma retirada mensal positiva.";
    }
    if (
      annualRatePercent === null ||
      annualRatePercent < 0 ||
      annualRatePercent > MONEY_LAB_LIMITS.maxAnnualRatePercent
    ) {
      errors.withdrawalRate = "Use uma taxa entre 0% e 200% ao ano.";
    }
    if (years === null || years < 1 || years > MONEY_LAB_LIMITS.maxYears) {
      errors.withdrawalYears = "Use um horizonte entre 1 e 50 anos inteiros.";
    }
    if (
      session.adjustWithdrawalForInflation &&
      (inflationRate === null ||
        inflationRate < 0 ||
        inflationRate > MONEY_LAB_LIMITS.maxAnnualRatePercent)
    ) {
      errors.withdrawalInflation = "Use um reajuste entre 0% e 200% ao ano.";
    }

    const result =
      Object.keys(errors).length === 0
        ? simulateWithdrawalLongevity({
            initialAmount: initialAmount!,
            monthlyWithdrawal: monthlyWithdrawal!,
            annualRatePercent: annualRatePercent!,
            annualWithdrawalIncreasePercent:
              session.adjustWithdrawalForInflation ? inflationRate! : 0,
            years: years!,
          })
        : null;
    const coveragePercent = result
      ? Math.min(100, (result.monthsCovered / result.horizonMonths) * 100)
      : 0;

    return (
      <View style={styles.toolBody}>
        <View style={styles.toolHeading}>
          <Eyebrow>v0.6.4 · Dinheiro que dura</Eyebrow>
          <Text accessibilityRole="header" style={styles.toolTitle}>
            Se eu retirar todo mês, até quando o dinheiro aguenta?
          </Text>
          <Text style={styles.toolSupport}>
            Escolha saldo, retirada, taxa e horizonte. A conta credita o
            rendimento primeiro e faz a retirada no fim de cada mês.
          </Text>
        </View>

        <View style={styles.fieldGrid}>
          <NumericField
            error={visibleError(
              "withdrawalInitial",
              errors.withdrawalInitial,
            )}
            hiddenAmount={hideAmounts}
            label="Saldo inicial"
            onBlur={() => touch("withdrawalInitial")}
            onChangeText={(value) =>
              patch({ withdrawalInitialAmountText: value })
            }
            suffix="R$"
            testID={testIds.moneyLab.life.withdrawalInitialInput}
            value={session.withdrawalInitialAmountText}
          />
          <NumericField
            error={visibleError(
              "withdrawalMonthly",
              errors.withdrawalMonthly,
            )}
            hiddenAmount={hideAmounts}
            label="Retirada por mês"
            onBlur={() => touch("withdrawalMonthly")}
            onChangeText={(value) => patch({ withdrawalMonthlyText: value })}
            suffix="R$"
            testID={testIds.moneyLab.life.withdrawalMonthlyInput}
            value={session.withdrawalMonthlyText}
          />
          <NumericField
            error={visibleError("withdrawalRate", errors.withdrawalRate)}
            label="Taxa efetiva anual"
            onBlur={() => touch("withdrawalRate")}
            onChangeText={(value) => patch({ withdrawalAnnualRateText: value })}
            suffix="% a.a."
            testID={testIds.moneyLab.life.withdrawalRateInput}
            value={session.withdrawalAnnualRateText}
          />
          <NumericField
            error={visibleError("withdrawalYears", errors.withdrawalYears)}
            label="Horizonte da conta"
            onBlur={() => touch("withdrawalYears")}
            onChangeText={(value) => patch({ withdrawalYearsText: value })}
            suffix="anos"
            testID={testIds.moneyLab.life.withdrawalYearsInput}
            value={session.withdrawalYearsText}
          />
        </View>

        <Pressable
          accessibilityHint="Aumenta a retirada uma vez por ano pela taxa informada"
          accessibilityRole="switch"
          accessibilityState={{
            checked: session.adjustWithdrawalForInflation,
          }}
          onPress={() =>
            patch({
              adjustWithdrawalForInflation:
                !session.adjustWithdrawalForInflation,
            })
          }
          style={({ pressed }) => [
            styles.toggleCard,
            session.adjustWithdrawalForInflation && styles.toggleCardSelected,
            pressed && styles.pressed,
          ]}
          testID={testIds.moneyLab.life.withdrawalInflationToggle}
        >
          <View style={styles.toggleCopy}>
            <Text style={styles.toggleTitle}>Reajustar a retirada todo ano</Text>
            <Text style={styles.toggleSupport}>
              Opcional: simula a retirada acompanhando uma inflação escolhida.
            </Text>
          </View>
          <View
            accessibilityElementsHidden
            style={[
              styles.switchTrack,
              session.adjustWithdrawalForInflation && styles.switchTrackSelected,
            ]}
          >
            <View
              style={[
                styles.switchThumb,
                session.adjustWithdrawalForInflation && styles.switchThumbSelected,
              ]}
            />
          </View>
        </Pressable>

        {session.adjustWithdrawalForInflation ? (
          <View style={styles.fieldGrid}>
            <NumericField
              error={visibleError(
                "withdrawalInflation",
                errors.withdrawalInflation,
              )}
              label="Reajuste anual da retirada"
              onBlur={() => touch("withdrawalInflation")}
              onChangeText={(value) => patch({ withdrawalInflationText: value })}
              suffix="% a.a."
              testID={testIds.moneyLab.life.withdrawalInflationInput}
              value={session.withdrawalInflationText}
            />
          </View>
        ) : null}

        {result ? (
          <View
            accessibilityLiveRegion="polite"
            style={styles.result}
            testID={testIds.moneyLab.life.result}
          >
            <View style={styles.resultHero}>
              <Text style={styles.resultEyebrow}>FÔLEGO DO CENÁRIO</Text>
              <Text style={styles.resultHeroValue}>
                {result.exhaustedAtMonth === null
                  ? `${result.years} anos sem zerar`
                  : formatDuration(result.exhaustedAtMonth)}
              </Text>
              <Text style={styles.resultHeroSupport}>
                {result.exhaustedAtMonth === null
                  ? `${formatCurrency(result.finalBalance, hideAmounts)} permanece no fim do horizonte escolhido.`
                  : `O saldo chega a zero durante a retirada do mês ${result.exhaustedAtMonth}.`}
              </Text>
            </View>

            <View
              accessibilityLabel={`Cobertura simulada: ${formatDuration(result.monthsCovered)} de ${formatDuration(result.horizonMonths)}.`}
              style={styles.breathBlock}
            >
              <View style={styles.breathLabels}>
                <Text style={styles.breathLabel}>Hoje</Text>
                <Text style={styles.breathLabel}>
                  {formatDuration(result.horizonMonths)}
                </Text>
              </View>
              <View style={styles.breathTrack}>
                <View
                  style={[
                    styles.breathFill,
                    { width: `${coveragePercent}%` },
                  ]}
                />
              </View>
              <Text style={styles.breathSupport}>
                A faixa mostra até onde o saldo chegou dentro do horizonte, não
                uma probabilidade de duração.
              </Text>
            </View>

            <View style={styles.metrics}>
              <Metric
                emphasis
                label="Total retirado"
                value={formatCurrency(result.totalWithdrawn, hideAmounts)}
              />
              <Metric
                label="Crescimento creditado"
                value={formatCurrency(result.growthEarned, hideAmounts)}
              />
              <Metric
                label="Saldo no último marco"
                value={formatCurrency(result.finalBalance, hideAmounts)}
              />
              <Metric
                label="Retirada mensal no último ano"
                value={formatCurrency(
                  result.finalScheduledMonthlyWithdrawal,
                  hideAmounts,
                )}
              />
            </View>

            <View style={styles.timelineBlock}>
              <Text style={styles.timelineTitle}>Como o saldo atravessa o tempo</Text>
              {result.timeline.map((point) => (
                <View key={point.month} style={styles.timelineRow}>
                  <View style={styles.timelineCopy}>
                    <Text style={styles.timelinePeriod}>
                      {point.month % 12 === 0
                        ? `Ano ${point.month / 12}`
                        : `Mês ${point.month}`}
                    </Text>
                    <Text style={styles.timelineMeta}>
                      {formatCurrency(point.totalWithdrawn, hideAmounts)} retirado
                    </Text>
                  </View>
                  <Text style={styles.timelineBalance}>
                    {formatCurrency(point.balance, hideAmounts)}
                  </Text>
                </View>
              ))}
            </View>

            <Text style={styles.inlineNote}>
              {result.annualWithdrawalIncreasePercent > 0
                ? `A retirada aumenta ${formatPercent(result.annualWithdrawalIncreasePercent)} a cada 12 meses completos.`
                : "A retirada fica nominalmente igual durante todo o horizonte."}
            </Text>
            <ResultGuardrail>
              Taxa e inflação constantes são hipóteses. Imposto, volatilidade,
              produto, mudança de gastos, novas entradas e o tempo real que o
              dinheiro precisa cobrir ficam fora; este resultado não define uma
              retirada segura.
            </ResultGuardrail>
          </View>
        ) : null}
      </View>
    );
  }

  return (
    <Surface style={styles.panel} testID={testIds.moneyLab.life.panel}>
      <View style={styles.heading}>
        <Eyebrow>Decisões do dia a dia</Eyebrow>
        <Text accessibilityRole="header" style={styles.title}>
          Traga a vida real para a brincadeira
        </Text>
        <Text style={styles.support}>
          Três contas curtas, locais e editáveis. Nenhuma delas lê ou altera sua
          carteira.
        </Text>
        {hideAmounts ? (
          <Text style={styles.privateNote}>
            Modo discreto ativo: entradas e resultados monetários estão ocultos.
          </Text>
        ) : null}
      </View>
      <View accessibilityRole="radiogroup" style={styles.toolGrid}>
        {tools.map((tool) => {
          const selected = session.lifeTool === tool.key;
          return (
            <Pressable
              accessibilityLabel={`${tool.title}. ${tool.support}`}
              accessibilityRole="radio"
              accessibilityState={{ selected }}
              key={tool.key}
              onPress={() => patch({ lifeTool: tool.key })}
              style={({ pressed }) => [
                styles.toolOption,
                compact && styles.toolOptionCompact,
                selected && styles.toolOptionSelected,
                pressed && styles.pressed,
              ]}
              testID={tool.testID}
            >
              <Text style={[styles.toolIndex, selected && styles.toolIndexSelected]}>
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
      {session.lifeTool === "flexible" ? renderFlexible() : null}
      {session.lifeTool === "installments" ? renderInstallments() : null}
      {session.lifeTool === "longevity" ? renderLongevity() : null}
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
    flexBasis: 220,
    flexGrow: 1,
    gap: 3,
    minHeight: 96,
    minWidth: 200,
    padding: spacing.sm,
  },
  toolOptionCompact: { flexBasis: 142, minWidth: 136 },
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
  choiceBlock: { gap: spacing.xs },
  choiceSupport: { color: colors.textMuted, fontSize: 11, lineHeight: 16 },
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
  toggleCard: {
    alignItems: "center",
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    flexDirection: "row",
    gap: spacing.md,
    justifyContent: "space-between",
    minHeight: 64,
    padding: spacing.sm,
  },
  toggleCardSelected: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
  },
  toggleCopy: { flex: 1, gap: 3 },
  toggleTitle: { color: colors.text, fontSize: 13, fontWeight: "900" },
  toggleSupport: { color: colors.textMuted, fontSize: 11, lineHeight: 16 },
  switchTrack: {
    backgroundColor: colors.border,
    borderRadius: radius.pill,
    height: 28,
    justifyContent: "center",
    paddingHorizontal: 3,
    width: 50,
  },
  switchTrackSelected: { backgroundColor: colors.primary },
  switchThumb: {
    backgroundColor: colors.surface,
    borderRadius: radius.pill,
    height: 22,
    width: 22,
  },
  switchThumbSelected: { alignSelf: "flex-end" },
  result: { gap: spacing.md },
  resultHero: {
    backgroundColor: colors.primaryDark,
    borderRadius: radius.md,
    gap: spacing.xs,
    padding: spacing.lg,
  },
  resultEyebrow: {
    color: colors.primarySoft,
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
  resultHeroSupport: {
    color: colors.primarySoft,
    fontSize: 12,
    lineHeight: 18,
  },
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
  inlineNote: {
    backgroundColor: colors.attentionSoft,
    borderRadius: radius.sm,
    color: colors.attention,
    fontSize: 12,
    lineHeight: 18,
    padding: spacing.sm,
  },
  breathBlock: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    gap: spacing.xs,
    padding: spacing.sm,
  },
  breathLabels: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  breathLabel: { color: colors.text, fontSize: 11, fontWeight: "800" },
  breathTrack: {
    backgroundColor: colors.border,
    borderRadius: radius.pill,
    height: 12,
    overflow: "hidden",
  },
  breathFill: {
    backgroundColor: colors.primary,
    borderRadius: radius.pill,
    height: "100%",
  },
  breathSupport: { color: colors.textMuted, fontSize: 10, lineHeight: 15 },
  timelineBlock: { gap: spacing.xs },
  timelineTitle: { color: colors.text, fontSize: 13, fontWeight: "900" },
  timelineRow: {
    alignItems: "center",
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
    flexDirection: "row",
    gap: spacing.sm,
    justifyContent: "space-between",
    minHeight: 54,
    paddingVertical: spacing.xs,
  },
  timelineCopy: { flex: 1, gap: 2 },
  timelinePeriod: { color: colors.text, fontSize: 12, fontWeight: "800" },
  timelineMeta: { color: colors.textMuted, fontSize: 10 },
  timelineBalance: {
    color: colors.primaryDark,
    fontSize: 14,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  guardrail: {
    backgroundColor: colors.goldSoft,
    borderColor: colors.gold,
    borderRadius: radius.sm,
    borderWidth: 1,
    gap: 4,
    padding: spacing.sm,
  },
  guardrailTitle: { color: colors.text, fontSize: 12, fontWeight: "900" },
  guardrailText: { color: colors.textMuted, fontSize: 11, lineHeight: 17 },
  pressed: { opacity: 0.65 },
});
