const assert = require("node:assert/strict");
const test = require("node:test");

const { currentSnapshot } = require("../.test-dist/data/currentSnapshot.js");
const { impactsForSignal } = require("../.test-dist/domain/insights.js");
const {
  selectMarketSnapshot,
  validateLiveSnapshot,
} = require("../.test-dist/data/snapshotProvider.js");

function validDocument() {
  return {
    schemaVersion: 1,
    mode: "live",
    generatedAt: "2026-08-27T15:30:00Z",
    asOf: "2026-08-26",
    verdict: "Leitura pública validada",
    verdictSupport: "Uma prova pública sustenta a leitura.",
    proofs: [{ source: "BACEN · Focus", text: "Prova rastreável." }],
    sources: [
      {
        id: "focus",
        label: "BACEN · Focus",
        available: true,
        asOf: "2026-08-21",
        status: "Atualizado",
      },
      {
        id: "curva",
        label: "Tesouro Transparente",
        available: false,
        asOf: null,
        status: "Indisponível",
      },
    ],
    signals: [
      {
        id: "focus-selic",
        label: "Focus · Selic",
        value: "13,75%",
        change: "−0,25 p.p.",
        headline: "Expectativa de Selic caiu",
        explanation: "Leitura histórica e educacional.",
        source: "BACEN · Focus",
        updatedAt: "2026-08-21",
        tone: "positive",
        effects: {
          "Renda fixa pós-fixada": {
            tone: "attention",
            headline: "Leitura pede atenção",
            explanation: "O carrego tende a perder força gradualmente.",
          },
        },
      },
    ],
    limits: ["Não é recomendação."],
    changeConditions: ["Nova fotografia pode mudar a leitura."],
  };
}

test("carrega a fotografia pública empacotada sem acionar fallback", () => {
  assert.equal(currentSnapshot.mode, "live");
  assert.equal(currentSnapshot.fallbackReason, undefined);
  assert.equal(currentSnapshot.positions.length, 5);
  assert.ok(currentSnapshot.signals.length > 0);
  assert.ok(currentSnapshot.sources.length > 0);
});

test("aceita snapshot v1 e combina somente a carteira demo local", () => {
  const document = validDocument();
  const snapshot = selectMarketSnapshot(document);

  assert.equal(validateLiveSnapshot(document), true);
  assert.equal(snapshot.mode, "live");
  assert.equal(snapshot.sourcesAvailable, 1);
  assert.equal(snapshot.sourcesTotal, 2);
  assert.equal(snapshot.positions.length, 5);
  assert.equal(Object.hasOwn(document, "positions"), false);
});

test("versão incompatível ativa fallback demo claramente rotulado", () => {
  const document = { ...validDocument(), schemaVersion: 2 };
  const snapshot = selectMarketSnapshot(document);

  assert.equal(validateLiveSnapshot(document), false);
  assert.equal(snapshot.mode, "demo");
  assert.match(snapshot.fallbackReason, /dados sintéticos locais/);
});

test("documento inválido ou com carteira pública ativa fallback", () => {
  assert.equal(selectMarketSnapshot({}).mode, "demo");
  assert.equal(selectMarketSnapshot("{json inválido").mode, "demo");
  assert.equal(
    selectMarketSnapshot({ ...validDocument(), positions: [{ amount: 1_000 }] }).mode,
    "demo",
  );
});

test("filtro por classe continua íntegro com fotografia live", () => {
  const snapshot = selectMarketSnapshot(validDocument());
  const impacts = impactsForSignal(
    snapshot,
    "focus-selic",
    "Renda fixa pós-fixada",
  );

  assert.equal(impacts.length, 1);
  assert.equal(impacts[0].position.shortName, "Selic 2029");
  assert.equal(
    impactsForSignal(snapshot, "focus-selic", "Exterior / dólar").length,
    0,
  );
});
