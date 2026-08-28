import { unzipSync } from "fflate";

import {
  buildPositionFromDraft,
  MAX_PORTFOLIO_POSITIONS,
  MAX_POSITION_AMOUNT,
} from "./privatePortfolio";
import { AssetClass, Position } from "./types";
import { decodeUtf8 } from "./utf8";

export const MAX_B3_FILE_BYTES = 5_000_000;

const MAX_SELECTED_XML_BYTES = 25_000_000;
const MAX_XML_ENTRY_BYTES = 8_000_000;
const MAX_SELECTED_ENTRIES = 64;
const MAX_WORKBOOK_ROWS = 10_000;
const MAX_WORKBOOK_CELLS = 200_000;
const MAX_SHARED_STRINGS = 50_000;

const SUPPORTED_SHEETS = new Set([
  "Acoes",
  "Empréstimos",
  "ETF",
  "Fundo de Investimento",
  "Renda Fixa",
  "Tesouro Direto",
]);

const VALUE_COLUMNS: Readonly<Record<string, readonly string[]>> = {
  Acoes: ["Valor Atualizado"],
  Empréstimos: ["Valor Atualizado"],
  ETF: ["Valor Atualizado"],
  "Fundo de Investimento": ["Valor Atualizado"],
  "Renda Fixa": [
    "Valor Atualizado MTM",
    "Valor Atualizado CURVA",
    "Valor Atualizado FECHAMENTO",
  ],
  "Tesouro Direto": ["Valor Atualizado", "Valor líquido", "Valor bruto"],
};

const CRYPTO_ETFS = new Set(["COIN11", "QBTC11", "HASH11"]);
const GOLD_ETFS = new Set(["GOLD11"]);
const REAL_ESTATE_ETFS = new Set(["XFIX11"]);
const FIXED_INCOME_ETFS = new Set(["NLFA11"]);
const FOREIGN_ETFS = new Set([
  "ACWI11",
  "ALUG11",
  "IVVB11",
  "NASD11",
  "QQQI11",
  "SPYI11",
  "WRLD11",
]);

export type B3ImportErrorCode =
  | "empty-file"
  | "file-too-large"
  | "invalid-file"
  | "unsupported-portfolio"
  | "portfolio-too-large";

export class B3ImportError extends Error {
  constructor(
    public readonly code: B3ImportErrorCode,
    message: string,
  ) {
    super(message);
    this.name = "B3ImportError";
  }
}

export type B3ImportResult = {
  positions: readonly Position[];
  validRows: number;
  ignoredRows: number;
  unsupportedRows: number;
  sheetsRead: readonly string[];
  totalAmount: number;
};

type ArchiveEntries = Readonly<Record<string, Uint8Array>>;
type CellValue = string | number | null;
type SheetRelationship = { name: string; path: string };
type SheetParseResult = {
  rows: readonly Readonly<Record<string, CellValue>>[];
  cellsRead: number;
};

function isSelectedEntry(name: string): boolean {
  return (
    name === "[Content_Types].xml" ||
    name === "xl/workbook.xml" ||
    name === "xl/_rels/workbook.xml.rels" ||
    name === "xl/sharedStrings.xml" ||
    /^xl\/worksheets\/[^/]+\.xml$/.test(name)
  );
}

function unzipWorkbook(content: Uint8Array): ArchiveEntries {
  if (content.byteLength === 0) {
    throw new B3ImportError("empty-file", "A planilha escolhida está vazia.");
  }
  if (content.byteLength > MAX_B3_FILE_BYTES) {
    throw new B3ImportError(
      "file-too-large",
      "A planilha excede o limite de 5 MB para processamento local.",
    );
  }
  if (content[0] !== 0x50 || content[1] !== 0x4b) {
    throw new B3ImportError(
      "invalid-file",
      "O arquivo não é uma planilha XLSX válida.",
    );
  }

  let selectedBytes = 0;
  let selectedEntries = 0;
  try {
    return unzipSync(content, {
      filter(file) {
        const normalizedName = file.name.replace(/\\/g, "/");
        if (!isSelectedEntry(normalizedName)) {
          return false;
        }
        selectedEntries += 1;
        selectedBytes += file.originalSize;
        if (
          selectedEntries > MAX_SELECTED_ENTRIES ||
          file.originalSize > MAX_XML_ENTRY_BYTES ||
          selectedBytes > MAX_SELECTED_XML_BYTES
        ) {
          throw new B3ImportError(
            "invalid-file",
            "A planilha expandida excede os limites seguros de leitura.",
          );
        }
        return true;
      },
    });
  } catch (error) {
    if (error instanceof B3ImportError) {
      throw error;
    }
    throw new B3ImportError(
      "invalid-file",
      "O arquivo não é uma planilha XLSX íntegra.",
    );
  }
}

function entry(entries: ArchiveEntries, name: string): Uint8Array | null {
  return entries[name] ?? entries[name.replace(/\//g, "\\")] ?? null;
}

function xmlText(bytes: Uint8Array | null, label: string): string {
  if (!bytes) {
    throw new B3ImportError(
      "invalid-file",
      `A planilha não contém ${label}.`,
    );
  }
  let xml: string;
  try {
    xml = decodeUtf8(bytes);
  } catch {
    throw new B3ImportError(
      "invalid-file",
      `O XML de ${label} não está em UTF-8 válido.`,
    );
  }
  if (/<!DOCTYPE|<!ENTITY/i.test(xml)) {
    throw new B3ImportError(
      "invalid-file",
      "A planilha contém declarações XML não permitidas.",
    );
  }
  return xml;
}

function decodeXmlEntities(value: string): string {
  return value.replace(
    /&(#x[0-9a-f]+|#\d+|amp|lt|gt|quot|apos);/gi,
    (entity, token: string) => {
      const normalized = token.toLowerCase();
      if (normalized === "amp") return "&";
      if (normalized === "lt") return "<";
      if (normalized === "gt") return ">";
      if (normalized === "quot") return '"';
      if (normalized === "apos") return "'";
      const codePoint = normalized.startsWith("#x")
        ? Number.parseInt(normalized.slice(2), 16)
        : Number.parseInt(normalized.slice(1), 10);
      if (
        !Number.isInteger(codePoint) ||
        codePoint < 0 ||
        codePoint > 0x10ffff ||
        (codePoint >= 0xd800 && codePoint <= 0xdfff)
      ) {
        throw new B3ImportError(
          "invalid-file",
          "A planilha contém uma entidade XML inválida.",
        );
      }
      return String.fromCodePoint(codePoint);
    },
  );
}

function attributes(fragment: string): Readonly<Record<string, string>> {
  const result: Record<string, string> = {};
  const pattern = /([A-Za-z_:][A-Za-z0-9_.:-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')/g;
  for (const match of fragment.matchAll(pattern)) {
    result[match[1]] = decodeXmlEntities(match[2] ?? match[3] ?? "");
  }
  return result;
}

function textNodes(fragment: string): string {
  const values: string[] = [];
  const pattern = /<(?:[A-Za-z_][\w.-]*:)?t\b[^>]*>([\s\S]*?)<\/(?:[A-Za-z_][\w.-]*:)?t>/g;
  for (const match of fragment.matchAll(pattern)) {
    values.push(decodeXmlEntities(match[1]));
  }
  return values.join("");
}

function parseSharedStrings(xml: string | null): readonly string[] {
  if (!xml) {
    return [];
  }
  const values: string[] = [];
  const pattern = /<(?:[A-Za-z_][\w.-]*:)?si\b[^>]*>([\s\S]*?)<\/(?:[A-Za-z_][\w.-]*:)?si>/g;
  for (const match of xml.matchAll(pattern)) {
    values.push(textNodes(match[1]));
    if (values.length > MAX_SHARED_STRINGS) {
      throw new B3ImportError(
        "invalid-file",
        "A tabela de textos da planilha excede o limite seguro.",
      );
    }
  }
  return values;
}

function relationshipPath(target: string): string | null {
  const normalized = target.replace(/\\/g, "/");
  const parts = normalized.startsWith("/") ? [] : ["xl"];
  for (const part of normalized.replace(/^\//, "").split("/")) {
    if (!part || part === ".") {
      continue;
    }
    if (part === "..") {
      if (parts.length === 0) {
        return null;
      }
      parts.pop();
      continue;
    }
    parts.push(part);
  }
  const path = parts.join("/");
  return /^xl\/worksheets\/[^/]+\.xml$/.test(path) ? path : null;
}

function workbookSheets(workbookXml: string, relationshipsXml: string): readonly SheetRelationship[] {
  const pathsById = new Map<string, string>();
  const relationshipPattern = /<(?:[A-Za-z_][\w.-]*:)?Relationship\b([^>]*)\/?\s*>/g;
  for (const match of relationshipsXml.matchAll(relationshipPattern)) {
    const attrs = attributes(match[1]);
    if (!attrs.Id || !attrs.Target || !attrs.Type?.endsWith("/worksheet")) {
      continue;
    }
    const path = relationshipPath(attrs.Target);
    if (path) {
      pathsById.set(attrs.Id, path);
    }
  }

  const sheets: SheetRelationship[] = [];
  const sheetPattern = /<(?:[A-Za-z_][\w.-]*:)?sheet\b([^>]*)\/?\s*>/g;
  for (const match of workbookXml.matchAll(sheetPattern)) {
    const attrs = attributes(match[1]);
    const relationshipId = attrs["r:id"] ?? attrs.id;
    const path = relationshipId ? pathsById.get(relationshipId) : undefined;
    if (attrs.name && SUPPORTED_SHEETS.has(attrs.name) && path) {
      sheets.push({ name: attrs.name, path });
    }
  }
  return sheets;
}

function columnIndex(reference: string): number | null {
  const match = /^([A-Z]+)\d+$/i.exec(reference);
  if (!match) {
    return null;
  }
  let value = 0;
  for (const character of match[1].toUpperCase()) {
    value = value * 26 + character.charCodeAt(0) - 64;
  }
  return value - 1;
}

function cellValue(
  cellAttributes: Readonly<Record<string, string>>,
  body: string,
  sharedStrings: readonly string[],
): CellValue {
  if (cellAttributes.t === "inlineStr") {
    return textNodes(body);
  }
  const valueMatch = /<(?:[A-Za-z_][\w.-]*:)?v\b[^>]*>([\s\S]*?)<\/(?:[A-Za-z_][\w.-]*:)?v>/.exec(body);
  if (!valueMatch) {
    return null;
  }
  const raw = decodeXmlEntities(valueMatch[1]).trim();
  if (cellAttributes.t === "s") {
    const index = Number.parseInt(raw, 10);
    if (!Number.isInteger(index) || index < 0 || index >= sharedStrings.length) {
      throw new B3ImportError(
        "invalid-file",
        "A planilha referencia um texto inexistente.",
      );
    }
    return sharedStrings[index];
  }
  if (cellAttributes.t === "str" || cellAttributes.t === "e") {
    return raw;
  }
  const numeric = Number(raw);
  return Number.isFinite(numeric) ? numeric : raw;
}

function rowCells(
  rowBody: string,
  sharedStrings: readonly string[],
): ReadonlyMap<number, CellValue> {
  const values = new Map<number, CellValue>();
  const cellPattern = /<(?:[A-Za-z_][\w.-]*:)?c\b([^>]*)>([\s\S]*?)<\/(?:[A-Za-z_][\w.-]*:)?c>/g;
  let sequentialIndex = 0;
  for (const match of rowBody.matchAll(cellPattern)) {
    const attrs = attributes(match[1]);
    const referencedIndex = attrs.r ? columnIndex(attrs.r) : null;
    const index = referencedIndex ?? sequentialIndex;
    values.set(index, cellValue(attrs, match[2], sharedStrings));
    sequentialIndex = index + 1;
  }
  return values;
}

function cleanText(value: CellValue | undefined): string {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value).trim().replace(/\s+/g, " ");
}

function parseWorksheet(
  xml: string,
  sheetName: string,
  sharedStrings: readonly string[],
): SheetParseResult {
  const rows: Readonly<Record<string, CellValue>>[] = [];
  const valueColumns = VALUE_COLUMNS[sheetName];
  let headers: ReadonlyMap<number, string> | null = null;
  let rowsSeen = 0;
  let cellsRead = 0;
  const rowPattern = /<(?:[A-Za-z_][\w.-]*:)?row\b[^>]*>([\s\S]*?)<\/(?:[A-Za-z_][\w.-]*:)?row>/g;

  for (const match of xml.matchAll(rowPattern)) {
    rowsSeen += 1;
    if (rowsSeen > MAX_WORKBOOK_ROWS) {
      throw new B3ImportError(
        "invalid-file",
        "A planilha excede o limite de linhas para importação local.",
      );
    }
    const cells = rowCells(match[1], sharedStrings);
    cellsRead += cells.size;
    if (cellsRead > MAX_WORKBOOK_CELLS) {
      throw new B3ImportError(
        "invalid-file",
        "A planilha excede o limite de células para importação local.",
      );
    }

    if (!headers) {
      const candidate = new Map<number, string>();
      for (const [index, value] of cells) {
        candidate.set(index, cleanText(value));
      }
      const names = [...candidate.values()];
      if (
        names.includes("Produto") &&
        valueColumns.some((column) => names.includes(column))
      ) {
        headers = candidate;
      }
      continue;
    }

    const record: Record<string, CellValue> = {};
    for (const [index, value] of cells) {
      const header = headers.get(index);
      if (header) {
        record[header] = value;
      }
    }
    rows.push(record);
  }

  return { rows: headers ? rows : [], cellsRead };
}

function positiveNumber(value: CellValue | undefined): number | null {
  if (typeof value === "number") {
    return Number.isFinite(value) && value > 0 ? value : null;
  }
  const text = cleanText(value).replace(/^R\$\s*/i, "").replace(/\s/g, "");
  if (!text || text === "-") {
    return null;
  }
  const normalized = text.includes(",")
    ? text.replace(/\./g, "").replace(",", ".")
    : text;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function shortCode(...values: readonly CellValue[]): string {
  const text = values.map(cleanText).find(Boolean) ?? "";
  const prefix = text.split(" - ", 1)[0].trim();
  return /^[A-Z0-9]{3,12}$/.test(prefix) ? prefix : text.slice(0, 80);
}

function normalizedText(value: string): string {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toUpperCase();
}

function classifyPosition(
  sheetName: string,
  asset: string,
  product: string,
  indexer: string,
): AssetClass | null {
  const text = normalizedText(`${asset} ${product} ${indexer}`);
  if (
    text.includes("FUNDO DE INVESTIMENTO IMOBILIARIO") ||
    sheetName === "Fundo de Investimento"
  ) {
    return "Fundos imobiliários / FIAGRO";
  }
  if (sheetName === "Acoes" || sheetName === "Empréstimos") {
    return "Bolsa brasileira";
  }
  if (sheetName === "ETF") {
    if (
      CRYPTO_ETFS.has(asset) ||
      text.includes("BITCOIN") ||
      text.includes("CRYPTO") ||
      text.includes("CRIPTO") ||
      GOLD_ETFS.has(asset) ||
      text.includes("OURO") ||
      text.includes("GOLD")
    ) {
      return null;
    }
    if (REAL_ESTATE_ETFS.has(asset) || text.includes("IFIX")) {
      return "Fundos imobiliários / FIAGRO";
    }
    if (FIXED_INCOME_ETFS.has(asset)) {
      return "Renda fixa pós-fixada";
    }
    if (FOREIGN_ETFS.has(asset)) {
      return "Exterior / dólar";
    }
    return "Bolsa brasileira";
  }
  if (sheetName === "Tesouro Direto") {
    if (text.includes("IPCA") || text.includes("RENDA+")) {
      return "Títulos IPCA+";
    }
    if (text.includes("SELIC")) {
      return "Renda fixa pós-fixada";
    }
    return "Renda fixa prefixada";
  }
  if (sheetName === "Renda Fixa") {
    if (text.includes("CDI") || text.includes("SELIC")) {
      return "Renda fixa pós-fixada";
    }
    if (text.includes("IPCA") || text.includes("IGP-M") || text.includes("IGPM")) {
      return "Títulos IPCA+";
    }
    return "Renda fixa prefixada";
  }
  return null;
}

export function parseB3Workbook(content: Uint8Array): B3ImportResult {
  const entries = unzipWorkbook(content);
  const contentTypes = xmlText(
    entry(entries, "[Content_Types].xml"),
    "a declaração de conteúdo XLSX",
  );
  if (
    !contentTypes.includes(
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
    )
  ) {
    throw new B3ImportError(
      "invalid-file",
      "O arquivo não é uma pasta de trabalho XLSX sem macros.",
    );
  }

  const workbookXml = xmlText(
    entry(entries, "xl/workbook.xml"),
    "a definição da pasta de trabalho",
  );
  const relationshipsXml = xmlText(
    entry(entries, "xl/_rels/workbook.xml.rels"),
    "os vínculos internos da pasta de trabalho",
  );
  const sharedBytes = entry(entries, "xl/sharedStrings.xml");
  const sharedStrings = parseSharedStrings(
    sharedBytes ? xmlText(sharedBytes, "a tabela de textos") : null,
  );
  const sheets = workbookSheets(workbookXml, relationshipsXml);
  const aggregated = new Map<
    string,
    { name: string; assetClass: AssetClass; amount: number }
  >();
  const sheetsRead: string[] = [];
  let validRows = 0;
  let ignoredRows = 0;
  let unsupportedRows = 0;
  let totalCellsRead = 0;

  for (const sheet of sheets) {
    const sheetXml = xmlText(entry(entries, sheet.path), `a aba ${sheet.name}`);
    const parsed = parseWorksheet(sheetXml, sheet.name, sharedStrings);
    totalCellsRead += parsed.cellsRead;
    if (totalCellsRead > MAX_WORKBOOK_CELLS) {
      throw new B3ImportError(
        "invalid-file",
        "A planilha excede o limite total de células para importação local.",
      );
    }
    if (parsed.rows.length === 0) {
      continue;
    }
    sheetsRead.push(sheet.name);
    for (const record of parsed.rows) {
      const product = cleanText(record.Produto);
      const asset = shortCode(
        record["Código de Negociação"],
        record.Código,
        record.Produto,
      );
      const amount = VALUE_COLUMNS[sheet.name]
        .map((column) => positiveNumber(record[column]))
        .find((value): value is number => value !== null);
      if ((!product && !asset) || amount === undefined) {
        ignoredRows += 1;
        continue;
      }
      const assetClass = classifyPosition(
        sheet.name,
        asset,
        product,
        cleanText(record.Indexador),
      );
      if (!assetClass) {
        unsupportedRows += 1;
        continue;
      }
      validRows += 1;
      const name = (asset || product).slice(0, 80);
      const key = `${assetClass}\u0000${name}`;
      const previous = aggregated.get(key);
      const aggregatedAmount = Math.round(((previous?.amount ?? 0) + amount) * 100) / 100;
      if (aggregatedAmount > MAX_POSITION_AMOUNT) {
        throw new B3ImportError(
          "portfolio-too-large",
          `A posição ${name} excede o valor máximo aceito pelo cofre local.`,
        );
      }
      aggregated.set(key, { name, assetClass, amount: aggregatedAmount });
    }
  }

  if (sheetsRead.length === 0) {
    throw new B3ImportError(
      "invalid-file",
      "Nenhuma aba reconhecida da posição B3 foi encontrada.",
    );
  }
  if (aggregated.size === 0) {
    throw new B3ImportError(
      unsupportedRows > 0 ? "unsupported-portfolio" : "invalid-file",
      unsupportedRows > 0
        ? "As posições encontradas usam classes ainda não cobertas pelo FocusLens Mobile."
        : "A planilha não contém posições com valor atualizado positivo.",
    );
  }
  if (aggregated.size > MAX_PORTFOLIO_POSITIONS) {
    throw new B3ImportError(
      "portfolio-too-large",
      `A planilha gera mais de ${MAX_PORTFOLIO_POSITIONS} posições. Revise o arquivo antes de importar.`,
    );
  }

  const positions = [...aggregated.values()]
    .sort((left, right) => right.amount - left.amount || left.name.localeCompare(right.name))
    .map((item, index) => {
      const result = buildPositionFromDraft(
        {
          name: item.name,
          assetClass: item.assetClass,
          amountText: item.amount.toFixed(2),
        },
        `b3-${String(index + 1).padStart(3, "0")}`,
      );
      if (!result.ok) {
        throw new B3ImportError(
          "invalid-file",
          "Uma posição importada não respeita o contrato privado do app.",
        );
      }
      return result.position;
    });

  return {
    positions,
    validRows,
    ignoredRows,
    unsupportedRows,
    sheetsRead,
    totalAmount: positions.reduce((total, position) => total + position.amount, 0),
  };
}
