const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const mobileRoot = path.resolve(__dirname, "..");

function readJson(name) {
  return JSON.parse(fs.readFileSync(path.join(mobileRoot, name), "utf8"));
}

test("configura um development build Android instalável", () => {
  const app = readJson("app.json").expo;
  const eas = readJson("eas.json");
  const packageJson = readJson("package.json");

  assert.equal(app.orientation, "default");
  assert.equal(app.version, "0.4.4");
  assert.equal(packageJson.version, "0.4.4");
  assert.equal(app.scheme, "focuslens");
  assert.equal(app.android.package, "com.raulsallesr.focuslens");
  assert.equal(app.android.versionCode, 8);
  assert.equal(app.ios.bundleIdentifier, "com.raulsallesr.focuslens");
  assert.equal(app.ios.buildNumber, "8");
  assert.equal(app.android.predictiveBackGestureEnabled, true);
  assert.equal(app.splash, undefined);
  assert.deepEqual(app.plugins[0], [
    "expo-splash-screen",
    {
      image: "./assets/focuslens-foreground.png",
      imageWidth: 200,
      resizeMode: "contain",
      backgroundColor: "#F3F7F5",
    },
  ]);
  assert.deepEqual(app.plugins[1], [
    "expo-secure-store",
    { configureAndroidBackup: true, faceIDPermission: false },
  ]);
  assert.equal(packageJson.dependencies.expo, "~57.0.18");
  assert.equal(packageJson.dependencies["expo-crypto"], "~57.0.2");
  assert.equal(packageJson.dependencies["expo-dev-client"], "~57.0.16");
  assert.equal(packageJson.dependencies["expo-document-picker"], "~57.0.1");
  assert.equal(packageJson.dependencies["expo-file-system"], "~57.0.6");
  assert.equal(packageJson.dependencies.fflate, "0.8.3");
  assert.equal(packageJson.dependencies["expo-secure-store"], "~57.0.2");
  assert.equal(packageJson.dependencies["expo-splash-screen"], "~57.0.8");
  assert.equal(
    packageJson.dependencies["react-native-safe-area-context"],
    "~5.7.0",
  );
  assert.equal(eas.build.development.developmentClient, true);
  assert.equal(eas.build.development.distribution, "internal");
  assert.equal(eas.build.development.android.buildType, "apk");
  assert.equal(eas.build["development-simulator"].ios.simulator, true);
  assert.equal(eas.build.preview.distribution, "internal");
  assert.equal(eas.build.preview.android.buildType, "apk");
  assert.equal(eas.build.preview.developmentClient, undefined);
});

test("não versiona segredo na configuração EAS", () => {
  const configText = ["app.json", "eas.json"]
    .map((name) => fs.readFileSync(path.join(mobileRoot, name), "utf8"))
    .join("\n");

  assert.doesNotMatch(configText, /token|password|secret|privateKey/i);
});
