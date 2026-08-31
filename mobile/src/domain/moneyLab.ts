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
