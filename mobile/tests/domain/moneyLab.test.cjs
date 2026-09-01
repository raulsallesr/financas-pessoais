const assert = require("node:assert/strict");
const test = require("node:test");

const {
  adjustForInflation,
  calculateDoublingTime,
  calculateMilestoneTimeline,
  calculateMonthlyYieldEquivalent,
  calculateRequiredMonthlyContribution,
  calculateReserveJourney,
  compareAnnualCostDrag,
  compareContributionImpact,
  compareDelayedStart,
  compareIntuitionChallenge,
  effectiveMonthlyRate,
  monthlyEquivalentForHabit,
  simulateCompoundGrowth,
  simulateExtraContribution,
  simulateHabitRedirect,
} = require("../../.test-dist/domain/moneyLab.js");

test("converte taxa anual efetiva e separa aportes de juros compostos", () => {
  const projection = simulateCompoundGrowth({
    initialAmount: 1_000,
    monthlyContribution: 300,
    annualRatePercent: 10,
    years: 10,
  });

  assert.ok(Math.abs(effectiveMonthlyRate(10) - 0.00797414) < 0.00000001);
  assert.equal(projection.totalContributed, 37_000);
  assert.ok(projection.futureValue > projection.totalContributed);
  assert.ok(projection.interestEarned > 25_000);
  assert.equal(projection.timeline.at(-1).year, 10);
  assert.equal(projection.timeline.at(-1).futureValue, projection.futureValue);
});

test("taxa zero mantém somente valor inicial e aportes", () => {
  const projection = simulateCompoundGrowth({
    initialAmount: 2_000,
    monthlyContribution: 100,
    annualRatePercent: 0,
    years: 2,
  });

  assert.equal(projection.futureValue, 4_400);
  assert.equal(projection.totalContributed, 4_400);
  assert.equal(projection.interestEarned, 0);
});

test("meta ao contrário encontra o aporte que fecha o valor futuro", () => {
  const goal = calculateRequiredMonthlyContribution({
    targetAmount: 50_000,
    initialAmount: 1_000,
    annualRatePercent: 10,
    years: 5,
  });
  const projection = simulateCompoundGrowth({
    initialAmount: 1_000,
    monthlyContribution: goal.monthlyContribution,
    annualRatePercent: 10,
    years: 5,
  });

  assert.ok(Math.abs(projection.futureValue - 50_000) < 0.000001);
  assert.equal(goal.targetMetByInitial, false);
  assert.ok(goal.monthlyContribution > 500);
});

test("meta já coberta pelo valor inicial não inventa aporte negativo", () => {
  const goal = calculateRequiredMonthlyContribution({
    targetAmount: 10_000,
    initialAmount: 10_000,
    annualRatePercent: 10,
    years: 5,
  });

  assert.equal(goal.monthlyContribution, 0);
  assert.equal(goal.targetMetByInitial, true);
});

test("esperar reduz meses de juros e aportes sem apagar o valor inicial", () => {
  const comparison = compareDelayedStart(
    {
      initialAmount: 1_000,
      monthlyContribution: 300,
      annualRatePercent: 10,
      years: 10,
    },
    3,
  );

  assert.equal(comparison.startLater.year, 7);
  assert.equal(comparison.contributionsSkipped, 10_800);
  assert.ok(comparison.difference > comparison.contributionsSkipped);
});

test("inflação traduz valor futuro para poder de compra do início", () => {
  const realValue = adjustForInflation(100_000, 5, 10);

  assert.ok(realValue > 61_000);
  assert.ok(realValue < 62_000);
});

test("hábito diário usa média anual explícita e permanece cenário mecânico", () => {
  const monthly = monthlyEquivalentForHabit(15, "daily");
  const projection = simulateHabitRedirect({
    amountPerOccurrence: 15,
    frequency: "daily",
    annualRatePercent: 10,
    years: 10,
  });

  assert.equal(monthly, 456.25);
  assert.equal(projection.monthlyEquivalent, monthly);
  assert.equal(projection.totalDirected, 54_750);
  assert.ok(projection.futureValue > projection.totalDirected);
});

test("desafio compara a variação de cada hipótese contra a mesma base", () => {
  const challenge = compareIntuitionChallenge({
    initialAmount: 1_000,
    monthlyContribution: 300,
    annualRatePercent: 10,
    years: 10,
  });

  assert.ok(challenge.rateGain > 0);
  assert.ok(challenge.contributionGain > 0);
  assert.equal(challenge.winner, "contribution");
});

test("rejeita valores fora dos limites didáticos", () => {
  assert.throws(
    () =>
      simulateCompoundGrowth({
        initialAmount: 0,
        monthlyContribution: 0,
        annualRatePercent: 10,
        years: 10,
      }),
    /valor inicial ou um aporte/,
  );
  assert.throws(
    () =>
      simulateCompoundGrowth({
        initialAmount: 1_000,
        monthlyContribution: 100,
        annualRatePercent: 201,
        years: 10,
      }),
    /entre 0% e 200%/,
  );
  assert.throws(
    () =>
      compareDelayedStart(
        {
          initialAmount: 1_000,
          monthlyContribution: 100,
          annualRatePercent: 10,
          years: 5,
        },
        5,
      ),
    /menor que o prazo total/,
  );
});

test("encontra quando o valor dobra e separa o efeito dos aportes", () => {
  const result = calculateDoublingTime({
    initialAmount: 10_000,
    monthlyContribution: 500,
    annualRatePercent: 10,
  });

  assert.equal(result.targetAmount, 20_000);
  assert.ok(result.withContributionsMonths < result.withoutContributionsMonths);
  assert.ok(result.withoutContributionsMonths >= 87);
  assert.ok(result.withoutContributionsMonths <= 88);
});

test("mantém dobra sem juros inalcançável quando também não há aportes", () => {
  const result = calculateDoublingTime({
    initialAmount: 10_000,
    monthlyContribution: 0,
    annualRatePercent: 0,
    maxYears: 10,
  });

  assert.equal(result.withContributionsMonths, null);
  assert.equal(result.withoutContributionsMonths, null);
});

test("localiza marcos dentro do horizonte e preserva os não alcançados", () => {
  const milestones = calculateMilestoneTimeline(
    {
      initialAmount: 5_000,
      monthlyContribution: 500,
      annualRatePercent: 8,
      years: 10,
    },
    [10_000, 50_000, 150_000],
  );

  assert.equal(milestones[0].amount, 10_000);
  assert.ok(milestones[0].reachedAtMonths > 0);
  assert.ok(milestones[1].reachedAtMonths > milestones[0].reachedAtMonths);
  assert.equal(milestones[2].reachedAtMonths, null);
});

test("traduz taxa anual para equivalente mensal sem dividir por doze", () => {
  const result = calculateMonthlyYieldEquivalent(20_000, 10);

  assert.ok(Math.abs(result.monthlyRatePercent - 0.797414) < 0.000001);
  assert.ok(result.oneMonthInterest > 159);
  assert.ok(result.oneMonthInterest < 160);
});

test("compara aporte extra hoje com a mesma base", () => {
  const result = simulateExtraContribution({
    input: {
      initialAmount: 1_000,
      monthlyContribution: 300,
      annualRatePercent: 10,
      years: 10,
    },
    extraAmount: 2_000,
    cadence: "today",
  });

  assert.equal(result.extraContributed, 2_000);
  assert.ok(result.difference > 5_000);
  assert.equal(
    result.withExtra.totalContributed - result.base.totalContributed,
    2_000,
  );
});

test("aporte extra anual entra ao fim de cada ano", () => {
  const result = simulateExtraContribution({
    input: {
      initialAmount: 1_000,
      monthlyContribution: 300,
      annualRatePercent: 10,
      years: 5,
    },
    extraAmount: 1_000,
    cadence: "yearly",
  });

  assert.equal(result.extraContributed, 5_000);
  assert.equal(
    result.withExtra.totalContributed - result.base.totalContributed,
    5_000,
  );
  assert.ok(result.difference > result.extraContributed);
});

test("calcula cobertura e caminho da reserva sem atribuir rendimento", () => {
  const result = calculateReserveJourney({
    currentReserve: 6_000,
    monthlyEssentialExpenses: 3_000,
    monthlyContribution: 750,
    targetMonths: 6,
  });

  assert.equal(result.currentMonthsCovered, 2);
  assert.equal(result.targetAmount, 18_000);
  assert.equal(result.missingAmount, 12_000);
  assert.equal(result.monthsToTarget, 16);
});

test("reserva sem aporte declara prazo indisponível", () => {
  const result = calculateReserveJourney({
    currentReserve: 1_000,
    monthlyEssentialExpenses: 2_000,
    monthlyContribution: 0,
    targetMonths: 6,
  });

  assert.equal(result.monthsToTarget, null);
  assert.equal(result.alreadyReached, false);
});

test("compara com e sem aporte sobre a mesma taxa e prazo", () => {
  const result = compareContributionImpact({
    initialAmount: 1_000,
    monthlyContribution: 300,
    annualRatePercent: 10,
    years: 10,
  });

  assert.ok(
    result.withContributions.futureValue >
      result.withoutContributions.futureValue,
  );
  assert.ok(result.difference > 50_000);
});

test("custo anual hipotético reduz a taxa efetiva sem virar tributo", () => {
  const result = compareAnnualCostDrag(
    {
      initialAmount: 10_000,
      monthlyContribution: 500,
      annualRatePercent: 10,
      years: 10,
    },
    1,
  );

  assert.ok(result.netAnnualRatePercent > 8.9);
  assert.ok(result.netAnnualRatePercent < 9);
  assert.ok(result.afterCost.futureValue < result.beforeCost.futureValue);
  assert.ok(result.difference > 0);
  assert.throws(
    () =>
      compareAnnualCostDrag(
        {
          initialAmount: 10_000,
          monthlyContribution: 500,
          annualRatePercent: 2,
          years: 10,
        },
        3,
      ),
    /menor ou igual/,
  );
});
