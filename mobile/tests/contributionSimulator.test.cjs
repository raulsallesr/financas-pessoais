const assert = require("node:assert/strict");
const test = require("node:test");

const {
  simulateClassContribution,
} = require("../.test-dist/domain/contributionSimulator.js");
const { demoSnapshot } = require("../.test-dist/data/demoSnapshot.js");

function rowFor(simulation, assetClass) {
  return simulation.allocations.find((item) => item.assetClass === assetClass);
}

test("simula aporte em uma classe sem alterar a fotografia recebida", () => {
  const original = JSON.stringify(demoSnapshot);
  const simulation = simulateClassContribution(
    demoSnapshot,
    10_000,
    "Renda fixa pós-fixada",
  );
  const target = rowFor(simulation, "Renda fixa pós-fixada");

  assert.equal(simulation.portfolioBefore, 72_500);
  assert.equal(simulation.portfolioAfter, 82_500);
  assert.equal(target.amountBefore, 28_000);
  assert.equal(target.amountAfter, 38_000);
  assert.equal(target.receivesContribution, true);
  assert.ok(target.allocationAfterPercent > target.allocationBeforePercent);
  assert.equal(JSON.stringify(demoSnapshot), original);
});

test("inclui uma classe ainda ausente quando ela recebe o aporte", () => {
  const simulation = simulateClassContribution(
    demoSnapshot,
    5_000,
    "Títulos IPCA+",
  );
  const target = rowFor(simulation, "Títulos IPCA+");

  assert.equal(target.amountBefore, 0);
  assert.equal(target.amountAfter, 5_000);
  assert.equal(target.allocationBeforePercent, 0);
  assert.ok(target.allocationAfterPercent > 0);
});

test("mantém a distribuição simulada fechando em cem por cento", () => {
  const simulation = simulateClassContribution(
    demoSnapshot,
    12_345.67,
    "Bolsa brasileira",
  );
  const totalPercent = simulation.allocations.reduce(
    (total, item) => total + item.allocationAfterPercent,
    0,
  );
  const unchangedClass = rowFor(simulation, "Exterior / dólar");

  assert.ok(Math.abs(totalPercent - 100) < 0.000_001);
  assert.ok(
    unchangedClass.allocationAfterPercent <
      unchangedClass.allocationBeforePercent,
  );
  assert.ok(unchangedClass.deltaPercentagePoints < 0);
});

test(
  "uma carteira vazia parte de zero e chega a cem por cento na classe escolhida",
  () => {
    const simulation = simulateClassContribution(
      { ...demoSnapshot, positions: [] },
      1_000,
      "Exterior / dólar",
    );

    assert.equal(simulation.portfolioBefore, 0);
    assert.equal(simulation.portfolioAfter, 1_000);
    assert.equal(simulation.allocations.length, 1);
    assert.equal(simulation.allocations[0].allocationAfterPercent, 100);
  },
);

test("rejeita valor inválido e classe fora do contrato", () => {
  assert.throws(
    () => simulateClassContribution(demoSnapshot, 0, "Bolsa brasileira"),
    /valor positivo/,
  );
  assert.throws(
    () => simulateClassContribution(demoSnapshot, Number.NaN, "Bolsa brasileira"),
    /valor positivo/,
  );
  assert.throws(
    () => simulateClassContribution(demoSnapshot, 1_000, "Cripto"),
    /contrato do app/,
  );
});
