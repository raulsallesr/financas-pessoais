const assert = require("node:assert/strict");
const test = require("node:test");

const {
  ALL_CLASSES,
  allocationByClass,
  availableClasses,
  buildRateScenario,
  impactedAllocation,
  impactsForSignal,
  portfolioTotal,
  signalCoverage,
  summarizeScenarioAllocation,
} = require("../.test-dist/domain/insights.js");
const { demoSnapshot } = require("../.test-dist/data/demoSnapshot.js");

test("resume a carteira sintética sem perder classes", () => {
  assert.equal(portfolioTotal(demoSnapshot), 72_500);
  assert.equal(demoSnapshot.positions.length, 5);
  assert.equal(availableClasses(demoSnapshot).length, 5);
});

test("resume alocação por classe em ordem de peso", () => {
  const allocation = allocationByClass(demoSnapshot);
  assert.equal(allocation.length, 5);
  assert.equal(allocation[0].assetClass, "Renda fixa pós-fixada");
  assert.equal(allocation[0].positionCount, 1);
  assert.ok(Math.abs(allocation[0].allocationPercent - 38.6206) < 0.001);
  assert.ok(
    Math.abs(
      allocation.reduce((total, item) => total + item.allocationPercent, 0) - 100,
    ) < 0.001,
  );
});

test("mede cobertura sem inventar efeito ausente", () => {
  const coverage = signalCoverage(demoSnapshot);
  assert.equal(coverage.positionCount, 5);
  assert.ok(Math.abs(coverage.allocationPercent - 100) < 0.001);

  const noEffects = {
    ...demoSnapshot,
    signals: demoSnapshot.signals.map((signal) => ({ ...signal, effects: {} })),
  };
  assert.deepEqual(signalCoverage(noEffects), {
    allocationPercent: 0,
    positionCount: 0,
  });
});

test("cruza o sinal da curva somente com posições relacionadas", () => {
  const impacts = impactsForSignal(demoSnapshot, "curva", ALL_CLASSES);
  assert.deepEqual(
    impacts.map((item) => item.position.id),
    ["pos-2", "pos-4"],
  );
  assert.ok(Math.abs(impactedAllocation(impacts) - 36.5517) < 0.001);
  assert.ok(impacts.every((item) => item.effect.tone === "positive"));
});

test("filtro de classe não inventa impacto fora do sinal", () => {
  const affected = impactsForSignal(
    demoSnapshot,
    "focus",
    "Renda fixa pós-fixada",
  );
  const unaffected = impactsForSignal(
    demoSnapshot,
    "curva",
    "Exterior / dólar",
  );
  assert.equal(affected.length, 1);
  assert.equal(affected[0].position.shortName, "Selic 2029");
  assert.deepEqual(unaffected, []);
});

test("cenário de juros muda direção sem prometer retorno", () => {
  const rising = buildRateScenario(demoSnapshot, 50);
  const falling = buildRateScenario(demoSnapshot, -50);
  const risingPrefix = rising.impacts.find(
    (item) => item.position.assetClass === "Renda fixa prefixada",
  );
  const fallingPrefix = falling.impacts.find(
    (item) => item.position.assetClass === "Renda fixa prefixada",
  );
  assert.equal(risingPrefix.effect.tone, "attention");
  assert.equal(fallingPrefix.effect.tone, "positive");
  assert.match(rising.explanation, /não uma previsão/);
});

test("resume o cenário por tom e explicita a parcela sem relação", () => {
  const rising = buildRateScenario(demoSnapshot, 50);
  const summary = summarizeScenarioAllocation(demoSnapshot, rising.impacts);
  const attention = summary.byTone.find((item) => item.tone === "attention");
  const positive = summary.byTone.find((item) => item.tone === "positive");

  assert.equal(attention.positionCount, 2);
  assert.ok(Math.abs(attention.allocationPercent - 36.5517) < 0.001);
  assert.equal(positive.positionCount, 1);
  assert.ok(Math.abs(positive.allocationPercent - 38.6206) < 0.001);
  assert.ok(Math.abs(summary.coveredAllocationPercent - 75.1724) < 0.001);
  assert.ok(Math.abs(summary.uncoveredAllocationPercent - 24.8276) < 0.001);
});

test("carteira vazia não vira cem por cento sem cobertura", () => {
  const emptySnapshot = { ...demoSnapshot, positions: [] };
  assert.deepEqual(summarizeScenarioAllocation(emptySnapshot, []), {
    byTone: [],
    coveredAllocationPercent: 0,
    uncoveredAllocationPercent: 0,
  });
});

test("cenário neutro e limites numéricos falham de forma explícita", () => {
  assert.deepEqual(buildRateScenario(demoSnapshot, 0).impacts, []);
  assert.throws(() => buildRateScenario(demoSnapshot, 101), /entre -100 e 100/);
  assert.throws(() => buildRateScenario(demoSnapshot, 12.5), /inteiro/);
});

test("contrato demo tem fonte, data e linguagem não imperativa", () => {
  const ids = new Set(demoSnapshot.signals.map((signal) => signal.id));
  assert.equal(ids.size, demoSnapshot.signals.length);
  for (const signal of demoSnapshot.signals) {
    assert.ok(signal.source);
    assert.ok(signal.updatedAt);
  }
  const content = JSON.stringify(demoSnapshot).toLocaleLowerCase("pt-BR");
  for (const prohibited of ["invista", "compre", "venda", "recomendo"] ) {
    assert.equal(content.includes(prohibited), false, prohibited);
  }
});
