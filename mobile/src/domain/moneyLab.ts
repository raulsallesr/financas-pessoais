export const MONEY_LAB_LIMITS = {
  maxAmount: 999_999_999_999.99,
  maxAnnualRatePercent: 200,
  maxYears: 50,
} as const;

const MONTHS_PER_YEAR = 12;

export type CompoundGrowthInput = {
  initialAmount: number;
  monthlyContribution: number;
  annualRatePercent: number;
  years: number;
};

export type ProjectionPoint = {
  year: number;
  futureValue: number;
  totalContributed: number;
  interestEarned: number;
};

export type CompoundGrowthProjection = ProjectionPoint & {
  monthlyRate: number;
  timeline: readonly ProjectionPoint[];
};

export type GoalProjection = {
  targetAmount: number;
  monthlyContribution: number;
  futureValueFromInitial: number;
  totalContributed: number;
  interestEarned: number;
  targetMetByInitial: boolean;
};

export type DelayedStartComparison = {
  delayYears: number;
  startNow: CompoundGrowthProjection;
  startLater: ProjectionPoint;
  difference: number;
  contributionsSkipped: number;
};

export type HabitFrequency = "daily" | "weekly" | "monthly";

export type HabitProjection = {
  frequency: HabitFrequency;
  amountPerOccurrence: number;
  monthlyEquivalent: number;
  totalDirected: number;
  futureValue: number;
  interestEarned: number;
};

export type ChallengeChoice = "rate" | "contribution";

export type IntuitionChallenge = {
  base: CompoundGrowthProjection;
  higherRate: CompoundGrowthProjection;
  higherContribution: CompoundGrowthProjection;
  rateGain: number;
  contributionGain: number;
  winner: ChallengeChoice | "tie";
};

export type DoublingTimeProjection = {
  targetAmount: number;
  withContributionsMonths: number | null;
  withoutContributionsMonths: number | null;
};

export type MilestoneProjection = {
  amount: number;
  reachedAtMonths: number | null;
  point: ProjectionPoint | null;
};

export type MonthlyYieldEquivalent = {
  monthlyRate: number;
  monthlyRatePercent: number;
  oneMonthInterest: number;
};

export type ExtraContributionCadence = "today" | "yearly";

export type ExtraContributionComparison = {
  cadence: ExtraContributionCadence;
  base: CompoundGrowthProjection;
  withExtra: ProjectionPoint;
  extraContributed: number;
  difference: number;
};

export type ReserveJourney = {
  targetMonths: number;
  currentMonthsCovered: number;
  targetAmount: number;
  missingAmount: number;
  monthsToTarget: number | null;
  alreadyReached: boolean;
};

export type ContributionImpactComparison = {
  withoutContributions: ProjectionPoint;
  withContributions: CompoundGrowthProjection;
  difference: number;
};

export type AnnualCostComparison = {
  annualCostPercent: number;
  netAnnualRatePercent: number;
  beforeCost: CompoundGrowthProjection;
  afterCost: CompoundGrowthProjection;
  difference: number;
};

export type FlexibleContributionPlan = {
  annualIncreasePercent: number;
  pauseStartMonth: number;
  pauseMonths: number;
  base: CompoundGrowthProjection;
  flexible: ProjectionPoint;
  finalScheduledMonthlyContribution: number;
  skippedContributions: number;
  difference: number;
};

export type InstallmentComparison = {
  cashPrice: number;
  installmentAmount: number;
  installmentCount: number;
  installmentTotal: number;
  difference: number;
  impliedMonthlyRatePercent: number | null;
  impliedAnnualRatePercent: number | null;
};

export type WithdrawalCheckpoint = {
  month: number;
  balance: number;
  totalWithdrawn: number;
  growthEarned: number;
  scheduledMonthlyWithdrawal: number;
};

export type WithdrawalLongevityProjection = {
  initialAmount: number;
  monthlyWithdrawal: number;
  annualRatePercent: number;
  annualWithdrawalIncreasePercent: number;
  years: number;
  horizonMonths: number;
  exhaustedAtMonth: number | null;
  monthsCovered: number;
  finalBalance: number;
  totalWithdrawn: number;
  growthEarned: number;
  finalScheduledMonthlyWithdrawal: number;
  timeline: readonly WithdrawalCheckpoint[];
};

function assertAmount(value: number, label: string, allowZero: boolean): void {
  const validMinimum = allowZero ? value >= 0 : value > 0;
  if (
    !Number.isFinite(value) ||
    !validMinimum ||
    value > MONEY_LAB_LIMITS.maxAmount
  ) {
    throw new Error(`${label} deve ser um valor válido.`);
  }
}

function assertRate(value: number, label = "A taxa anual"): void {
  if (
    !Number.isFinite(value) ||
    value < 0 ||
    value > MONEY_LAB_LIMITS.maxAnnualRatePercent
  ) {
    throw new Error(`${label} deve ficar entre 0% e 200% ao ano.`);
  }
}

function assertYears(value: number): void {
  if (
    !Number.isInteger(value) ||
    value < 1 ||
    value > MONEY_LAB_LIMITS.maxYears
  ) {
    throw new Error("O prazo deve ficar entre 1 e 50 anos inteiros.");
  }
}

function validateGrowthInput(input: CompoundGrowthInput): void {
  assertAmount(input.initialAmount, "O valor inicial", true);
  assertAmount(input.monthlyContribution, "O aporte mensal", true);
  if (input.initialAmount === 0 && input.monthlyContribution === 0) {
    throw new Error("Informe um valor inicial ou um aporte mensal.");
  }
  assertRate(input.annualRatePercent);
  assertYears(input.years);
}

function firstMonthAtTarget(
  input: CompoundGrowthInput,
  targetAmount: number,
): number | null {
  if (input.initialAmount >= targetAmount) {
    return 0;
  }
  const totalMonths = input.years * MONTHS_PER_YEAR;
  for (let month = 1; month <= totalMonths; month += 1) {
    if (projectionAtMonths(input, month).futureValue >= targetAmount) {
      return month;
    }
  }
  return null;
}

export function effectiveMonthlyRate(annualRatePercent: number): number {
  assertRate(annualRatePercent);
  return Math.pow(1 + annualRatePercent / 100, 1 / MONTHS_PER_YEAR) - 1;
}

function projectionAtMonths(
  input: CompoundGrowthInput,
  months: number,
): ProjectionPoint {
  const monthlyRate = effectiveMonthlyRate(input.annualRatePercent);
  const factor = Math.pow(1 + monthlyRate, months);
  const contributionFutureValue =
    monthlyRate === 0
      ? input.monthlyContribution * months
      : input.monthlyContribution * ((factor - 1) / monthlyRate);
  const futureValue = input.initialAmount * factor + contributionFutureValue;
  const totalContributed =
    input.initialAmount + input.monthlyContribution * months;

  if (!Number.isFinite(futureValue)) {
    throw new Error("A combinação informada ultrapassa o limite da simulação.");
  }

  return {
    year: months / MONTHS_PER_YEAR,
    futureValue,
    totalContributed,
    interestEarned: Math.max(0, futureValue - totalContributed),
  };
}

function timelineYears(years: number): readonly number[] {
  return [
    1,
    Math.ceil(years * 0.25),
    Math.ceil(years * 0.5),
    Math.ceil(years * 0.75),
    years,
  ]
    .filter((year) => year <= years)
    .filter((year, index, values) => values.indexOf(year) === index)
    .sort((left, right) => left - right);
}

export function simulateCompoundGrowth(
  input: CompoundGrowthInput,
): CompoundGrowthProjection {
  validateGrowthInput(input);
  const finalPoint = projectionAtMonths(input, input.years * MONTHS_PER_YEAR);
  return {
    ...finalPoint,
    monthlyRate: effectiveMonthlyRate(input.annualRatePercent),
    timeline: timelineYears(input.years).map((year) =>
      projectionAtMonths(input, year * MONTHS_PER_YEAR),
    ),
  };
}

export function adjustForInflation(
  futureValue: number,
  inflationRatePercent: number,
  years: number,
): number {
  if (!Number.isFinite(futureValue) || futureValue < 0) {
    throw new Error("O valor futuro deve ser válido.");
  }
  assertRate(inflationRatePercent, "A inflação");
  assertYears(years);
  return futureValue / Math.pow(1 + inflationRatePercent / 100, years);
}

export function calculateRequiredMonthlyContribution({
  targetAmount,
  initialAmount,
  annualRatePercent,
  years,
}: {
  targetAmount: number;
  initialAmount: number;
  annualRatePercent: number;
  years: number;
}): GoalProjection {
  assertAmount(targetAmount, "A meta", false);
  assertAmount(initialAmount, "O valor inicial", true);
  assertRate(annualRatePercent);
  assertYears(years);

  const months = years * MONTHS_PER_YEAR;
  const monthlyRate = effectiveMonthlyRate(annualRatePercent);
  const factor = Math.pow(1 + monthlyRate, months);
  const futureValueFromInitial = initialAmount * factor;
  const remaining = Math.max(0, targetAmount - futureValueFromInitial);
  const annuityFactor =
    monthlyRate === 0 ? months : (factor - 1) / monthlyRate;
  const monthlyContribution = remaining / annuityFactor;
  const totalContributed = initialAmount + monthlyContribution * months;

  return {
    targetAmount,
    monthlyContribution,
    futureValueFromInitial,
    totalContributed,
    interestEarned: Math.max(0, targetAmount - totalContributed),
    targetMetByInitial: remaining === 0,
  };
}

export function compareDelayedStart(
  input: CompoundGrowthInput,
  delayYears: number,
): DelayedStartComparison {
  validateGrowthInput(input);
  if (
    !Number.isInteger(delayYears) ||
    delayYears < 1 ||
    delayYears >= input.years
  ) {
    throw new Error("A espera deve ser menor que o prazo total.");
  }

  const startNow = simulateCompoundGrowth(input);
  const remainingMonths = (input.years - delayYears) * MONTHS_PER_YEAR;
  const startLater = projectionAtMonths(input, remainingMonths);

  return {
    delayYears,
    startNow,
    startLater,
    difference: Math.max(0, startNow.futureValue - startLater.futureValue),
    contributionsSkipped:
      input.monthlyContribution * delayYears * MONTHS_PER_YEAR,
  };
}

export function monthlyEquivalentForHabit(
  amountPerOccurrence: number,
  frequency: HabitFrequency,
): number {
  assertAmount(amountPerOccurrence, "O valor do hábito", false);
  if (frequency === "daily") {
    return (amountPerOccurrence * 365) / MONTHS_PER_YEAR;
  }
  if (frequency === "weekly") {
    return (amountPerOccurrence * 52) / MONTHS_PER_YEAR;
  }
  if (frequency === "monthly") {
    return amountPerOccurrence;
  }
  throw new Error("A frequência escolhida não faz parte do laboratório.");
}

export function simulateHabitRedirect({
  amountPerOccurrence,
  frequency,
  annualRatePercent,
  years,
}: {
  amountPerOccurrence: number;
  frequency: HabitFrequency;
  annualRatePercent: number;
  years: number;
}): HabitProjection {
  const monthlyEquivalent = monthlyEquivalentForHabit(
    amountPerOccurrence,
    frequency,
  );
  const projection = simulateCompoundGrowth({
    initialAmount: 0,
    monthlyContribution: monthlyEquivalent,
    annualRatePercent,
    years,
  });
  return {
    frequency,
    amountPerOccurrence,
    monthlyEquivalent,
    totalDirected: projection.totalContributed,
    futureValue: projection.futureValue,
    interestEarned: projection.interestEarned,
  };
}

export function compareIntuitionChallenge(
  input: CompoundGrowthInput,
  rateIncreasePercentagePoints = 1,
  monthlyContributionIncrease = 150,
): IntuitionChallenge {
  validateGrowthInput(input);
  assertAmount(
    monthlyContributionIncrease,
    "O aumento do aporte mensal",
    false,
  );
  assertRate(input.annualRatePercent + rateIncreasePercentagePoints);

  const base = simulateCompoundGrowth(input);
  const higherRate = simulateCompoundGrowth({
    ...input,
    annualRatePercent:
      input.annualRatePercent + rateIncreasePercentagePoints,
  });
  const higherContribution = simulateCompoundGrowth({
    ...input,
    monthlyContribution:
      input.monthlyContribution + monthlyContributionIncrease,
  });
  const rateGain = higherRate.futureValue - base.futureValue;
  const contributionGain =
    higherContribution.futureValue - base.futureValue;
  const difference = rateGain - contributionGain;

  return {
    base,
    higherRate,
    higherContribution,
    rateGain,
    contributionGain,
    winner:
      Math.abs(difference) < 0.01
        ? "tie"
        : difference > 0
          ? "rate"
          : "contribution",
  };
}

export function calculateDoublingTime({
  initialAmount,
  monthlyContribution,
  annualRatePercent,
  maxYears = MONEY_LAB_LIMITS.maxYears,
}: {
  initialAmount: number;
  monthlyContribution: number;
  annualRatePercent: number;
  maxYears?: number;
}): DoublingTimeProjection {
  assertAmount(initialAmount, "O valor inicial", false);
  assertAmount(monthlyContribution, "O aporte mensal", true);
  assertRate(annualRatePercent);
  assertYears(maxYears);

  const targetAmount = initialAmount * 2;
  const input = {
    initialAmount,
    monthlyContribution,
    annualRatePercent,
    years: maxYears,
  };
  const withoutContributions = { ...input, monthlyContribution: 0 };

  return {
    targetAmount,
    withContributionsMonths: firstMonthAtTarget(input, targetAmount),
    withoutContributionsMonths: firstMonthAtTarget(
      withoutContributions,
      targetAmount,
    ),
  };
}

export function calculateMilestoneTimeline(
  input: CompoundGrowthInput,
  milestones: readonly number[] = [10_000, 50_000, 100_000],
): readonly MilestoneProjection[] {
  validateGrowthInput(input);
  const uniqueMilestones = [...new Set(milestones)].sort(
    (left, right) => left - right,
  );
  uniqueMilestones.forEach((amount) =>
    assertAmount(amount, "O marco", false),
  );

  return uniqueMilestones.map((amount) => {
    const reachedAtMonths = firstMonthAtTarget(input, amount);
    return {
      amount,
      reachedAtMonths,
      point:
        reachedAtMonths === null
          ? null
          : projectionAtMonths(input, reachedAtMonths),
    };
  });
}

export function calculateMonthlyYieldEquivalent(
  amount: number,
  annualRatePercent: number,
): MonthlyYieldEquivalent {
  assertAmount(amount, "O valor aplicado", false);
  const monthlyRate = effectiveMonthlyRate(annualRatePercent);
  return {
    monthlyRate,
    monthlyRatePercent: monthlyRate * 100,
    oneMonthInterest: amount * monthlyRate,
  };
}

export function simulateExtraContribution({
  input,
  extraAmount,
  cadence,
}: {
  input: CompoundGrowthInput;
  extraAmount: number;
  cadence: ExtraContributionCadence;
}): ExtraContributionComparison {
  validateGrowthInput(input);
  assertAmount(extraAmount, "O aporte extra", false);
  if (cadence !== "today" && cadence !== "yearly") {
    throw new Error("A frequência do aporte extra não é suportada.");
  }

  const base = simulateCompoundGrowth(input);
  let withExtra: ProjectionPoint;
  let extraContributed: number;

  if (cadence === "today") {
    assertAmount(
      input.initialAmount + extraAmount,
      "O valor inicial com o aporte extra",
      false,
    );
    const projection = simulateCompoundGrowth({
      ...input,
      initialAmount: input.initialAmount + extraAmount,
    });
    withExtra = projection;
    extraContributed = extraAmount;
  } else {
    const monthlyRate = effectiveMonthlyRate(input.annualRatePercent);
    const totalMonths = input.years * MONTHS_PER_YEAR;
    let futureValue = input.initialAmount;
    let totalContributed = input.initialAmount;
    for (let month = 1; month <= totalMonths; month += 1) {
      futureValue = futureValue * (1 + monthlyRate) + input.monthlyContribution;
      totalContributed += input.monthlyContribution;
      if (month % MONTHS_PER_YEAR === 0) {
        futureValue += extraAmount;
        totalContributed += extraAmount;
      }
    }
    if (!Number.isFinite(futureValue)) {
      throw new Error("A combinação informada ultrapassa o limite da simulação.");
    }
    withExtra = {
      year: input.years,
      futureValue,
      totalContributed,
      interestEarned: Math.max(0, futureValue - totalContributed),
    };
    extraContributed = extraAmount * input.years;
  }

  return {
    cadence,
    base,
    withExtra,
    extraContributed,
    difference: Math.max(0, withExtra.futureValue - base.futureValue),
  };
}

export function calculateReserveJourney({
  currentReserve,
  monthlyEssentialExpenses,
  monthlyContribution,
  targetMonths,
}: {
  currentReserve: number;
  monthlyEssentialExpenses: number;
  monthlyContribution: number;
  targetMonths: number;
}): ReserveJourney {
  assertAmount(currentReserve, "A reserva atual", true);
  assertAmount(
    monthlyEssentialExpenses,
    "O gasto essencial mensal",
    false,
  );
  assertAmount(monthlyContribution, "O aporte mensal", true);
  if (!Number.isInteger(targetMonths) || targetMonths < 1 || targetMonths > 24) {
    throw new Error("A meta da reserva deve ficar entre 1 e 24 meses.");
  }

  const targetAmount = monthlyEssentialExpenses * targetMonths;
  const missingAmount = Math.max(0, targetAmount - currentReserve);
  const alreadyReached = missingAmount === 0;
  return {
    targetMonths,
    currentMonthsCovered: currentReserve / monthlyEssentialExpenses,
    targetAmount,
    missingAmount,
    monthsToTarget: alreadyReached
      ? 0
      : monthlyContribution === 0
        ? null
        : Math.ceil(missingAmount / monthlyContribution),
    alreadyReached,
  };
}

export function compareContributionImpact(
  input: CompoundGrowthInput,
): ContributionImpactComparison {
  validateGrowthInput(input);
  const withContributions = simulateCompoundGrowth(input);
  const withoutContributions =
    input.initialAmount === 0
      ? {
          year: input.years,
          futureValue: 0,
          totalContributed: 0,
          interestEarned: 0,
        }
      : projectionAtMonths(
          { ...input, monthlyContribution: 0 },
          input.years * MONTHS_PER_YEAR,
        );
  return {
    withoutContributions,
    withContributions,
    difference:
      withContributions.futureValue - withoutContributions.futureValue,
  };
}

export function compareAnnualCostDrag(
  input: CompoundGrowthInput,
  annualCostPercent: number,
): AnnualCostComparison {
  validateGrowthInput(input);
  assertRate(annualCostPercent, "O custo anual");
  if (annualCostPercent > input.annualRatePercent) {
    throw new Error("O custo anual deve ser menor ou igual à taxa do cenário.");
  }

  const netAnnualRatePercent =
    ((1 + input.annualRatePercent / 100) /
      (1 + annualCostPercent / 100) -
      1) *
    100;
  const beforeCost = simulateCompoundGrowth(input);
  const afterCost = simulateCompoundGrowth({
    ...input,
    annualRatePercent: netAnnualRatePercent,
  });
  return {
    annualCostPercent,
    netAnnualRatePercent,
    beforeCost,
    afterCost,
    difference: Math.max(0, beforeCost.futureValue - afterCost.futureValue),
  };
}

export function simulateFlexibleContributionPlan({
  input,
  annualIncreasePercent,
  pauseStartMonth,
  pauseMonths,
}: {
  input: CompoundGrowthInput;
  annualIncreasePercent: number;
  pauseStartMonth: number;
  pauseMonths: number;
}): FlexibleContributionPlan {
  validateGrowthInput(input);
  assertRate(annualIncreasePercent, "O reajuste anual do aporte");
  const totalMonths = input.years * MONTHS_PER_YEAR;
  if (
    !Number.isInteger(pauseStartMonth) ||
    pauseStartMonth < 1 ||
    pauseStartMonth > totalMonths
  ) {
    throw new Error("O início da pausa deve ficar dentro do prazo do cenário.");
  }
  if (!Number.isInteger(pauseMonths) || pauseMonths < 0 || pauseMonths > 12) {
    throw new Error("A pausa deve ficar entre zero e doze meses inteiros.");
  }

  const base = simulateCompoundGrowth(input);
  const monthlyRate = effectiveMonthlyRate(input.annualRatePercent);
  const annualIncreaseFactor = 1 + annualIncreasePercent / 100;
  let futureValue = input.initialAmount;
  let totalContributed = input.initialAmount;
  let skippedContributions = 0;
  let finalScheduledMonthlyContribution = input.monthlyContribution;

  for (let month = 1; month <= totalMonths; month += 1) {
    futureValue *= 1 + monthlyRate;
    const contributionYear = Math.floor((month - 1) / MONTHS_PER_YEAR);
    const scheduledContribution =
      input.monthlyContribution *
      Math.pow(annualIncreaseFactor, contributionYear);
    finalScheduledMonthlyContribution = scheduledContribution;
    const paused =
      pauseMonths > 0 &&
      month >= pauseStartMonth &&
      month < pauseStartMonth + pauseMonths;
    if (paused) {
      skippedContributions += scheduledContribution;
    } else {
      futureValue += scheduledContribution;
      totalContributed += scheduledContribution;
    }
  }

  if (
    !Number.isFinite(futureValue) ||
    !Number.isFinite(totalContributed) ||
    !Number.isFinite(finalScheduledMonthlyContribution)
  ) {
    throw new Error("A combinação informada ultrapassa o limite da simulação.");
  }

  const flexible: ProjectionPoint = {
    year: input.years,
    futureValue,
    totalContributed,
    interestEarned: Math.max(0, futureValue - totalContributed),
  };
  return {
    annualIncreasePercent,
    pauseStartMonth,
    pauseMonths,
    base,
    flexible,
    finalScheduledMonthlyContribution,
    skippedContributions,
    difference: flexible.futureValue - base.futureValue,
  };
}

function installmentPresentValue(
  installmentAmount: number,
  installmentCount: number,
  monthlyRate: number,
): number {
  if (monthlyRate === 0) {
    return installmentAmount * installmentCount;
  }
  return (
    installmentAmount *
    ((1 - Math.pow(1 + monthlyRate, -installmentCount)) / monthlyRate)
  );
}

export function compareCashAndInstallments({
  cashPrice,
  installmentAmount,
  installmentCount,
}: {
  cashPrice: number;
  installmentAmount: number;
  installmentCount: number;
}): InstallmentComparison {
  assertAmount(cashPrice, "O preço à vista", false);
  assertAmount(installmentAmount, "O valor da parcela", false);
  if (
    !Number.isInteger(installmentCount) ||
    installmentCount < 2 ||
    installmentCount > 60
  ) {
    throw new Error("A quantidade deve ficar entre 2 e 60 parcelas.");
  }

  const installmentTotal = installmentAmount * installmentCount;
  if (!Number.isFinite(installmentTotal)) {
    throw new Error("A combinação informada ultrapassa o limite da simulação.");
  }
  const difference = installmentTotal - cashPrice;
  if (difference <= 0) {
    return {
      cashPrice,
      installmentAmount,
      installmentCount,
      installmentTotal,
      difference,
      impliedMonthlyRatePercent: null,
      impliedAnnualRatePercent: null,
    };
  }

  let low = 0;
  let high = 1;
  let expansion = 0;
  while (
    installmentPresentValue(installmentAmount, installmentCount, high) >
      cashPrice &&
    expansion < 128
  ) {
    high *= 2;
    expansion += 1;
  }
  if (
    installmentPresentValue(installmentAmount, installmentCount, high) >
    cashPrice
  ) {
    throw new Error("A combinação informada ultrapassa o limite da simulação.");
  }
  for (let iteration = 0; iteration < 120; iteration += 1) {
    const midpoint = (low + high) / 2;
    if (
      installmentPresentValue(
        installmentAmount,
        installmentCount,
        midpoint,
      ) > cashPrice
    ) {
      low = midpoint;
    } else {
      high = midpoint;
    }
  }
  const impliedMonthlyRate = (low + high) / 2;

  return {
    cashPrice,
    installmentAmount,
    installmentCount,
    installmentTotal,
    difference,
    impliedMonthlyRatePercent: impliedMonthlyRate * 100,
    impliedAnnualRatePercent:
      (Math.pow(1 + impliedMonthlyRate, MONTHS_PER_YEAR) - 1) * 100,
  };
}

export function simulateWithdrawalLongevity({
  initialAmount,
  monthlyWithdrawal,
  annualRatePercent,
  annualWithdrawalIncreasePercent,
  years,
}: {
  initialAmount: number;
  monthlyWithdrawal: number;
  annualRatePercent: number;
  annualWithdrawalIncreasePercent: number;
  years: number;
}): WithdrawalLongevityProjection {
  assertAmount(initialAmount, "O saldo inicial", false);
  assertAmount(monthlyWithdrawal, "A retirada mensal", false);
  assertRate(annualRatePercent);
  assertRate(
    annualWithdrawalIncreasePercent,
    "O reajuste anual da retirada",
  );
  assertYears(years);

  const horizonMonths = years * MONTHS_PER_YEAR;
  const monthlyRate = effectiveMonthlyRate(annualRatePercent);
  const annualWithdrawalFactor = 1 + annualWithdrawalIncreasePercent / 100;
  const checkpointMonths = new Set(
    timelineYears(years).map((year) => year * MONTHS_PER_YEAR),
  );
  const timeline: WithdrawalCheckpoint[] = [];
  let balance = initialAmount;
  let totalWithdrawn = 0;
  let growthEarned = 0;
  let scheduledMonthlyWithdrawal = monthlyWithdrawal;
  let exhaustedAtMonth: number | null = null;

  for (let month = 1; month <= horizonMonths; month += 1) {
    if (month > 1 && (month - 1) % MONTHS_PER_YEAR === 0) {
      scheduledMonthlyWithdrawal *= annualWithdrawalFactor;
    }

    const monthlyGrowth = balance * monthlyRate;
    balance += monthlyGrowth;
    growthEarned += monthlyGrowth;
    const actualWithdrawal = Math.min(balance, scheduledMonthlyWithdrawal);
    balance -= actualWithdrawal;
    totalWithdrawn += actualWithdrawal;

    if (
      !Number.isFinite(balance) ||
      !Number.isFinite(totalWithdrawn) ||
      !Number.isFinite(growthEarned) ||
      !Number.isFinite(scheduledMonthlyWithdrawal)
    ) {
      throw new Error("A combinação informada ultrapassa o limite da simulação.");
    }

    if (balance <= 0.005) {
      balance = 0;
      exhaustedAtMonth = month;
    }

    if (checkpointMonths.has(month) || exhaustedAtMonth !== null) {
      timeline.push({
        month,
        balance,
        totalWithdrawn,
        growthEarned,
        scheduledMonthlyWithdrawal,
      });
    }

    if (exhaustedAtMonth !== null) {
      break;
    }
  }

  return {
    initialAmount,
    monthlyWithdrawal,
    annualRatePercent,
    annualWithdrawalIncreasePercent,
    years,
    horizonMonths,
    exhaustedAtMonth,
    monthsCovered: exhaustedAtMonth ?? horizonMonths,
    finalBalance: balance,
    totalWithdrawn,
    growthEarned,
    finalScheduledMonthlyWithdrawal: scheduledMonthlyWithdrawal,
    timeline,
  };
}
