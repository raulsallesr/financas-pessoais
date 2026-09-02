# Testes móveis

As camadas têm responsabilidades diferentes e não devem ser misturadas:

- `domain/`: contratos e funções puras compilados por `tsconfig.domain.json` e
  executados com `node:test`;
- `components/`: estados, semântica e interação React Native com `jest-expo` e
  React Native Testing Library;
- `e2e/`: validações estáticas dos fluxos Maestro e do mapa canônico de
  seletores;
- `../e2e/maestro/flows/`: jornadas executadas contra um APK Android ou app iOS
  já instalado, sem instrumentar o código do produto.

## Comandos

```powershell
npm run test:domain
npm run test:components
npm run test:e2e:contracts
npm test
```

Com Maestro instalado e um binário `com.raulsallesr.focuslens` aberto em um
emulador, simulador ou aparelho conectado:

```powershell
npm run e2e:maestro
```

No Windows, o executor recomendado descobre o toolchain portátil em
`%LOCALAPPDATA%\focuslens-tools`, valida todos os YAMLs, exige exatamente um
Android autorizado — ou um selecionado explicitamente — e confere
`versionName`/`versionCode` antes de tocar no app:

```powershell
npm run e2e:maestro:check:windows
npm run e2e:maestro:device:windows
npm run e2e:maestro:windows
```

Os caminhos podem ser sobrescritos somente para a sessão por
`FOCUSLENS_JAVA_HOME`, `FOCUSLENS_MAESTRO_HOME` e
`FOCUSLENS_ANDROID_PLATFORM_TOOLS`. Havendo mais de um aparelho, use
`FOCUSLENS_ANDROID_DEVICE`. O script não altera o `PATH` global e não cria build
EAS; ele falha fechado se o pacote ou a versão instalada divergir de
`app.json`. Um mutex também impede duas instâncias locais do Maestro de disputar
a mesma pasta de logs no Windows. `device:windows` para depois da validação ADB,
sem abrir o app. O executor recusa qualquer fluxo com `clearState: true`; as
jornadas versionadas encerram e reabrem somente o processo, preservando todo o
estado local.

`src/testing/testIds.json` é a única fonte dos seletores estáveis. Mudanças de
copy não devem exigir alteração dos fluxos; novos IDs precisam entrar primeiro
nesse mapa e passar por `test:e2e:contracts`.
