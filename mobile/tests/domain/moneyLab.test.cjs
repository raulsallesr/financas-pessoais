const assert = require("node:assert/strict");
const test = require("node:test");

const {
  adjustForInflation,
  calculateRequiredMonthlyContribution,
  compareDelayedStart,
  compareIntuitionChallenge,
  effectiveMonthlyRate,
  monthlyEquivalentForHabit,
  simulateCompoundGrowth,
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
