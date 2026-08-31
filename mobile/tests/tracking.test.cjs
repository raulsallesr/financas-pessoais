const assert = require("node:assert/strict");
const test = require("node:test");

const {
  createFavoriteSignals,
  orderSignalsByFavorites,
  toggleFavoriteSignal,
  validateFavoriteSignals,
} = require("../.test-dist/domain/favorites.js");
const {
  comparePublicSnapshots,
  createPublicSnapshotHistory,
  recordPublicSnapshot,
} = require("../.test-dist/domain/snapshotHistory.js");
const {
  buildExplainableAlert,
} = require("../.test-dist/domain/explainableAlerts.js");
const { demoSnapshot } = require("../.test-dist/data/demoSnapshot.js");
const {
  selectMarketSnapshot,
} = require("../.test-dist/data/snapshotProvider.js");
const liveSnapshot = require("../src/data/liveSnapshot.json");

test("favoritos usam contrato pequeno, único e sem dado de carteira", () => {
  const empty = createFavoriteSignals();
  const first = toggleFavoriteSignal(empty, "focus-selic");
  const second = toggleFavoriteSignal(first, "curva-prefixada");

  assert.deepEqual(second, {
    schemaVersion: 1,
    signalIds: ["focus-selic", "curva-prefixada"],
  });
  assert.equal(validateFavoriteSignals(second), true);
  assert.equal(
    validateFavoriteSignals({ schemaVersion: 1, signalIds: ["focus", "focus"] }),
    false,
  );
  assert.doesNotMatch(JSON.stringify(second), /amount|position|valor/i);
  assert.deepEqual(toggleFavoriteSignal(second, "focus-selic").signalIds, [
    "curva-prefixada",
  ]);
});

test("favoritos aparecem primeiro sem alterar a ordem dos demais sinais", () => {
  const ordered = orderSignalsByFavorites(demoSnapshot.signals, [
    "dolar",
    "focus",
  ]);
  assert.deepEqual(
    ordered.map((signal) => signal.id),
    ["dolar", "focus", "curva", "inflacao"],
  );
});

test("histórico deduplica fotografia pública e nunca recebe carteira", () => {
  const first = createPublicSnapshotHistory();
  const recorded = recordPublicSnapshot(first, liveSnapshot);
  const duplicate = recordPublicSnapshot(recorded, liveSnapshot);

  assert.equal(recorded.snapshots.length, 1);
  assert.equal(duplicate, recorded);
  assert.equal(recorded.snapshots[0].generatedAt, liveSnapshot.generatedAt);
  assert.doesNotMatch(JSON.stringify(recorded), /"positions"|"amount"/i);
});

test("histórico mantém somente as oito fotografias públicas mais recentes", () => {
  const snapshots = Array.from({ length: 10 }, (_, index) => ({
    ...liveSnapshot,
    generatedAt: `2026-08-${String(index + 1).padStart(2, "0")}T12:00:00Z`,
  }));
  const history = createPublicSnapshotHistory(snapshots);

  assert.equal(history.snapshots.length, 8);
  assert.equal(history.snapshots[0].generatedAt, "2026-08-10T12:00:00Z");
  assert.equal(history.snapshots[7].generatedAt, "2026-08-03T12:00:00Z");
});

test("compara fotografias por campos literais sem interpretar percentuais", () => {
  const previous = {
    ...liveSnapshot,
    generatedAt: "2026-08-20T12:00:00Z",
    signals: liveSnapshot.signals.map((signal, index) =>
      index === 0 ? { ...signal, value: "1,90%" } : signal,
    ),
  };
  const comparison = comparePublicSnapshots(liveSnapshot, previous);

  assert.equal(comparison.previous.generatedAt, previous.generatedAt);
  assert.equal(comparison.signalChanges.length, 1);
  assert.deepEqual(comparison.signalChanges[0], {
    id: liveSnapshot.signals[0].id,
    label: liveSnapshot.signals[0].label,
    kind: "changed",
    previousValue: "1,90%",
    currentValue: "1,95%",
  });
});

test("alerta explica prova, alcance e limite sem prometer retorno", () => {
  const alert = buildExplainableAlert(demoSnapshot, "curva");

  assert.equal(alert.affectedPositionCount, 2);
  assert.ok(alert.affectedAllocationPercent > 36);
  assert.match(alert.whatProves, /Tesouro Transparente/);
  assert.match(alert.whereItAffects, /2 posições/);
  assert.match(alert.whatItDoesNotProve, /Não prova retorno futuro/);
});

test("alerta declara ausência de relação quando snapshot não fornece efeito", () => {
  const liveWithDemoPortfolio = selectMarketSnapshot(liveSnapshot);
  const alert = buildExplainableAlert(
    liveWithDemoPortfolio,
    liveWithDemoPortfolio.signals[0].id,
  );

  assert.equal(alert.affectedPositionCount, 0);
  assert.equal(alert.affectedAllocationPercent, 0);
  assert.match(alert.whereItAffects, /Nenhuma relação direta foi classificada/);
});
