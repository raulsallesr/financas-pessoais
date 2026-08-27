const assert = require("node:assert/strict");
const test = require("node:test");

const {
  ALL_CLASSES,
  availableClasses,
  buildRateScenario,
  impactedAllocation,
  impactsForSignal,
  portfolioTotal,
} = require("../.test-dist/domain/insights.js");
const { demoSnapshot } = require("../.test-dist/data/demoSnapshot.js");

test("resume a carteira sintética sem perder classes", () => {
  assert.equal(portfolioTotal(demoSnapshot), 72_500);
  assert.equal(demoSnapshot.positions.length, 5);
  assert.equal(availableClasses(demoSnapshot).length, 5);
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
