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

`src/testing/testIds.json` é a única fonte dos seletores estáveis. Mudanças de
copy não devem exigir alteração dos fluxos; novos IDs precisam entrar primeiro
nesse mapa e passar por `test:e2e:contracts`.
