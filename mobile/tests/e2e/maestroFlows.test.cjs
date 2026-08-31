const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const mobileRoot = path.resolve(__dirname, "../..");
const maestroRoot = path.join(mobileRoot, "e2e", "maestro");
const flowsRoot = path.join(maestroRoot, "flows");
const testIds = require(path.join(mobileRoot, "src", "testing", "testIds.json"));
const app = JSON.parse(
  fs.readFileSync(path.join(mobileRoot, "app.json"), "utf8"),
).expo;

function flattenStrings(value) {
  if (typeof value === "string") {
    return [value];
  }
  return Object.values(value).flatMap(flattenStrings);
}

function readFlows() {
  return fs
    .readdirSync(flowsRoot)
    .filter((name) => name.endsWith(".yaml"))
    .sort()
    .map((name) => ({
      name,
      content: fs.readFileSync(path.join(flowsRoot, name), "utf8"),
    }));
}

test("workspace Maestro aponta para o mesmo app Android e iOS", () => {
  const config = fs.readFileSync(path.join(maestroRoot, "config.yaml"), "utf8");

  assert.match(config, /^appId: com\.raulsallesr\.focuslens$/m);
  assert.match(config, /flows:\s*\r?\n\s+- "flows\/\*\*\/\*\.yaml"/);
  assert.equal(app.android.package, "com.raulsallesr.focuslens");
  assert.equal(app.ios.bundleIdentifier, "com.raulsallesr.focuslens");
});

test("fluxos usam somente seletores registrados no mapa canônico", () => {
  const knownIds = new Set(flattenStrings(testIds));
  const flows = readFlows();

  assert.deepEqual(
    flows.map((flow) => flow.name),
    ["contribution-simulator.yaml", "navigation-smoke.yaml"],
  );
  for (const flow of flows) {
    const referencedIds = [...flow.content.matchAll(/^\s+id:\s+"([^"]+)"$/gm)].map(
      (match) => match[1],
    );
    assert.ok(referencedIds.length > 0, `${flow.name} precisa usar testID`);
    for (const id of referencedIds) {
      assert.ok(knownIds.has(id), `${flow.name} usa testID não registrado: ${id}`);
    }
  }
});

test("fluxos partem de estado limpo e não carregam dado pessoal", () => {
  const combined = readFlows()
    .map((flow) => flow.content)
    .join("\n");

  assert.equal((combined.match(/clearState: true/g) ?? []).length, 2);
  assert.doesNotMatch(combined, /cpf|cnpj|password|token|secret|accountId/i);
});
