# Validação — FocusLens development build

**Status em 2026-08-31:** projeto EAS vinculado; os primeiros APKs `development`
e `preview` foram instalados em POCO X8 Pro. Quatro abas, snapshot e abertura
offline, safe areas em paisagem, rotação e comportamento do botão Voltar foram
aprovados. O preview `v0.4.0` com cofre/importação B3 também foi gerado e
instalado no POCO X8 Pro com Android 16 (`BP2A.250605.031.A3`). TalkBack,
texto ampliado e alvos de toque ainda precisam ser registrados. O preview
`v0.5.2`, build `11`, foi gerado e o Raul confirmou sua instalação; como o
aparelho não estava conectado ao ADB, a versão instalada e as jornadas ainda
não foram verificadas ou avaliadas.

**Pausa de produto:** DB-10 a DB-12 continuam pendentes, mas o Raul decidiu
melhorar primeiro a utilidade do app. A pausa não transforma nenhum item em
aprovado nem invalida as evidências físicas já registradas.

**Decisão posterior em 2026-08-31:** o desenvolvimento local da Etapa 5C foi
autorizado sem fechar DB-10 a DB-12. TalkBack, texto ampliado e alvos de toque
continuam obrigatórios antes do gate de produção.

**Retomada segura preparada em 2026-09-02:** as jornadas Maestro agora usam
`clearState: false`, reiniciam somente o processo e preservam o estado local. O
runner recusa qualquer fluxo destrutivo e permite conferir ADB, package e versão
sem abrir o app. Isso remove o risco de limpeza, mas não aprova nenhum gate
físico sem execução e observação reais.

Este documento é a evidência operacional da seção 13 de
`docs/product/PLANO_FOCUSLENS.md`. Não marca o incremento como concluído enquanto o APK não
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

O projeto EAS é `@raulsallesr/focuslens-br`, com `owner` `raulsallesr` e
`projectId` `a0f97a2a-f26f-4b53-ac1b-fafe4ef27b4b`. Esses identificadores são
públicos e ficam versionados em `app.json`. Token, senha, chave, sessão e
keystore permanecem fora do repositório.

## 2. Estado externo atual

As verificações locais de 2026-08-28 encontraram:

- `eas whoami`: `raulsallesr`;
- `adb`: ausente;
- Java/JDK: ausente;
- Android SDK: ausente;
- APK `development`: instalado e shell do dev client aberto;
- Metro LAN: indisponível porque o firewall corporativo bloqueia entrada e
  aceita somente regras da política central;
- APK `preview`: instalado sobre o development build e validado offline.

A rota EAS Build em nuvem foi concluída sem instalar Android Studio, JDK ou SDK
local. O preview foi a rota funcional para a validação sem depender da rede
corporativa. Não ampliar a cadeia local nem adotar túnel externo sem necessidade.

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

**Executado em 2026-08-28:** login pelo navegador concluído e `whoami`
confirmado como `raulsallesr`. Nenhuma credencial foi registrada no projeto.

## 4. Vincular o projeto EAS

Executar uma única vez, de forma interativa:

```powershell
npx --yes eas-cli@23.0.0 init
```

Revisar o `owner` e o `extra.eas.projectId` que o comando acrescentar à
configuração. Esses identificadores não são segredos, mas devem apontar para o
projeto FocusLens correto antes do commit.

**Executado em 2026-08-28:** criado e vinculado
[`@raulsallesr/focuslens-br`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br).
O diff de `app.json` contém somente o `owner` e o `projectId` públicos.

## 5. Gerar o development build Android

```powershell
npx --yes eas-cli@23.0.0 build --platform android --profile development
```

O perfil gera APK interno com `expo-dev-client`; não publica em loja. O link do
artefato deve ser registrado aqui, sem versionar o arquivo binário.

**Build concluído em 2026-08-28:** perfil `development`, ID
[`1ca28edc-ee9f-4b21-8ec6-6ba8baa9b918`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/1ca28edc-ee9f-4b21-8ec6-6ba8baa9b918),
commit `60fa378`, fingerprint `519796b16038fd44ff83dee56fd0fcb3d868dffd`.
O [APK de desenvolvimento](https://expo.dev/artifacts/eas/E6YGMQWwuHyyqCDzAEcW6Uxt6T4MXUoH0Wq7I_5-CDg.apk)
expira em 2026-09-11. A geração e a instalação posterior pela rota de link EAS
foram aprovadas.

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

**Resultado em 2026-08-28:** development e preview instalados no POCO X8 Pro
pela rota de link EAS. O preview substituiu o development build com a mesma
assinatura e abriu o produto diretamente. O aparelho usa Android 16, build
`BP2A.250605.031.A3`.

## 7. Build interno para teste offline

O development client é a bancada de depuração e normalmente carrega o bundle
do Metro. Para confirmar abertura totalmente autônoma, gerar também o perfil
interno `preview`, que incorpora o bundle JavaScript:

```powershell
npx --yes eas-cli@23.0.0 build --platform android --profile preview
```

**Build concluído em 2026-08-28:** perfil `preview`, ID
[`dd050dbe-5d0d-44e8-aae8-e13f613b7405`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/dd050dbe-5d0d-44e8-aae8-e13f613b7405),
commit `60fa378`, mesmo fingerprint do development build. O
[APK preview](https://expo.dev/artifacts/eas/QEsmnNjXMB21Q4YktNPkdk26UkIj0NN9ey_n75X60mE.apk)
expira em 2026-09-11. A instalação e a validação offline foram aprovadas no
POCO X8 Pro.

**Preview funcional mais recente:** app `0.4.0`, build `4`, EAS
[`c7695638-2f38-42a4-af07-92303f2a5ce0`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/c7695638-2f38-42a4-af07-92303f2a5ce0),
commit `c6bb875`, fingerprint
`4df3790bd18465bb8a429b23f9814aabf1ac6dc8`. O
[APK direto](https://expo.dev/artifacts/eas/25BWk8wQe0mppgR7jumlP4VdI99WJctpNg_Nwjf5Cec.apk)
expira em 2026-09-11. Ele foi instalado no Android 16: CL-02 a CL-10 e BI-01 a
BI-03 foram aprovados; os demais itens estão pendentes.

**Preview anterior de utilidade:** app `0.4.4`, build `8`, EAS
[`6199d700-82ca-44df-8ede-6987679c2566`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/6199d700-82ca-44df-8ede-6987679c2566),
commit `565b071c72fcdd4583fb951f8edd97cbec6dde4b`, fingerprint
`60a05723598a9a039fc90320bcf2a45eb945acaf`. O
[APK direto](https://expo.dev/artifacts/eas/u_SIGIlaaIXgDgQYRd_qNcSgVPPUo7bOdm-TD8k1HNk.apk)
expira em 2026-09-14. O corte traz recorte pessoal antes do mercado, entrada B3
antes da carteira fictícia, alternativa manual, modo discreto entre abas e
resumo de Cenários. O build terminou `FINISHED` sem variáveis `Plain text` ou
`Sensitive`, mas ainda não foi instalado; portanto não existe evidência física
específica deste corte. Ele foi sucedido pelo `v0.5.2/11`; nenhum gate mudou de
estado por causa do build intermediário.

**Preview atual da Etapa 5C:** app `0.5.2`, build `11`, EAS
[`c08e5397-427f-42c2-a163-ab5cd815cb55`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/c08e5397-427f-42c2-a163-ab5cd815cb55),
commit `1c477f5d0c0da3f5980509a2f08f599016ffb1f4`, fingerprint
`4a0bc79db5a2beeb9b694f3ee8718ff13be38dff`. O
[APK direto](https://expo.dev/artifacts/eas/dvVgjSbINj4f3OdJ4CJXx_O651PcG-llvTyurlh0Ytc.apk)
expira em 2026-09-14. O build terminou `FINISHED`, sem variáveis `Plain text` ou
`Sensitive`, e inclui histórico público, favoritos, alertas explicáveis,
simulador de aportes e o harness E2E. O Raul confirmou a instalação por cima do
app em 2026-08-31, mas o ADB encontrou zero aparelhos conectados e não confirmou
package ou versão. Nenhum gate físico mudou de estado apenas por esse relato.

**Preview candidato atual:** app `0.6.4`, build `23`, EAS
[`6ac1268d-5902-46b4-8108-457977bb7e1f`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/6ac1268d-5902-46b4-8108-457977bb7e1f),
commit `a2bb4b5`, fingerprint
`057c832c7452945400ff2d5f2c34b90bf9f3b275`. O build foi submetido em
2026-09-02 e terminou `FINISHED` no mesmo dia. O
[APK direto](https://expo.dev/artifacts/eas/p-3qRdd8j_d0vP5ZBVMeHqXZ2_zMJ5r-9YlSO2IhhSo.apk)
expira em 2026-09-16. O artefato ainda não foi instalado: não registrar package,
versão ou gate físico até ele ser observado no aparelho.

Com o preview instalado:

1. abrir conectado e confirmar `DADOS PÚBLICOS`, data e fontes;
2. encerrar o app;
3. ativar modo avião;
4. abrir novamente e confirmar que a fotografia empacotada continua visível;
5. confirmar que nenhuma carteira ou rede é necessária para navegar.

O fallback demo para documento ausente, incompatível ou com chave pessoal é
validado automaticamente. Uma reprodução visual em aparelho deve usar um build
temporário de teste; não adulterar nem commitar o snapshot público canônico.

**Evidência física em 2026-08-28:** após encerrar o app e ativar modo avião, o
preview reabriu com `DADOS PÚBLICOS`, fotografia, fontes e as quatro abas
navegáveis, sem carteira ou conexão de rede.

## 8. Checklist em aparelho real

| ID | Verificação | Estado | Evidência esperada |
|---|---|---|---|
| DB-01 | Development APK gerado | Aprovado | EAS `1ca28edc-ee9f-4b21-8ec6-6ba8baa9b918`, `FINISHED` |
| DB-02 | APK instalado | Aprovado | development e preview no POCO X8 Pro com Android 16 (`BP2A.250605.031.A3`) |
| DB-03 | Hoje, Carteira, Cenários e Entenda | Aprovado | quatro abas abriram sem erro, inclusive offline |
| DB-04 | Snapshot empacotado | Aprovado | `DADOS PÚBLICOS`, fotografia e fontes visíveis |
| DB-05 | Abertura offline | Aprovado | preview reabriu e navegou em modo avião |
| DB-06 | Fallback demo | Automatizado | testes de provider aprovados |
| DB-07 | Safe areas | Aprovado | retrato e paisagem funcionaram sem conteúdo sob recortes ou gesto inferior |
| DB-08 | Voltar Android | Aprovado | aba interna → Hoje; Hoje → sistema |
| DB-09 | Rotação | Aprovado | retrato/paisagem funcionaram sem corte ou erro |
| DB-10 | TalkBack | Pendente | ordem lógica e controles nomeados |
| DB-11 | Texto ampliado | Pendente | maior tamanho sem conteúdo inacessível |
| DB-12 | Alvos de toque | Pendente | controles acionáveis sem precisão fina |

Registrar nesta tabela somente observação sintética e técnica. Não incluir
posição, valor, conta ou qualquer dado pessoal do aparelho.

**Evidência física adicional em 2026-08-28:** o Raul confirmou no POCO X8 Pro
que rotação, paisagem e comportamento do botão Voltar funcionaram sem erro.
Essa confirmação fecha DB-07 a DB-09, mas não substitui os roteiros específicos
de TalkBack, texto ampliado ou alvos de toque.

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
- testes móveis: 42 de domínio, 6 de componentes e 4 contratos E2E aprovados,
  incluindo configuração EAS, snapshot empacotado, carteira/importação,
  histórico, favoritos, alertas, simulador, seletores e privacidade dos fluxos;
- export Android/Hermes: aprovado com 650 módulos;
- testes Python: 191 aprovados e `pip check` sem dependência quebrada;
- EAS `development`, `preview` público e previews privados até `v0.5.2/11`:
  concluídos sem variável `Plain text` ou `Sensitive` no ambiente de build;
- `npm audit --omit=dev`: zero vulnerabilidade na árvore de produção; a árvore
  completa tem 11 moderadas transitivas e nenhuma alta/crítica;
- `npm audit fix --force` não foi aplicado: a correção sugerida faria downgrade
  incompatível de pacotes do toolchain, inclusive do Expo.

Essas evidências não substituem o fechamento de DB-10 a DB-12.

## 12. Critério de conclusão

A seção 13 só pode mudar para concluída quando:

- o development APK estiver vinculado a um build EAS identificável;
- o APK estiver instalado em Android real;
- DB-03, DB-04 e DB-07 a DB-12 estiverem aprovados;
- o teste offline estiver aprovado por preview ou evidência equivalente;
- comandos, limitações e rota iOS estiverem atualizados;
- gates Python e móvel passarem no fechamento;
- `CONTEXT.md` registrar com honestidade o próximo incremento e os gates que
  continuam pendentes.

Referências oficiais:

- Expo development builds:
  https://docs.expo.dev/develop/development-builds/create-a-build/
- EAS Build setup:
  https://docs.expo.dev/build/setup/
- Safe area context:
  https://docs.expo.dev/versions/latest/sdk/safe-area-context/
