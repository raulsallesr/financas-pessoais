const assert = require("node:assert/strict");
const test = require("node:test");

const {
  ASSET_CLASSES,
  MAX_PORTFOLIO_POSITIONS,
  buildPositionFromDraft,
  createPrivatePortfolio,
  parsePositionAmount,
  validatePrivatePortfolio,
} = require("../../.test-dist/domain/privatePortfolio.js");
const { decodeUtf8, encodeUtf8 } = require("../../.test-dist/domain/utf8.js");

const VALID_CLASS = "Renda fixa pós-fixada";

function position(id = "local-1") {
  return {
    id,
    name: "Tesouro Selic 2029",
    shortName: "Tesouro Selic 2029",
    assetClass: VALID_CLASS,
    amount: 1_250.5,
  };
}

test("interpreta valores em formatos brasileiros sem aceitar zero ou sinal", () => {
  assert.equal(parsePositionAmount("1.250,50"), 1_250.5);
  assert.equal(parsePositionAmount("R$ 1250,50"), 1_250.5);
  assert.equal(parsePositionAmount("1250.50"), 1_250.5);
  assert.equal(parsePositionAmount("1.000"), 1_000);
  assert.equal(parsePositionAmount("0"), null);
  assert.equal(parsePositionAmount("-100"), null);
  assert.equal(parsePositionAmount("1,234"), null);
});

test("normaliza uma posição e deriva apelido limitado", () => {
  const result = buildPositionFromDraft(
    {
      name: "  Fundo   Imobiliário Muito Longo ABCD11  ",
      assetClass: "Fundos imobiliários / FIAGRO",
      amountText: "10.000,25",
    },
    "local-2",
  );

  assert.equal(result.ok, true);
  assert.equal(result.position.name, "Fundo Imobiliário Muito Longo ABCD11");
  assert.equal(result.position.shortName.length <= 24, true);
  assert.equal(result.position.amount, 10_000.25);
});

test("devolve erros por campo antes de criar uma posição", () => {
  const result = buildPositionFromDraft(
    { name: " ", assetClass: null, amountText: "abc" },
    "local-3",
  );

  assert.equal(result.ok, false);
  assert.deepEqual(Object.keys(result.errors).sort(), [
    "amountText",
    "assetClass",
    "name",
  ]);
});

test("valida o contrato privado v1 e aceita carteira vazia explícita", () => {
  const full = createPrivatePortfolio([position()], "2026-08-28T18:00:00.000Z");
  const empty = createPrivatePortfolio([], "2026-08-28T18:00:00.000Z");

  assert.equal(validatePrivatePortfolio(full), true);
  assert.equal(validatePrivatePortfolio(empty), true);
  assert.equal(full.schemaVersion, 1);
  assert.equal(ASSET_CLASSES.length, 6);
});

test("rejeita duplicidade, classe desconhecida e campos fora do contrato", () => {
  const base = createPrivatePortfolio([position()], "2026-08-28T18:00:00.000Z");

  assert.equal(
    validatePrivatePortfolio({ ...base, positions: [position(), position()] }),
    false,
  );
  assert.equal(
    validatePrivatePortfolio({
      ...base,
      positions: [{ ...position(), assetClass: "Cripto" }],
    }),
    false,
  );
  assert.equal(validatePrivatePortfolio({ ...base, cloudId: "forbidden" }), false);
});

test("limita o tamanho do cofre privado", () => {
  const positions = Array.from({ length: MAX_PORTFOLIO_POSITIONS + 1 }, (_, index) =>
    position(`local-${index}`),
  );
  assert.equal(
    validatePrivatePortfolio({
      schemaVersion: 1,
      updatedAt: "2026-08-28T18:00:00.000Z",
      positions,
    }),
    false,
  );
});

test("preserva UTF-8 sem depender de polyfill do runtime nativo", () => {
  const content = "Tesouro IPCA+ · ação São Paulo 📊";
  assert.equal(decodeUtf8(encodeUtf8(content)), content);
  assert.throws(() => decodeUtf8(Uint8Array.from([0xc0, 0x80])), /UTF-8/);
});
