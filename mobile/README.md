# FocusLens Mobile

App móvel do FocusLens BR em React Native, Expo e TypeScript. A
experiência responde a uma pergunta simples: **o que o mercado está dizendo e
onde isso encosta na minha carteira?**

![FocusLens Mobile com dados públicos](../docs/assets/focuslens-mobile-v0.2-live.png)

## O que já funciona

- **Hoje:** sinais públicos tocáveis com valor, movimento, data e fonte;
- **origem explícita:** “Dados públicos” quando o contrato vivo é válido e
  “Demonstração” quando o provider precisa usar o fallback local;
- **impacto personalizado:** cada sinal revela somente as posições e classes
  relacionadas na carteira de demonstração;
- **Carteira:** criação, edição e exclusão de posições locais, exposição, peso
  por posição e controle para ocultar valores;
- **cofre privado nativo:** chave no SecureStore e documento `v1` cifrado com
  AES-256-GCM no diretório persistente do app;
- **Cenários:** choque ilustrativo de −100 a +100 bps com mudança imediata da
  leitura por posição;
- **Entenda:** fluxo Sinal → Evidência → Exposição → Limite;
- navegação inferior persistente, alvos de toque de pelo menos 44 px, tema
  claro e nenhuma informação transmitida somente por cor.

O mercado vem de `src/data/liveSnapshot.json`, gerado pelos motores Python a
partir dos caches públicos versionados. O JSON público não contém posição,
quantia ou identificador pessoal. No Android/iOS, uma carteira criada pelo
usuário fica criptografada somente no aparelho; até o primeiro salvamento, o app
usa posições sintéticas claramente rotuladas. O app não conecta conta,
corretora ou Open Finance, não sincroniza carteira e não produz recomendação.

## Como a carteira local é protegida

- a demo nunca é persistida automaticamente;
- a chave AES de 256 bits fica no cofre nativo do sistema;
- o documento privado `v1` fica cifrado com AES-GCM e contexto autenticado;
- a gravação usa arquivo temporário e substituição do destino;
- chave ausente, arquivo alterado ou schema inválido bloqueiam a carteira sem
  misturar a demo;
- “Apagar carteira local” remove arquivo e chave após confirmação;
- a bancada web continua somente em demonstração e não oferece falsa
  persistência segura.

O corte não usa biometria, nuvem, autenticação ou telemetria financeira. Troca
de aparelho e restauração de backup não são prometidas nesta versão.

## Como atualizar a fotografia pública

Na raiz do projeto, usando o `.venv` externo já documentado:

```powershell
$pythonProjeto = "$env:USERPROFILE\.venvs\financas-pessoais\Scripts\python.exe"
& $pythonProjeto gerar_mobile_snapshot.py
```

O comando lê somente `dados/focus_cache.json` e
`dados/curva_prefixada_cache.json`; não consulta rede. A gravação usa UTF-8,
ordenação estável, newline final e substituição atômica. Se o conteúdo público
não mudou, o gerador preserva `generatedAt` e não cria diff de relógio. Para
reproduzir um diagnóstico de defasagem em uma data específica, use
`--reference-date AAAA-MM-DD`.

## Como visualizar agora

Pré-requisito: Node.js LTS.

```powershell
cd mobile
npm ci
npm run web
```

Esse comando abre a mesma árvore de componentes React Native no renderer web e
é o caminho imediato para revisar a experiência. O produto continua sendo
React Native; o renderer web é somente uma bancada de desenvolvimento.

### Atalho validado nesta máquina

No computador de trabalho, o Node portátil e as dependências externas ao
OneDrive já estão preparados. Abra um PowerShell novo e cole:

```powershell
$nodeRoot = "$env:LOCALAPPDATA\focuslens-tools\node-v24.20.0-win-x64"
$env:Path = "$nodeRoot;$env:Path"
$mobileRoot = Join-Path $env:USERPROFILE "OneDrive - FitBank Pagamentos Eletrônicos\Documentos\AI-Handoff-Hub-Starter\01_Projetos\Financas-Pessoais\mobile"
Set-Location -LiteralPath $mobileRoot
npm run web
```

Se o navegador não abrir sozinho, use o endereço exibido pelo Expo no terminal,
normalmente `http://localhost:8081`. `Ctrl+C` encerra o servidor. Essas linhas
precisam ser executadas na mesma janela do PowerShell para que o `npm` portátil
permaneça no `PATH`.

Nesta máquina, `mobile/node_modules` é uma junção local ignorada pelo Git para
`%LOCALAPPDATA%\focuslens-mobile\development\node_modules`. Não remover ou
versionar essa junção. Em outra máquina, prefira um clone curto, como
`C:\dev\financas-pessoais`, e então rode `npm ci` dentro de `mobile/`.

## Como rodar em um aparelho

Este corte usa Expo SDK 57. Para um projeto de produto, o caminho recomendado é
um **development build** próprio, não depender do aplicativo genérico Expo Go.
`eas.json`, `expo-dev-client`, identificadores Android/iOS, safe areas, rotação
e splash nativo já estão configurados. Em 2026-08-28, o projeto
`@raulsallesr/focuslens-br` foi vinculado e os APKs `development` e `preview`
foram gerados e instalados no POCO X8 Pro pela rota de link EAS. O preview
aprovou as quatro abas, o snapshot empacotado e a reabertura em modo avião. Esta
máquina continua sem `adb`, Java ou Android SDK.

Para reproduzir os builds depois de autenticar localmente, sem enviar credencial
pelo chat:

```powershell
npx --yes eas-cli@23.0.0 login
npx --yes eas-cli@23.0.0 init
npx --yes eas-cli@23.0.0 build --platform android --profile development
```

Depois que o development APK estiver instalado, inicie o Metro com:

```powershell
npm run start:dev-client
```

O perfil `preview` gera um APK interno com bundle incorporado para o teste de
abertura offline; não publica em loja. Os IDs, links temporários, instalação,
checklist Android, rota iOS, evidências e limites estão em
[`docs/VALIDACAO_DEVELOPMENT_BUILD.md`](../docs/VALIDACAO_DEVELOPMENT_BUILD.md).

O corte `v0.3.0` adiciona módulos nativos de criptografia, filesystem e
SecureStore; portanto exige um novo APK. O preview anterior continua válido para
o fluxo público/offline, mas não contém o cofre privado.

Se o checkout estiver dentro de OneDrive e a instalação encontrar limites de
caminho, prefira um clone local curto para o desenvolvimento móvel. Nesta
máquina, as dependências foram mantidas fora do OneDrive e ligadas por um
`node_modules` local ignorado pelo Git.

## Gates

```powershell
npm run typecheck
npm run test:domain
npm run export:android
```

O gate atual cobre contrato demo, público e privado, schema incompatível,
documento inválido, proibição de carteira no artefato público, valores e campos
do editor, duplicidade, limite de posições, UTF-8, fallback, cálculo de peso,
filtro por classe, impacto por sinal, configuração EAS/SecureStore, snapshot
empacotado, limites do cenário e linguagem não imperativa. O bundle Android é
gerado pelo Metro sem depender do Streamlit.

## Estrutura

```text
App.tsx                 estado e navegação principal
src/components/         componentes móveis reutilizáveis
src/data/               snapshot vivo, validação/provider e fallback demo
src/domain/             contratos público/privado, filtros e sensibilidade
src/screens/            Hoje, Carteira, Cenários e Entenda
src/storage/            cofre local criptografado para Android/iOS
assets/                 marca determinística em SVG e PNG
tests/                  testes do domínio TypeScript
```

Na raiz, `mobile_snapshot.py` adapta os quatro contratos Python sem alterar os
motores; `gerar_mobile_snapshot.py` é a entrada local de geração. O app importa
o JSON como recurso read-only, valida o schema `1` e só então combina os sinais
com `demoSnapshot.ts` em memória.

A arquitetura e a fronteira entre os motores Python e o app estão em
[`docs/ARQUITETURA_MOBILE.md`](../docs/ARQUITETURA_MOBILE.md).

## Relação com o produto institucional

Este app é o cliente de referência da futura camada **FocusLens Embedded**. Ele
não consome hoje API bancária, Open Finance, autenticação institucional ou
carteira em nuvem. A estratégia aprovada está em
[`docs/ESTRATEGIA_INSTITUCIONAL.md`](../docs/ESTRATEGIA_INSTITUCIONAL.md) e a
arquitetura-alvo em
[`docs/ARQUITETURA_INSTITUCIONAL.md`](../docs/ARQUITETURA_INSTITUCIONAL.md).
O próximo passo é gerar e validar o preview `v0.3.0` no POCO X8 Pro, fechar
TalkBack, texto ampliado e alvos de toque, e então implementar a importação B3
sanitizada sem antecipar a camada institucional.
