const assert = require("node:assert/strict");
const test = require("node:test");
const { strToU8, zipSync } = require("fflate");

const {
  B3ImportError,
  MAX_B3_FILE_BYTES,
  parseB3Workbook,
} = require("../.test-dist/domain/b3Import.js");

const CONTENT_TYPES = `<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
</Types>`;

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function columnName(index) {
  let value = index + 1;
  let result = "";
  while (value > 0) {
    value -= 1;
    result = String.fromCharCode(65 + (value % 26)) + result;
    value = Math.floor(value / 26);
  }
  return result;
}

function sheetXml(rows, options = {}) {
  const shared = options.shared ?? new Map();
  const dimension = options.dimension ?? `A1:${columnName(rows[0].length - 1)}${rows.length}`;
  const body = rows
    .map((row, rowIndex) => {
      const cells = row
        .map((value, columnIndex) => {
          if (value === null || value === undefined) return "";
          const ref = `${columnName(columnIndex)}${rowIndex + 1}`;
          if (typeof value === "number") {
            return `<c r="${ref}"><v>${value}</v></c>`;
          }
          if (shared.has(value)) {
            return `<c r="${ref}" t="s"><v>${shared.get(value)}</v></c>`;
          }
          return `<c r="${ref}" t="inlineStr"><is><t>${escapeXml(value)}</t></is></c>`;
        })
        .join("");
      return `<row r="${rowIndex + 1}">${cells}</row>`;
    })
    .join("");
  return `<?xml version="1.0" encoding="UTF-8"?>
    <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <dimension ref="${dimension}"/><sheetData>${body}</sheetData>
    </worksheet>`;
}

function workbook(entriesBySheet, options = {}) {
  const sheetEntries = Object.entries(entriesBySheet);
  const workbookSheets = sheetEntries
    .map(
      ([name], index) =>
        `<sheet name="${escapeXml(name)}" sheetId="${index + 1}" r:id="rId${index + 1}"/>`,
    )
    .join("");
  const relationships = sheetEntries
    .map(
      (_entry, index) =>
        `<Relationship Id="rId${index + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${index + 1}.xml"/>`,
    )
    .join("");
  const files = {
    "[Content_Types].xml": strToU8(options.contentTypes ?? CONTENT_TYPES),
    "xl/workbook.xml": strToU8(
      `<?xml version="1.0" encoding="UTF-8"?><workbook xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>${workbookSheets}</sheets></workbook>`,
    ),
    "xl/_rels/workbook.xml.rels": strToU8(
      `<?xml version="1.0" encoding="UTF-8"?><Relationships>${relationships}</Relationships>`,
    ),
  };
  sheetEntries.forEach(([, xml], index) => {
    files[`xl/worksheets/sheet${index + 1}.xml`] = strToU8(xml);
  });
  if (options.sharedStrings) {
    files["xl/sharedStrings.xml"] = strToU8(options.sharedStrings);
  }
  return zipSync(files);
}

function syntheticB3Workbook() {
  return workbook({
    Acoes: sheetXml(
      [
        ["Produto", "Código de Negociação", "Valor Atualizado"],
        ["Empresa energia", "EGIE3 - EMPRESA", 1_000],
        ["Mineradora", "VALE3 - EMPRESA", 200],
        [null, null, 1_200],
      ],
      { dimension: "A1" },
    ),
    Empréstimos: sheetXml([
      ["Produto", "Valor Atualizado"],
      ["VALE3 - EMPRESA", 300],
    ]),
    ETF: sheetXml([
      ["Produto", "Código de Negociação", "Valor Atualizado"],
      ["ETF exterior", "IVVB11 - FUNDO", 400],
      ["ETF cripto", "HASH11 - FUNDO", 500],
      ["ETF ouro", "GOLD11 - FUNDO", 600],
      ["ETF renda fixa", "NLFA11 - FUNDO", 700],
    ]),
    "Fundo de Investimento": sheetXml([
      ["Produto", "Código de Negociação", "Valor Atualizado"],
      ["FII", "MXRF11 - FUNDO", 800],
    ]),
    "Renda Fixa": sheetXml([
      [
        "Produto",
        "Código",
        "Indexador",
        "Valor Atualizado MTM",
        "Valor Atualizado CURVA",
      ],
      ["CFF - FUNDO DE INVESTIMENTO IMOBILIARIO", null, "-", "-", 900],
      ["CDB", "CDB123", "CDI", 1_000, 1_010],
    ]),
    "Tesouro Direto": sheetXml([
      ["Produto", "Valor Atualizado"],
      ["Tesouro IPCA+ 2035", 1_100],
      ["Tesouro Selic 2029", 1_200],
    ]),
  });
}

test("importa, sanitiza e agrega somente as classes cobertas pelo mobile", () => {
  const content = syntheticB3Workbook();
  const original = Uint8Array.from(content);
  const result = parseB3Workbook(content);

  assert.deepEqual(content, original);
  assert.equal(result.positions.length, 9);
  assert.equal(result.validRows, 10);
  assert.equal(result.ignoredRows, 1);
  assert.equal(result.unsupportedRows, 2);
  assert.equal(result.totalAmount, 7_600);
  assert.deepEqual(result.sheetsRead, [
    "Acoes",
    "Empréstimos",
    "ETF",
    "Fundo de Investimento",
    "Renda Fixa",
    "Tesouro Direto",
  ]);

  const byName = new Map(result.positions.map((position) => [position.name, position]));
  assert.equal(byName.get("VALE3").amount, 500);
  assert.equal(byName.get("IVVB11").assetClass, "Exterior / dólar");
  assert.equal(byName.get("NLFA11").assetClass, "Renda fixa pós-fixada");
  assert.equal(byName.get("MXRF11").assetClass, "Fundos imobiliários / FIAGRO");
  assert.equal(byName.get("CFF").assetClass, "Fundos imobiliários / FIAGRO");
  assert.equal(byName.get("Tesouro IPCA+ 2035").assetClass, "Títulos IPCA+");
  assert.equal(byName.get("Tesouro Selic 2029").assetClass, "Renda fixa pós-fixada");
  assert.equal(result.positions.every((position) => /^b3-\d{3}$/.test(position.id)), true);
});

test("lê tabela de textos compartilhados e entidades XML", () => {
  const values = ["Produto", "Código de Negociação", "Valor Atualizado", "Ação & Energia", "EGIE3 - EMPRESA"];
  const shared = new Map(values.map((value, index) => [value, index]));
  const sharedStrings = `<sst>${values.map((value) => `<si><t>${escapeXml(value)}</t></si>`).join("")}</sst>`;
  const content = workbook(
    {
      Acoes: sheetXml(
        [
          ["Produto", "Código de Negociação", "Valor Atualizado"],
          ["Ação & Energia", "EGIE3 - EMPRESA", 123.45],
        ],
        { shared },
      ),
    },
    { sharedStrings },
  );

  const result = parseB3Workbook(content);
  assert.equal(result.positions[0].name, "EGIE3");
  assert.equal(result.positions[0].amount, 123.45);
});

test("rejeita arquivo vazio, conteúdo que não é ZIP e tamanho excessivo", () => {
  assert.throws(() => parseB3Workbook(new Uint8Array()), (error) => {
    assert.equal(error instanceof B3ImportError, true);
    assert.equal(error.code, "empty-file");
    return true;
  });
  assert.throws(() => parseB3Workbook(strToU8("não é XLSX")), /não é uma planilha XLSX válida/);
  assert.throws(
    () => parseB3Workbook(new Uint8Array(MAX_B3_FILE_BYTES + 1)),
    /excede o limite de 5 MB/,
  );
});

test("rejeita pasta de trabalho com macro, declaração XML ou aba desconhecida", () => {
  const macroType = CONTENT_TYPES.replace(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
    "application/vnd.ms-excel.sheet.macroEnabled.main+xml",
  );
  assert.throws(
    () => parseB3Workbook(workbook({ Acoes: sheetXml([["Produto", "Valor Atualizado"], ["Teste", 10]]) }, { contentTypes: macroType })),
    /sem macros/,
  );
  assert.throws(
    () => parseB3Workbook(workbook({ Outra: sheetXml([["Produto", "Valor Atualizado"], ["Teste", 10]]) })),
    /Nenhuma aba reconhecida/,
  );
  assert.throws(
    () => parseB3Workbook(workbook({ Acoes: `<!DOCTYPE x><worksheet></worksheet>` })),
    /declarações XML não permitidas/,
  );
});

test("falha fechado quando a importação ultrapassa o contrato privado", () => {
  const rows = [["Produto", "Código de Negociação", "Valor Atualizado"]];
  for (let index = 0; index < 101; index += 1) {
    rows.push([`Ativo ${index}`, `AT${String(index).padStart(4, "0")} - EMPRESA`, index + 1]);
  }
  assert.throws(
    () => parseB3Workbook(workbook({ Acoes: sheetXml(rows) })),
    /mais de 100 posições/,
  );
});
