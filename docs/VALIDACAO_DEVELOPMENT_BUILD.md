# Validação — FocusLens development build

**Status em 2026-08-28:** configuração nativa concluída; build e validação em
aparelho aguardam autenticação local no Expo/EAS e um Android disponível.

Este documento é a evidência operacional da seção 13 de
`PLANO_FOCUSLENS.md`. Não marca o incremento como concluído enquanto o APK não
for gerado, instalado e validado em aparelho real.

## 1. O que já está configurado

- Expo SDK `57.0.18` e EAS CLI mínimo `23.0.0`;
- `expo-dev-client` compatível com o SDK 57;
- perfil EAS `development`, distribuição interna e APK Android;
- perfil `development-simulator` para a rota de simulador iOS;
- perfil interno `preview` para validar inicialização autônoma e offline;
- identificadores `com.raulsallesr.focuslens` no Android e iOS;
- scheme `focuslens` para abertura pelo development client;
- rotação liberada com `orientation: default`;
- safe areas fornecidas por `react-native-safe-area-context` nos quatro lados;
- splash migrado para o plugin suportado `expo-splash-screen`;
- APK, AAB, IPA, credenciais e pastas nativas geradas ignorados pelo Git.

O `projectId` do EAS ainda não existe porque a máquina não está autenticada. Ele
é um identificador público do projeto, não uma credencial, e poderá ser
versionado depois de `eas init`. Token, senha, chave e sessão permanecem fora do
repositório.

## 2. Bloqueio externo atual

As verificações locais de 2026-08-28 encontraram:

- `eas whoami`: `Not logged in`;
- `adb`: ausente;
- Java/JDK: ausente;
- Android SDK: ausente;
- nenhum APK de development build gerado ou instalado.

Por isso, a rota preferida é EAS Build em nuvem. Não instalar Android Studio,
JDK e SDK completos apenas para contornar a falta de login sem uma decisão
explícita; isso acrescentaria uma cadeia local grande que o projeto não exige.

## 3. Autenticação segura

O Raul deve executar o login no próprio terminal. Não enviar usuário, senha,
token ou código de recuperação pelo chat e não inserir segredo em `app.json`,
`eas.json`, `.env` ou documentação.

```powershell
$nodeRoot = "$env:LOCALAPPDATA\focuslens-tools\node-v24.20.0-win-x64"
$env:Path = "$nodeRoot;$env:Path"
Set-Location "<checkout>\mobile"
npx --yes eas-cli@23.0.0 login
npx --yes eas-cli@23.0.0 whoami
```

Depois de `whoami` identificar a conta correta, o Codex pode continuar a
configuração e os builds sem receber a credencial.

## 4. Vincular o projeto EAS

Executar uma única vez, de forma interativa:

```powershell
npx --yes eas-cli@23.0.0 init
```

Revisar o `owner` e o `extra.eas.projectId` que o comando acrescentar à
configuração. Esses identificadores não são segredos, mas devem apontar para o
projeto FocusLens correto antes do commit.

## 5. Gerar o development build Android

```powershell
npx --yes eas-cli@23.0.0 build --platform android --profile development
```

O perfil gera APK interno com `expo-dev-client`; não publica em loja. O link do
artefato deve ser registrado aqui, sem versionar o arquivo binário.

Depois de instalar o APK, iniciar o Metro no mesmo checkout:

```powershell
npm run start:dev-client
```

O aparelho e o computador devem enxergar a mesma rede. Se a rede local impedir
a conexão, diagnosticar a rota antes de adotar túnel ou outra dependência.

## 6. Instalação no Android

Há duas rotas permitidas:

1. abrir no aparelho o link/QR interno fornecido pelo EAS e autorizar a
   instalação daquela fonte;
2. com Platform Tools instalado e depuração USB autorizada, executar:

```powershell
adb devices
adb install -r <caminho-do-apk>
```

Não versionar o APK. Registrar somente URL do build EAS, identificador, data,
perfil e resultado da instalação.

## 7. Build interno para teste offline

O development client é a bancada de depuração e normalmente carrega o bundle
do Metro. Para confirmar abertura totalmente autônoma, gerar também o perfil
interno `preview`, que incorpora o bundle JavaScript:

```powershell
npx --yes eas-cli@23.0.0 build --platform android --profile preview
```

Com o preview instalado:

1. abrir conectado e confirmar `DADOS PÚBLICOS`, data e fontes;
2. encerrar o app;
3. ativar modo avião;
4. abrir novamente e confirmar que a fotografia empacotada continua visível;
5. confirmar que nenhuma carteira ou rede é necessária para navegar.

O fallback demo para documento ausente, incompatível ou com chave pessoal é
validado automaticamente. Uma reprodução visual em aparelho deve usar um build
temporário de teste; não adulterar nem commitar o snapshot público canônico.

## 8. Checklist em aparelho real

| ID | Verificação | Estado | Evidência esperada |
|---|---|---|---|
| DB-01 | Development APK gerado | Pendente | URL e ID do build EAS |
| DB-02 | APK instalado | Pendente | modelo/Android e resultado |
| DB-03 | Hoje, Carteira, Cenários e Entenda | Pendente | quatro abas abrem sem erro |
| DB-04 | Snapshot empacotado | Pendente | `DADOS PÚBLICOS`, data e fontes |
| DB-05 | Abertura offline | Pendente | preview abre em modo avião |
| DB-06 | Fallback demo | Automatizado | testes de provider aprovados |
| DB-07 | Safe areas | Pendente | nada sob status/gesto/notch |
| DB-08 | Voltar Android | Pendente | aba interna → Hoje; Hoje → sistema |
| DB-09 | Rotação | Pendente | retrato/paisagem sem corte ou overflow |
| DB-10 | TalkBack | Pendente | ordem lógica e controles nomeados |
| DB-11 | Texto ampliado | Pendente | maior tamanho sem conteúdo inacessível |
| DB-12 | Alvos de toque | Pendente | controles acionáveis sem precisão fina |

Registrar nesta tabela somente observação sintética e técnica. Não incluir
posição, valor, conta ou qualquer dado pessoal do aparelho.

## 9. Roteiro de acessibilidade

### Safe areas e rotação

- verificar retrato e paisagem;
- conferir topo, laterais e área do gesto inferior;
- rolar cada aba até o fim e confirmar que a navegação não cobre conteúdo;
- repetir em fonte padrão e no maior tamanho do sistema.

### TalkBack

- percorrer da marca ao conteúdo e depois à navegação inferior;
- confirmar nomes das quatro abas e estado selecionado;
- confirmar rótulos dos sinais, filtros, ocultação de valores e choques;
- verificar que cor não é a única informação de estado;
- garantir rota previsível de retorno.

### Voltar Android

- em Carteira, Cenários ou Entenda, voltar deve levar para Hoje;
- em Hoje, voltar deve ser devolvido ao sistema;
- nenhum toque ou retorno pode apagar ou inventar carteira.

## 10. Rota iOS

Build de desenvolvimento para aparelho físico:

```powershell
npx --yes eas-cli@23.0.0 build --platform ios --profile development
```

Build para simulador:

```powershell
npx --yes eas-cli@23.0.0 build --platform ios --profile development-simulator
```

A geração iOS depende de conta Apple, certificados e ambiente compatíveis. A
rota está documentada, mas não será apresentada como executada sem a evidência
real.

## 11. Evidências automatizadas atuais

- `expo install --check`: dependências compatíveis;
- Expo Doctor: `21/21` checks aprovados;
- TypeScript: aprovado;
- testes móveis: 13 aprovados, incluindo configuração EAS, snapshot empacotado,
  fallback e proibição de carteira pública;
- export Android/Hermes: aprovado com 603 módulos;
- `npm audit --omit=dev --audit-level=high`: zero vulnerabilidade alta ou
  crítica e 11 moderadas transitivas;
- `npm audit fix --force` não foi aplicado: a correção sugerida faria downgrade
  incompatível de pacotes do toolchain, inclusive do Expo.

Essas evidências não substituem DB-01 a DB-05 e DB-07 a DB-12.

## 12. Critério de conclusão

A seção 13 só pode mudar para concluída quando:

- o development APK estiver vinculado a um build EAS identificável;
- o APK estiver instalado em Android real;
- DB-03, DB-04 e DB-07 a DB-12 estiverem aprovados;
- o teste offline estiver aprovado por preview ou evidência equivalente;
- comandos, limitações e rota iOS estiverem atualizados;
- gates Python e móvel passarem no fechamento;
- `CONTEXT.md` registrar o próximo incremento sem antecipar carteira real.

Referências oficiais:

- Expo development builds:
  https://docs.expo.dev/develop/development-builds/create-a-build/
- EAS Build setup:
  https://docs.expo.dev/build/setup/
- Safe area context:
  https://docs.expo.dev/versions/latest/sdk/safe-area-context/
