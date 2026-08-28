import { AssetClass, Position } from "./types";

export const PRIVATE_PORTFOLIO_SCHEMA_VERSION = 1 as const;
export const MAX_PORTFOLIO_POSITIONS = 100;
export const MAX_POSITION_AMOUNT = 999_999_999_999.99;

export const ASSET_CLASSES: readonly AssetClass[] = [
  "Renda fixa pós-fixada",
  "Renda fixa prefixada",
  "Títulos IPCA+",
  "Fundos imobiliários / FIAGRO",
  "Bolsa brasileira",
  "Exterior / dólar",
];

export type PrivatePortfolioV1 = {
  schemaVersion: typeof PRIVATE_PORTFOLIO_SCHEMA_VERSION;
  updatedAt: string;
  positions: readonly Position[];
};

export type PositionDraft = {
  name: string;
  assetClass: AssetClass | null;
  amountText: string;
};

export type PositionDraftErrors = Partial<
  Record<keyof PositionDraft, string>
>;

export type PositionDraftResult =
  | { ok: true; position: Position }
  | { ok: false; errors: PositionDraftErrors };

const DOCUMENT_KEYS = new Set(["schemaVersion", "updatedAt", "positions"]);
const POSITION_KEYS = new Set(["id", "name", "shortName", "assetClass", "amount"]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasOnlyKeys(value: Record<string, unknown>, allowed: Set<string>): boolean {
  return Object.keys(value).every((key) => allowed.has(key));
}

function isIsoDateTime(value: unknown): value is string {
  return (
    typeof value === "string" &&
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value) &&
    Number.isFinite(Date.parse(value))
  );
}

function isPosition(value: unknown): value is Position {
  return (
    isRecord(value) &&
    hasOnlyKeys(value, POSITION_KEYS) &&
    typeof value.id === "string" &&
    /^[A-Za-z0-9._-]{1,64}$/.test(value.id) &&
    typeof value.name === "string" &&
    value.name.trim() === value.name &&
    value.name.length >= 2 &&
    value.name.length <= 80 &&
    typeof value.shortName === "string" &&
    value.shortName.trim() === value.shortName &&
    value.shortName.length >= 1 &&
    value.shortName.length <= 24 &&
    ASSET_CLASSES.includes(value.assetClass as AssetClass) &&
    typeof value.amount === "number" &&
    Number.isFinite(value.amount) &&
    value.amount > 0 &&
    value.amount <= MAX_POSITION_AMOUNT
  );
}

export function validatePrivatePortfolio(
  document: unknown,
): document is PrivatePortfolioV1 {
  if (
    !isRecord(document) ||
    !hasOnlyKeys(document, DOCUMENT_KEYS) ||
    document.schemaVersion !== PRIVATE_PORTFOLIO_SCHEMA_VERSION ||
    !isIsoDateTime(document.updatedAt) ||
    !Array.isArray(document.positions) ||
    document.positions.length > MAX_PORTFOLIO_POSITIONS ||
    !document.positions.every(isPosition)
  ) {
    return false;
  }

  const ids = document.positions.map((position) => position.id);
  return new Set(ids).size === ids.length;
}

export function createPrivatePortfolio(
  positions: readonly Position[],
  updatedAt = new Date().toISOString(),
): PrivatePortfolioV1 {
  const document: PrivatePortfolioV1 = {
    schemaVersion: PRIVATE_PORTFOLIO_SCHEMA_VERSION,
    updatedAt,
    positions: [...positions],
  };
  if (!validatePrivatePortfolio(document)) {
    throw new Error("A carteira local não respeita o contrato privado v1.");
  }
  return document;
}

export function parsePositionAmount(value: string): number | null {
  const compact = value.trim().replace(/^R\$\s*/i, "").replace(/\s/g, "");
  if (!compact) {
    return null;
  }

  let normalized: string;
  if (compact.includes(",")) {
    if (!/^\d+(?:\.\d{3})*(?:,\d{1,2})?$/.test(compact)) {
      return null;
    }
    normalized = compact.replace(/\./g, "").replace(",", ".");
  } else if (/^\d{1,3}(?:\.\d{3})+$/.test(compact)) {
    normalized = compact.replace(/\./g, "");
  } else {
    if (!/^\d+(?:\.\d{1,2})?$/.test(compact)) {
      return null;
    }
    normalized = compact;
  }

  const amount = Number(normalized);
  if (!Number.isFinite(amount) || amount <= 0 || amount > MAX_POSITION_AMOUNT) {
    return null;
  }
  return Math.round(amount * 100) / 100;
}

function shortNameFor(name: string): string {
  return name.length <= 24 ? name : `${name.slice(0, 23).trimEnd()}…`;
}

export function buildPositionFromDraft(
  draft: PositionDraft,
  id: string,
): PositionDraftResult {
  const errors: PositionDraftErrors = {};
  const name = draft.name.trim().replace(/\s+/g, " ");
  const amount = parsePositionAmount(draft.amountText);

  if (name.length < 2) {
    errors.name = "Informe um nome com pelo menos 2 caracteres.";
  } else if (name.length > 80) {
    errors.name = "Use no máximo 80 caracteres.";
  }
  if (!draft.assetClass || !ASSET_CLASSES.includes(draft.assetClass)) {
    errors.assetClass = "Selecione a classe do ativo.";
  }
  if (amount === null) {
    errors.amountText = "Informe um valor positivo, por exemplo 1.250,50.";
  }
  if (!/^[A-Za-z0-9._-]{1,64}$/.test(id)) {
    throw new Error("O identificador local da posição é inválido.");
  }

  if (Object.keys(errors).length > 0 || !draft.assetClass || amount === null) {
    return { ok: false, errors };
  }
  return {
    ok: true,
    position: {
      id,
      name,
      shortName: shortNameFor(name),
      assetClass: draft.assetClass,
      amount,
    },
  };
}
