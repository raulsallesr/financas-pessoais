# CONTEXT — Finanças Pessoais

- **Status**: motores FocusLens BR `v2.0` preservados como release candidate.
  A Etapa 5 móvel possui fundação React Native `v0.1` e contrato vivo `v1`
  concluídos em 2026-08-27. A configuração do development build foi concluída
  em 2026-08-28; os primeiros APKs `development` e `preview` foram instalados no
  POCO X8 Pro com Android 16 (`BP2A.250605.031.A3`). Quatro abas, snapshot,
  offline, rotação, paisagem e Voltar passaram; TalkBack, texto ampliado e alvos
  de toque ainda aguardam evidência.
  O corte móvel `v0.4.0` já implementa editor, cofre local criptografado e
  importação B3 sanitizada com prévia; o APK foi instalado, BI-01 a BI-03 e
  CL-02 a CL-10 foram aprovados no aparelho, mas o restante do ciclo físico
  continua pendente. O preview mais recente `v0.5.2`, build `11`, foi gerado em
  2026-08-31 e o Raul confirmou a instalação no aparelho; a versão instalada não
  foi conferida por ADB e o corte ainda não recebeu avaliação física. Por decisão explícita do
  Raul em 2026-08-31, o desenvolvimento da Etapa 5C chegou ao corte local
  `v0.6.0`: além da revisão semanal, Cenários oferece nove caminhos educacionais
  com crescimento composto, metas, tempo, inflação, hábitos, aportes extras,
  reserva e comparações de custo. Valores e progresso ficam somente na sessão.
  Os dois fluxos Maestro continuam prontos para o binário nativo. O
  toolchain Windows portátil foi instalado e os dois YAMLs passaram no Maestro
  `2.9.0`; a última consulta ADB encontrou zero aparelhos conectados. A execução
  das jornadas e os gates físicos
  anteriores continuam pendentes, sem serem inferidos como aprovados. O roadmap
  institucional **FocusLens Embedded** foi aprovado e
  documentado, mas permanece posterior aos gates móveis. Tag, release e
  abertura pública da `v2.0` continuam aguardando licença e decisão sobre
  e-mail histórico.
- **Repositório**: https://github.com/raulsallesr/financas-pessoais (privado)
- **Fonte oficial**: BACEN, Sistema de Expectativas de Mercado (Boletim
  Focus), API pública Olinda/OData
  (`https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata`),
  sem autenticação.
- **Periodicidade**: BACEN publica o Boletim Focus toda segunda-feira; a API
  tem granularidade diária, então o app permite atualizar a qualquer momento.
- **Curva oficial**: Tesouro Transparente, conjunto diário “Taxas dos Títulos
  Ofertados pelo Tesouro Direto”, CSV aberto sob ODbL 1.0.

## Handoff para um novo chat — 2026-09-01

### Ponto de partida verificado

- O produto está estável e versionado até a `v1.14`; o commit funcional dessa
  entrega é `0f1458c` e recebeu a tag `v1.14`.
- A branch de trabalho é `main`. `git pull --ff-only` avançou em 2026-09-01 até
  `85a2b48`, trazendo somente os dois caches públicos antes deste trabalho. O corte
  funcional anterior a este registro de handoff é `0bd94ee`; o APK `v0.4.0`
  foi construído a partir de `c6bb875`.
- A **Etapa 4 — FocusLens BR integrado (`v2.0`)** está concluída tecnicamente
  como release candidate. Não refazer as Etapas 1–3 nem os cinco incrementos
  da Etapa 4.
- O Raul redirecionou explicitamente o produto para um app móvel em
  2026-08-27. `mobile/` contém a fundação React Native/Expo/TypeScript com Hoje,
  Carteira, Cenários e Entenda. Streamlit é referência funcional dos motores,
  não a interface final.
- A implementação da fundação móvel `v0.1` está no commit `2c242b8`. Ela passou
  por 185 testes Python, `py_compile`, `pip check`, TypeScript, 6 testes de
  domínio móvel, export do bundle Android e validação visual em 375×812,
  430×932, 768×1024 e 844×390, sem overflow horizontal. A captura aprovada está
  em `docs/assets/focuslens-mobile-v0.1.png`.
- O incremento 2 da Etapa 5 está concluído. `mobile_snapshot.py` adapta
  `ResumoIntegrado`, `ResumoFocusSemanal`, `LeituraCurva` e
  `LeituraConvergencia`; `gerar_mobile_snapshot.py` lê somente os caches
  públicos e grava `mobile/src/data/liveSnapshot.json` de forma atômica.
- `snapshotProvider.ts` valida schema, campos, datas, fontes, sinais e ausência
  de carteira. Documento ausente, incompatível, inválido ou com chave pessoal
  ativa a demo sintética e mostra o motivo; um contrato válido recebe as
  posições demo somente em memória.
- O fechamento do contrato vivo passou por 191 testes Python, 10 testes móveis,
  `py_compile`, `pip check`, TypeScript, bundle Android e `git diff --check`.
  A Home foi validada em 375×812, 430×932, 768×1024 e 844×390, sempre com
  `scrollWidth == clientWidth`. A captura viva está em
  `docs/assets/focuslens-mobile-v0.2-live.png`.
- Este fechamento revalidou a suíte Python completa, `pip check`, TypeScript,
  os 25 testes móveis, o bundle Android/Hermes com 640 módulos, os links locais
  de 11 documentos canônicos, a ausência de chaves pessoais no snapshot
  público, o scanner de assinaturas de segredo e `git diff --check`. O primeiro
  pytest encontrou `WinError 5` apenas no temporário do sandbox e o primeiro
  export encontrou `spawn EPERM` ao iniciar o Hermes; ambos passaram fora do
  sandbox, sem mudança de código. `.test-dist` e `dist-android` foram removidos
  após os gates; `mobile/node_modules` permanece como junction local válida e
  não versionada.
- `npm run web` já permite testar a mesma árvore de componentes React Native no
  navegador. Os APKs internos `development` e `preview` foram instalados e
  validados no POCO X8 Pro; a bancada web continua apenas como apoio visual.
- A configuração da seção 13 foi preparada em 2026-08-28: `eas.json` possui
  perfis `development`, `development-simulator` e `preview`; `app.json` possui
  identificadores `com.raulsallesr.focuslens`, scheme, rotação e splash por
  plugin; `App.tsx` usa `react-native-safe-area-context` nos quatro lados.
- O Expo foi atualizado ao patch compatível `57.0.18`. `expo install --check`
  confirmou dependências atuais, Expo Doctor aprovou `21/21`, TypeScript e 13
  testes móveis passaram e o export Android/Hermes concluiu 603 módulos. A
  auditoria encontrou zero vulnerabilidade alta/crítica e 11 moderadas
  transitivas; `audit fix --force` não foi usado porque faria downgrade
  incompatível de pacotes do toolchain, inclusive do Expo.
- O login local foi concluído como `raulsallesr`, sem registrar credencial. O
  projeto `@raulsallesr/focuslens-br` foi criado e vinculado ao `projectId`
  público. Os builds EAS `development`
  (`1ca28edc-ee9f-4b21-8ec6-6ba8baa9b918`) e `preview`
  (`dd050dbe-5d0d-44e8-aae8-e13f613b7405`) terminaram com o mesmo fingerprint
  do commit `60fa378`. Development e preview foram instalados no POCO X8 Pro;
  DB-01 a DB-05 e DB-07 a DB-09 estão aprovados; DB-06 é automatizado. O Metro LAN foi
  bloqueado pelo firewall corporativo, mas o preview reabriu e navegou em modo
  avião. O aparelho usa Android 16 (`BP2A.250605.031.A3`); DB-10 a DB-12
  continuam pendentes e foram pausados por decisão do Raul enquanto a utilidade
  cotidiana do produto é refinada.
- A Etapa 5B começou em 2026-08-28 com o corte móvel `v0.3.0`. O editor cria,
  edita e exclui posições; a primeira gravação substitui conscientemente a demo.
  `privatePortfolio.ts` define o contrato privado `v1`, `securePortfolioStorage.ts`
  guarda a chave no SecureStore e cifra o documento com AES-256-GCM em arquivo
  persistente com troca atômica. O web não persiste carteira; falha de chave,
  autenticação ou schema bloqueia o dado e oferece reset explícito.
- As dependências nativas `expo-crypto`, `expo-file-system` e
  `expo-secure-store` foram instaladas nas versões compatíveis com Expo 57. O
  plugin do SecureStore configura Android Auto Backup sem declarar uso de Face
  ID. TypeScript, 20 testes, export web e bundle Android/Hermes com 633 módulos
  passaram. O preview EAS `67b97c57-ce20-4cb6-8c21-570c4742762e`, commit
  `9308f02` e fingerprint `a28c993ae571b5d58d7eea95f8fe6fc877c71023`
  terminou `FINISHED`. O ciclo foi validado depois no preview `v0.4.0`: CL-02 a
  CL-10 foram aprovados; CL-11 a CL-13 continuam pendentes.
- Em 2026-08-28, o Raul interrompeu conscientemente o restante do checklist
  físico porque o app ainda não despertava vontade de uso. O corte `v0.4.1`
  inicia um refinamento de valor dentro da Etapa 5B: a Home passa a começar
  pelo recorte pessoal, deixa explícita a cobertura real dos sinais, a Carteira
  resume distribuição por classe e posições longas usam revelação progressiva.
  Nenhum motor, contrato público `v1`, persistência ou item da Etapa 5C mudou.
- O corte `v0.4.2` continua o mesmo refinamento: “Ocultar valores” agora é um
  estado único da sessão e permanece ao trocar entre Carteira, Hoje e Cenários.
  Cenários abre com uma hipótese explícita de +50 bps, resume a parcela que pede
  atenção, a que pode favorecer e a que não possui relação classificada, antes
  de abrir as posições. A agregação reutiliza somente os efeitos educacionais
  já existentes no TypeScript; nenhum efeito, probabilidade ou retorno foi criado.
- O corte `v0.4.3` corrige a hierarquia real da Home: o recorte pessoal agora
  aparece antes do contexto de mercado e resume maior classe, maior posição e
  cobertura sem expor montante. A ação principal leva à montagem da carteira na
  demonstração e à sensibilidade quando a carteira já é local. É uma mudança de
  apresentação e navegação sobre contratos existentes, sem persistência nova.
- O corte `v0.4.4` reduz o atrito para sair da demonstração: ao abrir Carteira,
  a importação B3 aparece como caminho principal antes do patrimônio fictício,
  enquanto a entrada manual permanece como alternativa. Carteiras locais
  preservam “Adicionar posição” como ação principal; parser, cofre e contrato
  privado continuam idênticos. O preview EAS `v0.4.4`, build `8`, terminou
  `FINISHED` em 2026-08-31 no commit `565b071`, sem variáveis `Plain text` ou
  `Sensitive`; não foi avaliado separadamente e foi sucedido pelo `v0.5.2/11`,
  cuja instalação foi confirmada pelo Raul.
- Em 2026-08-27, o Raul aprovou seguir o roadmap institucional **FocusLens
  Embedded**. `docs/ESTRATEGIA_INSTITUCIONAL.md` registra a tese, os módulos, o
  piloto e as métricas de compra; `docs/ARQUITETURA_INSTITUCIONAL.md` registra
  fronteiras, contratos, segurança, observabilidade e gates. Essa aprovação não
  altera o próximo incremento nem significa que API, SDK, Governance Studio ou
  integração bancária já existam.
- `resumo_integrado.py` escolhe entre Focus × Curva, Expectativas, Curva e
  Qualidade dos dados; a Home usa esse contrato na primeira dobra e segue
  Resumo → Expectativas → Curva → Carteira. `curva_cenarios.py` adiciona o
  choque paralelo puro e `METODOLOGIA_FOCUSLENS.md` conecta os contratos. O
  pacote da `v2.0` inclui captura, arquitetura, release notes, LinkedIn e
  auditoria de publicação.
- O repositório continua privado. A consulta anônima ao GitHub retornou 404;
  nenhuma mudança de visibilidade, tag ou release foi executada.
- Existe um stash anterior chamado
  `codex-pre-focuslens-cache-2026-08-26`. Ele deve ser preservado e não pode
  ser aplicado ou removido sem antes inspecionar seu conteúdo e confirmar a
  intenção com o Raul.
- Existe também `codex-web-cockpit-before-mobile-pivot-2026-08-27`, criado para
  preservar o protótipo Streamlit não publicado quando o Raul pediu a virada
  móvel.
- A verificação para este handoff encontrou uma alteração local isolada em
  `dados/focus_cache.json`: somente `atualizado_em` mudava de `2026-08-26` para
  `2026-08-27`. Como a origem não foi atribuída com segurança, ela foi guardada
  no stash `codex-focus-cache-before-mobile-handoff-2026-08-27`. Os três
  stashes devem ser preservados; não aplicar nem remover nenhum deles sem
  inspecionar seu conteúdo e confirmar a intenção com o Raul.

### Mapa de retomada

| Arquivo | Para que serve |
|---|---|
| `CLAUDE.md` | Regras permanentes, guardrails e gates obrigatórios. |
| `CONTEXT.md` | Estado vivo, decisões fechadas, bloqueios e próximo passo. |
| `PLANO_FOCUSLENS.md` | Escopo do produto e checklist do próximo incremento. |
| `mobile/README.md` | Comandos para executar e validar o app móvel. |
| `docs/ARQUITETURA_MOBILE.md` | Fronteira Python → contrato → React Native. |
| `docs/VALIDACAO_DEVELOPMENT_BUILD.md` | EAS, instalação, offline, acessibilidade e evidências físicas. |
| `docs/VALIDACAO_CARTEIRA_LOCAL.md` | Ciclo físico do editor e cofre local. |
| `docs/VALIDACAO_IMPORTACAO_B3.md` | Prévia, substituição, offline e privacidade do importador XLSX. |
| `docs/ESTRATEGIA_INSTITUCIONAL.md` | Tese, produto Embedded, piloto, métricas e pacote comercial. |
| `docs/ARQUITETURA_INSTITUCIONAL.md` | Arquitetura-alvo, contratos, segurança e gates institucionais. |
| `docs/AUDITORIA_PUBLICACAO_V2.0.md` | Evidência e pendências da publicação web `v2.0`. |

### Ordem de leitura e preparação

1. Trabalhe dentro deste repositório, nunca no git do hub que o contém.
2. Rode `git pull --ff-only`, `git status --short --branch` e `git stash list`.
   Não aplique os stashes apenas para “limpar” a lista.
3. Leia `CLAUDE.md`, este `CONTEXT.md` e `PLANO_FOCUSLENS.md`, nessa ordem.
4. Para continuar o app, leia `mobile/README.md` e
   `docs/ARQUITETURA_MOBILE.md`; siga a seção “Próxima execução — Etapa 5” do
   plano. Para fechar o build e a Etapa 5B, leia também
   `docs/VALIDACAO_DEVELOPMENT_BUILD.md`, `docs/VALIDACAO_CARTEIRA_LOCAL.md` e
   `docs/VALIDACAO_IMPORTACAO_B3.md`. Para publicar a `v2.0` web, leia
   também
   `docs/AUDITORIA_PUBLICACAO_V2.0.md` e `docs/RELEASE_V2.0.md`.
5. Para trabalhar na trilha B2B, leia `docs/ESTRATEGIA_INSTITUCIONAL.md` e
   `docs/ARQUITETURA_INSTITUCIONAL.md`; a seção 14 do plano define quando essa
   trilha pode começar.
6. A licença e o e-mail histórico só bloqueiam a abertura pública/tag/release;
   não bloqueiam o desenvolvimento privado do app móvel.

### Decisões que não devem ser reabertas

- A experiência principal agora é móvel. A página Streamlit permanece íntegra
  como bancada dos motores e não deve receber uma nova rodada de redesign antes
  do contrato vivo do app.
- Os motores existentes são a fonte dos cálculos. A integração não deve
  duplicar regras numéricas dentro da UI móvel.
- BACEN/Focus, SGS e Tesouro Transparente são as fontes públicas do produto;
  ANBIMA continua opcional e fora do caminho crítico do MVP.
- Notícias, Radar e dados da carteira não entram no cálculo de convergência
  Focus × Curva. A carteira permanece local à sessão.
- Taxa de título não é previsão pura da Selic. O app continua educacional,
  sem recomendação, promessa, causalidade inventada ou probabilidade falsa.
- O visual móvel preserva tema claro, verde-petróleo, dourado discreto, números
  e fontes perto da conclusão e detalhes progressivos. A marca em lente + curva
  é determinística e versionada em SVG/PNG.
- IPCA+, títulos com cupom, bootstrap, forwards e backtest continuam fora da
  `v2.0`, salvo nova decisão explícita do Raul.
- A direção B2B aprovada chama-se **FocusLens Embedded**. O produto vendável é
  a camada explicável e auditável — API, receipt, Exposure Adapter, SDK e
  Governance Studio — e não apenas as telas do app.
- O primeiro piloto institucional usará posições que o próprio banco já mantém.
  Open Finance fica para uma expansão posterior aos gates e não será usado como
  atalho para provar o caso de valor.
- Motores não conhecerão identidade, consentimento ou catálogo. Explicação
  educacional e recomendação comercial continuarão separadas.

### Estado atual e próxima decisão, sem ambiguidade

- Entrega atual: **Etapa 5C — laboratório do dinheiro `v0.6.0`**. Histórico
  público local, favoritos, alertas explicáveis, simulador por classe, revisão
  contextual e nove caminhos educacionais em Cenários estão implementados.
- O APK interno mais recente é o `v0.5.2`, build `11`: EAS
  [`c08e5397-427f-42c2-a163-ab5cd815cb55`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/c08e5397-427f-42c2-a163-ab5cd815cb55),
  [download direto](https://expo.dev/artifacts/eas/dvVgjSbINj4f3OdJ4CJXx_O651PcG-llvTyurlh0Ytc.apk),
  commit `1c477f5`, fingerprint `4a0bc79db5a2beeb9b694f3ee8718ff13be38dff` e
  expiração em 2026-09-14. O Raul confirmou a instalação por cima do app em
  2026-08-31; como o aparelho não estava conectado ao ADB, package/versão e as
  jornadas ainda não foram verificados. Instalação declarada não aprova gate físico.
- A `v0.5.3` conecta `o que mudou` → `o que prova` → `onde toca a carteira` →
  `o que explorar em Cenários` → `o que não prova`, somente com fotografia,
  favoritos, `effects`, impactos e posições já compostos em memória. A ida a
  Cenários não preenche hipótese e oferece retorno explícito à revisão.
- A `v0.5.4`–`v0.5.6` adiciona “Quanto vira?”, meta ao contrário, preço de
  esperar, inflação opcional, hábito recorrente e desafio de intuição. A taxa é
  sempre fornecida pela pessoa e mantida constante apenas para a conta; nenhum
  número vem da carteira, do snapshot ou de uma instituição.
- A `v0.5.7`–`v0.6.0` acrescenta quando o valor dobra, marcos da jornada, régua
  temporal, equivalente mensal correto, aporte extra único ou anual, caminho da
  reserva e comparação sem aporte/com aporte, inflação e custo hipotético. O
  custo é uma hipótese de taxa, não produto ou tributo; a reserva não recebe
  rendimento inventado.
- TypeScript, 61 testes de domínio, 22 de componentes, 4 contratos E2E e o
  export Android/Hermes com 654 módulos passaram. As quatro trilhas novas foram
  percorridas em 375×812, 430×932, 768×1024 e 844×390 sem overflow horizontal
  ou alvo visível abaixo de 44 px. Essa evidência é local, não física.
- Não existe incremento de utilidade posterior à `v0.6.0` escolhido neste
  handoff. A decisão vigente continua sendo melhorar a experiência antes de
  priorizar os checklists físicos, sem ampliar escopo por inferência.
- Evidência já fechada permanece válida: Android 16
  (`BP2A.250605.031.A3`), BI-01 a BI-03 e CL-02 a CL-10 aprovados. BI-04 a
  BI-13, CL-11 a CL-13 e DB-10 a DB-12 continuam pendentes, mas pausados até o
  Raul considerar a experiência útil o suficiente para retomar os gates.
- Não alterar os motores, o schema público `1` ou os três stashes. Autenticação,
  nuvem, Open Finance e Embedded continuam posteriores.
- Os dois YAMLs Maestro atuais usam `clearState: true`; não executá-los contra
  uma carteira local que precise ser preservada. Antes da futura execução física,
  usar um estado de demonstração descartável ou preparar fluxos não destrutivos.
- Não antecipar a Etapa 6/Embedded durante o development build. O roadmap
  institucional aprovado começa somente depois dos gates definidos na seção 14.
- A definição e a evidência completa até a `v0.6.0` estão nas seções 24 a 31
  de `PLANO_FOCUSLENS.md`.

### Prompt pronto para abrir o próximo chat

> Abra o projeto `01_Projetos/Financas-Pessoais`, rode `git pull --ff-only` e
> leia integralmente `CLAUDE.md`, `CONTEXT.md`, `PLANO_FOCUSLENS.md`,
> `mobile/README.md` e `docs/ARQUITETURA_MOBILE.md`. Confira `git stash list`,
> mas não aplique nem remova os três stashes documentados. A `v2.0` dos motores,
> a fundação móvel `v0.1`, o contrato público `v1` e o editor/cofre privado com
> importação B3 local `v0.4.0` já estão implementados; não refaça
> `v1.12`–`v2.0`, não redesenhe o Streamlit, não replique fórmulas dos motores em TypeScript
> e não coloque carteira no snapshot. A configuração
> EAS/dev client já está pronta e validada; não a refaça. O projeto
> `@raulsallesr/focuslens-br` está vinculado. Os APKs Android `development` e
> `preview` anteriores já foram instalados no POCO X8 Pro com Android
> 16 (`BP2A.250605.031.A3`). DB-01 a DB-09, BI-01 a BI-03 e CL-02 a CL-10 estão
> aprovados, com DB-06 automatizado. O preview `v0.5.2`, build `11`, EAS
> `c08e5397-427f-42c2-a163-ab5cd815cb55`, está `FINISHED` e o Raul confirmou sua
> instalação, mas o aparelho não estava conectado ao ADB e o corte ainda não foi
> avaliado fisicamente. O Raul autorizou iniciar a Etapa 5C em
> 2026-08-31; a `v0.6.0` local já implementa histórico de fotografias públicas,
> favoritos, alertas explicáveis, simulador por classe, revisão guiada e o
> laboratório do dinheiro. Cenários oferece “Quanto vira?”, meta ao contrário,
> preço de esperar, inflação opcional, hábito recorrente, desafio de intuição,
> dobra do valor, marcos temporais, equivalente mensal, aportes extras, caminho
> da reserva e comparação completa de aportes, inflação e custo hipotético.
> A taxa e os valores são sempre escolhidos pela pessoa; todo o laboratório vive
> somente na sessão, não toca carteira/snapshot/storage/rede e respeita o modo
> discreto. Hoje e Entenda continuam conectando mudança, prova, relação com a
> carteira, Cenários e limite. A ida a Cenários não preenche hipótese e possui
> retorno explícito.
> Os dois fluxos Maestro e seus seletores canônicos estão preparados, mas ainda
> não foram executados em binários Android/iOS. No Windows, Temurin `17.0.20.1`,
> Maestro `2.9.0` e ADB `37.0.1` estão instalados de forma portátil; os YAMLs
> passaram em `npm run e2e:maestro:check:windows`, e o runner confirmou o bloqueio
> por ausência de Android conectado. Não rode esses fluxos automaticamente: os
> YAMLs atuais usam `clearState: true` e podem apagar a carteira local. O Raul
> prefere continuar nas melhorias antes dos testes. As seções 24 a 31 do plano
> estão concluídas localmente e os gates passaram; o próximo incremento de
> utilidade ainda deve ser escolhido, sem antecipar escopo. Preserve a Home orientada ao
> recorte pessoal, a cobertura honesta, a
> distinção entre carteira local e demonstração, a entrada B3 antes do exemplo
> fictício e o modo discreto. BI-04 a BI-13, CL-11 a CL-13 e DB-10 a DB-12
> continuam pausados e pendentes; não os marque como aprovados. Não envie
> planilha ou valores pelo chat e não antecipe autenticação de cliente, Open
> Finance ou Embedded.
> O roadmap FocusLens Embedded já está aprovado e documentado, mas não antecipe
> API, SDK, autenticação ou integração bancária. Rode TypeScript, testes móveis
> e export Android em qualquer novo incremento; faça commit/push apenas no git próprio.

## Direção aprovada — FocusLens BR

- O projeto evoluirá no mesmo repositório, em quatro entregas independentes e
  publicáveis: Focus Semanal (`v1.12`), Curva Tesouro (`v1.13`), Focus × Curva
  (`v1.14`) e integração FocusLens BR (`v2.0`). Não serão criados repositórios
  descartáveis para cada etapa.
- `PLANO_FOCUSLENS.md` é o contrato canônico de produto: tese, escopo, limites,
  arquitetura prevista, padrão visual, gates e estratégia de publicação.
- A identidade atual permanece: tema claro, verde-petróleo, dourado discreto,
  hierarquia editorial, conteúdo denso e detalhes progressivos. A evolução não
  adicionará dependência visual nem trocará o design a cada marco.
- Fontes padrão: BACEN/Focus e SGS, mais Tesouro Transparente na etapa da
  curva. ANBIMA será opcional e nunca dependência do MVP.
- A curva começará por títulos prefixados sem cupom e pontos observados. Taxa
  de título não será apresentada como previsão pura da Selic; prêmio de prazo,
  risco e liquidez permanecem limitações explícitas.
- As Etapas 0, 1, 2 e 3 foram concluídas em 2026-08-26. A Etapa 4 foi
  concluída tecnicamente em 2026-08-27; falta somente a decisão de governança
  para tag, release e abertura pública da `v2.0`.
- A Etapa 5 começou em 2026-08-27 por decisão explícita do Raul. O app móvel é
  o destino do produto; a fundação `v0.1` e o contrato vivo `v1` foram
  concluídos. A configuração nativa do development build foi concluída em
  2026-08-28; os primeiros APKs `development` e `preview` foram instalados e o
  fluxo principal/offline foi aprovado. No `v0.4.0`, CL-02 a CL-10 e BI-01 a
  BI-03 também foram aprovados. Acessibilidade e o restante da importação estão
  pausados e pendentes; o Raul autorizou desenvolver a Etapa 5C em paralelo para
  aumentar a utilidade, sem inferir aprovação desses gates.
- A direção institucional foi aprovada em 2026-08-27: o app pessoal será o
  cliente de referência e a futura camada **FocusLens Embedded** oferecerá API,
  receipt auditável, Exposure Adapter privado, SDK, Governance Studio e piloto
  controlado. A sequência canônica está na seção 14 de `PLANO_FOCUSLENS.md`.

## Arquitetura

- Projeto pessoal, **sem relação com FitBank/Fits** — repositório próprio
  (git e remote independentes, `origin` continua
  `https://github.com/raulsallesr/financas-pessoais.git`). Desde 2026-08-04
  a pasta mora fisicamente dentro do hub da Fits
  (`01_Projetos/Financas-Pessoais/`, movida de `Documents/financas-pessoais`)
  para dar acesso de arquivo ao Codex; o `.gitignore` do hub ignora esta
  pasta inteira.
- **Fluxo de código (atualizado 2026-08-04): Claude e Codex escrevem direto,
  com a mesma autorização** — sem brief, sem tier de risco, sem revisão do
  Claude como porta de entrada; uma conversa direta com o Raul já autoriza.
  Exceção permanente registrada em `AGENTS.md` do hub (seção "Exceção
  permanente — `01_Projetos/Financas-Pessoais/`") e em `CLAUDE.md` deste
  projeto. As restrições são usar só o git deste projeto (nunca o do hub) e
  rodar os testes antes de considerar pronto. Commit e `git push` estão
  permanentemente autorizados após o gate passar, sem nova confirmação a
  cada tarefa (decisão explícita do Raul, 2026-08-04).
- `mobile/` é a interface principal em React Native/Expo/TypeScript. `App.tsx`
  mantém a navegação Hoje, Carteira, Cenários e Entenda; `src/domain/` separa o
  contrato e os filtros da camada visual; `src/data/demoSnapshot.ts` é
  explicitamente sintético; `docs/ARQUITETURA_MOBILE.md` registra a fronteira
  para o provider vivo.
- A referência Streamlit continua em página única: `app_financas.py` chama `pagina_home.py`, que
  compõe Resumo, Expectativas, Curva e Carteira na mesma rolagem. O menu
  lateral usa essas quatro âncoras; os antigos entrypoints em `pages/` foram
  removidos para não manter navegação paralela.
- Separação motor puro / adaptador / UI:
  - `financas_taxonomia.py` — enums compartilhados (ClasseAtivo, Direcao,
    unidades de exibição).
  - `motor_indicadores.py` — motor genérico indicador+direção → efeito por
    classe de ativo (reaproveitável por features futuras).
  - `focus_data.py` — dataclasses e cálculo de delta/tendência (sem I/O).
  - `focus_atualizacao.py` — regras puras de verificação automática e
    diagnóstico da idade dos dados em dias úteis.
  - `focus_leitura.py` — adaptador da API Olinda + cache local em
    `dados/focus_cache.json`.
  - `focus_regras.py` — narrativa em linguagem simples + analogias.
  - `focus_apresentacao.py` — priorização, destaques e formatação da camada
    visual (sem Streamlit).
  - `focus_semanal.py` — motor puro de relevância normalizada, ranking e
    estados da fotografia semanal.
  - `pagina_focus.py` — composição da seção e dos estados do Focus.
  - `curva_data.py` — contrato e consolidação dos pontos observados.
  - `curva_fontes.py` — download limitado, parser do CSV, validação e cache
    atômico das 45 datas mais recentes.
  - `curva_modelo.py` — fotografias D-5/D-21, deltas em bps, inclinação,
    estados e narrativa determinística.
  - `curva_cenarios.py` — choque paralelo puro sobre a fotografia atual, com
    taxas simuladas, inclinação preservada, narrativa e limites explícitos.
  - `curva_apresentacao.py` — formatação pt-BR, séries e especificação do
    gráfico e linhas da tabela, sem dependência do Streamlit.
  - `pagina_curva.py` — resumo, métricas, curva com estilos de linha e tabela
    acessível.
  - `convergencia_modelo.py` — matriz direcional Focus × Curva, recortes de
    ponta, cinco estados, evidências e condições de mudança, sem I/O.
  - `convergencia_apresentacao.py` — formatação pt-BR das quatro métricas da
    convergência, sem Streamlit.
  - `pagina_convergencia.py` — apresentação anterior preservada e coberta por
    testes durante a migração; não é mais seção paralela da Home.
  - `resumo_integrado.py` — orquestração pura dos três contratos públicos;
    escolhe a leitura prioritária, limita a síntese a duas–quatro provas e
    mantém datas, limites e condições sem refazer cálculos; também filtra um
    único contexto externo do Radar sem repetir o Focus.
  - `pagina_resumo.py` — adaptador independente dos dois caches e composição
    visual do Resumo, com falha isolada por fonte.
  - `pagina_home.py` — composição da experiência única;
    `app_financas.py` é apenas o entrypoint principal.
  - `ui_estilos.py` — tokens e CSS responsivo/acessível compartilhável.
  - `noticias_data.py` — normalização, relevância, deduplicação e seleção
    diversificada das manchetes (sem I/O).
  - `noticias_feed.py` — adaptador RSS isolado para InfoMoney e Brazil
    Journal, Money Times, Agência Brasil, InvestNews e NeoFeed, com timeout,
    limite de resposta, allowlist e fallback por fonte.
  - `noticias_focus.py` — motor puro e conservador que identifica temas no
    próprio título e cruza a direção editorial com a última mudança do Focus.
  - `noticias_artigo.py` — extrator sob demanda e efêmero do conteúdo de uma
    matéria, com robots.txt, allowlist HTTPS, redirecionamentos validados,
    limites de tamanho e descarte de navegação/publicidade.
  - `noticias_analise.py` — motor puro que identifica temas, direção, números
    e instituições no texto, compara os sinais com o Focus e devolve apenas
    análise estruturada; o corpo editorial não integra o resultado.
  - `mercado_data.py` — dataclasses, consolidação, variação de 30 dias e
    normalização base 100 (sem I/O).
  - `mercado_fontes.py` — adaptadores independentes para PTAX/BACEN,
    Brent/EIA via FRED, BTC/BRL/Binance e CDI/Selic diários via SGS.
  - `macro_modelo.py` — sinais, eixos, cenário condicionado, perspectivas,
    confiança e temas editoriais (motor puro e explicável).
  - `pagina_macro.py` — carga reutilizável do cenário e apresentação completa
    anterior do Radar; a Home usa a carga na Carteira e só o contexto externo
    selecionado no Resumo.
  - `carteira_modelo.py` — normalização, alocação, resultado, benchmark e
    cruzamento puro entre classes da carteira e perspectivas do Radar.
  - `b3_importacao.py` — adaptador `openpyxl` em memória para o XLSX da Área
    do Investidor B3; mantém apenas ativo, classe e valor, ignora
    identificadores/subtotais e consolida ativos repetidos entre abas.
  - `pagina_carteira.py` — editor de posições em memória e apresentação; os
    valores pessoais e a planilha importada não são persistidos nem
    versionados.
  - `METODOLOGIA_RADAR.md` — contrato, fontes, limites e próximos gates do
    motor macro.
  - `METODOLOGIA_FOCUS.md` — cálculo, limiares, estados e limites do Focus
    Semanal.
  - `METODOLOGIA_CURVA.md` — fonte, licença, fórmulas, estados e limites da
    Curva Tesouro.
  - `METODOLOGIA_FOCUS_CURVA.md` — contrato de comparabilidade, matriz dos
    estados, pontas, evidências e limites da convergência.
  - `METODOLOGIA_FOCUSLENS.md` — ponto de entrada integrado para prioridade,
    evidências, datas, fontes, cenário e limites entre as quatro camadas.
  - `docs/RELEASE_V2.0.md` — notas do release candidate e artefatos finais.
  - `docs/AUDITORIA_PUBLICACAO_V2.0.md` — gate técnico de privacidade,
    segredos, licenças, dependências e histórico Git.
  - `docs/POST_LINKEDIN_FOCUSLENS_V2.0.md` — texto e checklist de publicação.
  - `atualizar_focus_cache.py` — entrada sem Streamlit usada pela automação
    agendada em `.github/workflows/atualizar-focus.yml`.
  - `atualizar_curva_cache.py` — entrada sem Streamlit usada pela automação
    diária em `.github/workflows/atualizar-curva.yml`.
- Guardrail de conteúdo: o motor de regras nunca recebe dados do usuário e
  nunca usa linguagem imperativa ("invista", "compre") — só descritiva/
  histórica. `tests/test_focus_regras.py` faz lint de vocabulário proibido.
- **Multi-máquina (trabalho + casa)**: mesma conta Claude, mas sem memória de
  conversa compartilhada entre sessões/máquinas — o git é a única fonte de
  verdade. Por isso: `CLAUDE.md` (instruções fixas, lido automaticamente por
  qualquer sessão Claude Code) + este `CONTEXT.md` (estado vivo) substituem a
  memória de chat. `dados/focus_cache.json` e
  `dados/curva_prefixada_cache.json` são versionados — contêm apenas dados
  públicos e mantêm a mesma fotografia nas duas máquinas.

## Estado atual

- v1 (2026-08-03): Selic (próxima reunião do Copom), IPCA e câmbio (ano
  corrente), comparação semana-a-semana, narrativa e efeitos por classe de
  ativo. Endpoints confirmados ao vivo via curl: `ExpectativasMercadoSelic`
  (campo `Reuniao`, ex. `"R5/2026"`) e `ExpectativasMercadoAnuais` (campo
  `DataReferencia`, ex. `"2026"`); `baseCalculo=0` = todos os respondentes.
  **Bug encontrado e corrigido**: a API do BACEN (Olinda) não decodifica
  corretamente o `+` que a lib `requests` usa por padrão para espaços em
  query params — devolve 400 ("types not compatible") mesmo em filtros OData
  válidos. `focus_leitura._get()` monta a query string manualmente com
  `urllib.parse.quote` (força `%20`).
- **v1.1 (2026-08-04)** — higiene + série histórica + mais indicadores:
  - `.venv` dedicado criado (o projeto rodava contra o Python global da
    máquina, com dezenas de libs não relacionadas — risco de dependência
    cruzada). Ver "Como rodar" no README.
  - Primeiro commit git feito (baseline v1), segundo commit com esta v1.1.
  - `focus_data.serie_historica()` + seção "Como evoluiu nas últimas
    semanas" em `pages/1_Boletim_Focus.py` (um `st.line_chart` por
    indicador, com aviso específico de que a "próxima reunião do Copom" da
    Selic muda com o tempo e pode gerar um salto que não é mudança real de
    expectativa).
  - 3 indicadores novos: `PIB Total`, `IGP-M`, `Dívida líquida do setor
    público` (confirmados ao vivo via curl no endpoint
    `ExpectativasMercadoAnuais`). `IGP-M` deliberadamente **sem** regra de
    efeito por classe de ativo em `motor_indicadores.py` — não tem uma
    relação direta e didaticamente honesta com nenhuma das 5 classes atuais
    (ele indexa aluguel, não título público); a UI já trata lista de
    efeitos vazia sem quebrar.
  - Auditoria em 2026-08-04 confirmou que as "modificações do Codex" que o
    Raul mencionou não estão neste repositório (byte-a-byte idêntico ao v1)
    — decisão dele foi seguir com as melhorias sem investigar isso.
  - 37 testes pytest passando (30 do v1 + 7 novos); testado ao vivo (Selic
    14,00%, IPCA 5,03%, Câmbio R$5,20, PIB Total 1,99%, IGP-M 4,54%, Dívida
    líquida 69,90% do PIB em 2026-08-04) e o gráfico de série histórica
    confirmado com um snapshot sintético de 2 semanas (removido depois —
    cache real fica só com dados reais).
- **v1.3 (2026-08-04)** — experiência em camadas + contexto externo:
  - A página abre com uma síntese visual e somente os três indicadores
    prioritários (Selic, IPCA e câmbio). Impactos por classe, um único
    histórico selecionável, manchetes e detalhes formam as camadas seguintes;
    tabela, indicadores secundários e explicações completas ficam recolhidos.
  - Estados de impacto usam texto e cor, nunca cor isolada; estilos têm
    contraste validado, foco visível, alvos de 44 px, suporte a tema
    claro/escuro, redução de movimento e layout responsivo.
  - Motor semântico corrigido: estabilidade usa limiar específico por
    indicador; exposição cambial diante da Selic e títulos IPCA+ deixaram de
    simplificar relações ambíguas; narrativa informa o intervalo exato entre
    as leituras, sem assumir que houve atualização semanal.
  - Feed RSS de InfoMoney + Brazil Journal exibe três manchetes relevantes
    sem republicar conteúdo, com cache de 15 minutos, deduplicação, diversidade
    de fontes, validação de URL e degradação independente. Integração ao vivo
    confirmou 20 itens e nenhuma fonte indisponível em 2026-08-04.
  - Streamlit fixado em `>=1.49,<1.57` para manter compatibilidade com o
    caminho longo do projeto no OneDrive/Windows. Ambiente validado fora do
    OneDrive em `%USERPROFILE%\.venvs\financas-pessoais`.
  - Gate final: 50 testes pytest passando, incluindo `AppTest` da hierarquia,
    gráfico único, manchetes e estados de fallback; `py_compile` limpo.
- **v1.4 (2026-08-04)** — rotina autônoma e entrada mais clara:
  - Ao abrir o panorama, o app verifica o BACEN no máximo uma vez por dia
    útil; primeira execução e cache incompleto disparam backfill de até 12
    semanas. Falha de rede preserva a última fotografia e mostra o estado
    sem interromper a leitura.
  - Cache JSON passou a validar estrutura e formato da API e a ser escrito
    atomicamente (`fsync` + replace no mesmo diretório), reduzindo o risco de
    truncamento por interrupção/OneDrive.
  - Histórico real preenchido com 72 registros: 12 coletas semanais para
    cada um dos 6 indicadores, de 15/05/2026 a 31/07/2026.
  - GitHub Actions consulta o BACEN toda segunda-feira às 12h30 de Brasília e
    versiona apenas `dados/focus_cache.json` quando houver mudança; também
    aceita execução manual.
  - Home redesenhada como porta de entrada: estado da coleta, CTA direto,
    explicação da rotina em três passos e próximos módulos sob demanda.
  - Gate ampliado para 62 testes, cobrindo atualização automática, idade em
    dias úteis, backfill, deduplicação, cache inválido/atômico, CLI e home.
- **v1.5 (2026-08-04)** — Radar Macro explicável:
  - Nova página cruza expectativas do Focus com preço e momentum de dólar
    PTAX, Brent e Bitcoin em cinco eixos: inflação/custos, condições
    monetárias, atividade, fiscal e apetite a risco.
  - Saída é cenário direcional condicionado de 4–12 semanas, com confiança
    máxima moderada, evidências, classes com vento favorável/pressão,
    ressalvas e três condições explícitas de invalidação. Não há alvo de
    preço nem recomendação personalizada.
  - Manchetes entram somente como frequência de temas nos metadados RSS; o
    app explicita que não raspou nem leu o corpo integral das matérias.
  - Gráfico principal normaliza as três séries em base 100; preço real,
    data, fonte e tabela ficam disponíveis. Séries defasadas deixam de
    sustentar a confiança.
  - Integração ao vivo em 2026-08-04: PTAX R$ 5,1053 (04/08, -1,28% em 30
    dias), Brent US$ 91,82 (27/07, +30,87%) e BTC/BRL R$ 331.016 (04/08,
    -1,35%); nenhuma das cinco fontes ficou indisponível. Cenário produzido:
    “Juros altos, mas inflação sem aceleração clara”, confiança moderada.
  - Gate ampliado para 76 testes, incluindo os três adaptadores, fallback
    independente, normalização, motor/guardrail e `AppTest` da nova página.
- **v1.6 (2026-08-04)** — página única + referências + carteira:
  - Home, Focus, Radar e carteira passaram a formar uma única página com
    quatro âncoras no menu lateral, foco visível, alvos de 44 px e estado
    ativo por seção. Os dois entrypoints multipágina foram removidos.
  - PTAX, Brent e Bitcoin agora são coletados desde 1º de janeiro. CDI (SGS
    12) e Selic realizada (SGS 11) são compostos a partir das taxas diárias e
    entram no mesmo gráfico em base 100; não entram como sinal duplicado no
    motor macro.
  - Carteira MVP permite informar nome, classe, valor atual, valor investido
    e benchmark. Mostra total, concentração, alocação, resultado, comparação
    no ano e parcela exposta a cada perspectiva macro. Dados ficam apenas na
    sessão do navegador.
  - Validação ao vivo em 04/08/2026: 147 pontos PTAX (02/01–04/08), 143
    Brent (02/01–27/07), 216 BTC/BRL (01/01–04/08), 146 CDI e 146 Selic
    (02/01–03/08); nenhuma fonte indisponível.
  - Gate ampliado para 84 testes, incluindo composição de taxas, cinco
    adaptadores, carteira pura, privacidade/empty state e as três seções de
    UI com `AppTest`; `py_compile` limpo.
- **v1.7 (2026-08-04)** — importação da posição B3:
  - A carteira recebe o XLSX da Área do Investidor diretamente no navegador,
    processa em memória e preenche o editor sem copiar a planilha para o
    projeto. Conta, instituição, CNPJ, ISIN, contratos e demais colunas sem
    uso não são mantidos pelo adaptador.
  - As seis abas conhecidas são aceitas; subtotais e linhas sem valor são
    descartados, o mesmo ativo em custódia e empréstimo é consolidado e
    renda fixa usa MTM, curva ou fechamento nessa ordem. A dimensão A1
    incorreta do exportador B3 é corrigida antes da leitura.
  - Classes passam a incluir FIIs/FIAGRO, com perspectiva macro agregada e
    ressalva explícita sobre diferenças entre imóveis, recebíveis e agro.
  - Validado de ponta a ponta contra uma exportação real fornecida pelo Raul,
    sem versionar arquivo, identificadores, ativos ou valores pessoais.
  - Gate ampliado para 91 testes, incluindo XLSX sintético criado em runtime,
    dimensão A1 incorreta, arquivo inválido, consolidação, privacidade e
    upload via `AppTest`; `py_compile` limpo.
- **v1.8 (2026-08-06)** — tema claro + identidade visual:
  - Tema Streamlit fixado explicitamente em modo claro, sem alternância pelo
    tema do sistema. A nova paleta combina fundo verde-neutro muito claro,
    superfícies brancas, verde-petróleo de alto contraste e dourado discreto.
  - Home ganhou hero editorial, hierarquia tipográfica mais clara, cartões
    consistentes e etapas numeradas. O menu lateral passou a usar SVGs
    vetoriais próprios; os nomes de Material Symbols que apareciam como
    texto em alguns navegadores foram eliminados.
  - Sidebar inicia em modo automático: aberta em desktop e recolhida em
    telas pequenas. Abaixo de 768 px, colunas são empilhadas e os blocos
    ficam limitados ao viewport; a medição do DOM no Chrome confirmou largura
    rolável igual à largura visível no menor viewport aceito pelo headless.
  - Acessibilidade preservada/reforçada: skip link, foco visível, alvos de
    44 px, contraste WCAG AA testado, navegação com rótulo textual, ícones
    decorativos ocultos de leitores de tela e `prefers-reduced-motion`.
  - A cor principal dos gráficos foi centralizada em `ui_estilos.py`.
    Cálculos, fontes, textos metodológicos e dados não foram alterados.
  - Validação visual desktop em navegador real; gate ampliado para 93 testes,
    zero falhas/erros, mais `py_compile` limpo.
- **v1.9 (2026-08-07)** — interface enxuta e conteúdo priorizado:
  - A home deixou de funcionar como landing page: hero, cartão explicativo e
    três etapas redundantes foram substituídos por um cabeçalho compacto com
    status da coleta e acesso direto às seções.
  - O Focus prioriza síntese, Selic/IPCA/câmbio e histórico. Manchetes
    duplicadas foram removidas dessa seção; impactos, indicadores secundários
    e metodologia continuam disponíveis por abertura progressiva.
  - O Radar mostra primeiro cenário, preços e desempenho no ano; sinais,
    classes de ativo, temas editoriais e invalidadores foram agrupados em
    detalhes recolhidos. A carteira recolhe a importação B3 e a exposição
    macro, elimina métricas e tabelas duplicadas e mantém os valores exatos
    acessíveis sob demanda.
  - A densidade visual aumentou com conteúdo limitado a 1100 px, cartões e
    métricas menores, sombras mais discretas e ritmo vertical compacto. Foco
    visível, alvos de 44 px, contraste, redução de movimento, rótulos textuais
    e alternativas tabulares dos gráficos foram preservados.
  - Cálculos, fontes, persistência e dados não foram alterados. Gate: 93
    testes aprovados, `py_compile` e `git diff --check` limpos.
- **v1.10 (2026-08-07)** — noticiário multifuente cruzado com o Focus:
  - O gráfico histórico do Focus foi removido: a série quase reta da Selic
    não entregava sinal acionável e repetia informação já resumida nas
    métricas.
  - A seção substituta consulta em paralelo seis feeds validados — InfoMoney,
    Brazil Journal, Money Times, Agência Brasil, InvestNews e NeoFeed — e
    mostra os três temas mais conectados a juros, inflação, câmbio, atividade
    ou fiscal. O teste ao vivo leu 60 manchetes, dez por fonte, sem fonte
    indisponível.
  - Cada tema informa quantidade de manchetes e fontes e classifica a relação
    com a última mudança do Focus como `Em linha`, `Em tensão`, `Monitorar` ou
    `Sem direção clara`. As manchetes usadas ficam acessíveis no próprio card.
  - Para evitar relações artificiais, apenas palavras presentes no título
    podem sustentar o cruzamento; categorias amplas dos feeds não viram
    evidência. O app explicita que não lê o corpo das matérias e que frequência
    não equivale a verdade.
  - A navegação caiu de quatro para três destinos reais: Focus, Radar e
    Carteira. A capa continua como cabeçalho, mas deixou de parecer uma aba.
  - Gate ampliado para 98 testes, com regressão contra temas inventados por
    categoria; `py_compile`, integração real das seis fontes e
    `git diff --check` aprovados.
- **v1.11 (2026-08-07)** — leitura aprofundada das matérias:
  - Cada manchete destacada pode ser analisada sob demanda na própria seção
    Focus. O app abre a fonte somente depois do clique e mostra síntese
    conservadora, relações por tema com a última mudança do Focus, números,
    instituições e cinco pontos objetivos para acompanhar.
  - A análise diferencia `Em linha`, `Em tensão`, `Monitorar` e `Sem direção
    clara`; ausência de sinal suficiente aparece como limite, sem completar
    lacunas nem atribuir intenção ao autor.
  - A leitura respeita robots.txt, aceita somente HTTPS e hosts das seis
    fontes, valida redirecionamentos, limita o HTML a 2 MB e o texto a 6 mil
    palavras. O corpo integral existe apenas durante o processamento em
    memória: cache e sessão recebem somente a análise estruturada. Na tela,
    a rastreabilidade usa título/link da fonte e um trecho de até 18 palavras.
  - Validação real em 07/08/2026 analisou, sem persistir o texto, matérias de
    InvestNews (878 palavras), Money Times (604) e Agência Brasil (275);
    falhas de extração/robots degradam para aviso e link original.
  - Gate ampliado para 105 testes, incluindo segurança do extrator, bloqueio
    por robots.txt, redirecionamento externo, classificação, evidências e
    carregamento somente após clique; `py_compile` e integração real limpos.
- **v1.12 (2026-08-26)** — Focus Semanal:
  - O topo da seção Focus responde “o que mudou” antes dos detalhes e mostra
    até três revisões entre Selic, IPCA, câmbio e PIB Total.
  - A relevância é comparável entre unidades: delta absoluto dividido pelo
    limiar específico de estabilidade. Empates seguem ordem fixa e o método
    está documentado em `METODOLOGIA_FOCUS.md`.
  - A tela distingue `Atualizado`, `Defasado`, `Indisponível` e `Sem mudança
    relevante`, sempre com datas e evidência perto da conclusão.
  - Motor, apresentação e UI permanecem separados; a identidade clara em
    verde-petróleo foi preservada e a captura principal está versionada.
  - Gate: 115 testes aprovados; `py_compile` dos três módulos alterados e
    `git diff --check` limpos. Desktop foi inspecionado em navegador real;
    responsividade, foco, contraste e redução de movimento permanecem cobertos
    pelo CSS compartilhado e pelos testes de UI.
- **v1.13 (2026-08-26)** — Curva Tesouro:
  - Fonte oficial validada ao vivo: 175.462 registros, oito famílias e
    histórico efetivo desde 31/12/2004. O MVP usa somente `Tesouro Prefixado`
    sem cupom e `Taxa Compra Manha`, conforme metadados oficiais.
  - O cache inicial contém 225 pontos em 45 datas. A curva de 26/08/2026 tem
    cinco vencimentos; D-5 é 19/08 e D-21 é 28/07, sempre por observações
    efetivamente publicadas.
  - Na fotografia de lançamento, a variação mediana D-5 foi -24 bps e a
    inclinação entre as pontas observadas foi +93 bps. Isso é evidência da
    demo, não recomendação nem previsão de Selic.
  - Gráfico diferencia atual, D-5 e D-21 por cor, traço e marcador; a tabela
    preserva valores exatos e lacunas. Fonte indisponível degrada para cache
    ou estado explícito sem afetar as outras seções.
  - Automação em dias úteis, metodologia ODbL, captura e diagrama técnico
    acompanham a entrega.
  - Gate final: 132 testes aprovados; `py_compile` dos seis módulos da entrega
    e `git diff --check` limpos. A interface foi inspecionada em navegador real
    a 1440 px e 390 px, sem rolagem horizontal no viewport móvel.
- **v1.13.1 (2026-08-26)** — revisão de qualidade pré-integração:
  - A preparação de formatação, gráfico e tabela saiu de `pagina_curva.py`
    para `curva_apresentacao.py`, uma camada pura e testável. A página caiu de
    372 para 262 linhas sem mudar o resultado visual.
  - `PontoCurva` passou a rejeitar vencimento inválido, campo obrigatório vazio
    e número não finito. Duplicatas idênticas são consolidadas; duplicatas
    conflitantes interrompem fonte ou cache com erro controlado.
  - Gate: 141 testes aprovados, todos os módulos compilados, `pip check` e
    `git diff --check` limpos. O cache real carregou 225 pontos no estado
    `Atualizada`; interface e diagrama foram inspecionados em navegador real a
    1440 px, 375 px e 844 px em paisagem, com `scrollWidth == clientWidth`.
    O intervalo de 769–960 px agora organiza as quatro métricas em grade 2×2,
    evitando truncamento dos valores.
- **v1.14 (2026-08-26)** — Focus × Curva:
  - O motor compara a revisão da Selic para a mesma reunião com a mediana
    D-5 de ao menos dois vencimentos prefixados em comum. As direções formam os
    estados `Alinhados`, `Curva mais pressionada`, `Curva mais benigna`,
    `Sinais mistos` e `Dados insuficientes`.
  - Com quatro ou mais pontos, os vencimentos mais próximos e mais distantes
    viram ponta curta e longa. Direções opostas permanecem mistas; notícias,
    Radar e carteira não entram no cálculo.
  - Na fotografia de lançamento, a Selic `R6/2026` ficou em 13,75% entre
    14/08 e 21/08, enquanto a curva caiu mediana de 24 bps entre 19/08 e
    26/08. O estado é `Curva mais benigna`, com curta em -6,5 bps e longa em
    -29 bps; esses valores são evidência da demo, não recomendação.
  - O veredito, quatro métricas, “O que prova” e “O que faria mudar” foram
    validados em 390, 844 e 1440 px, sem rolagem horizontal. Captura,
    metodologia, diagrama técnico e texto de LinkedIn acompanham a entrega.
  - Gate final: 160 testes aprovados fora do sandbox do Windows; `py_compile`,
    `pip check` e `git diff --check` limpos. O primeiro run dentro do sandbox
    encontrou apenas `WinError 5` nos diretórios temporários usados pelos
    testes de cache atômico, sem regressão funcional.
- **Etapa 4 · incremento 1 (2026-08-27)** — contrato do Resumo integrado:
  - `resumo_integrado.py` consome `ResumoFocusSemanal`, `LeituraCurva` e
    `LeituraConvergencia` sem I/O, Streamlit ou nova fórmula. A prioridade é
    determinística: convergência íntegra; revisão relevante do Focus; curva
    atual; Focus atual; qualidade dos dados.
  - A saída preserva veredito, duas a quatro provas sem cards de preenchimento,
    datas separadas por fonte, limites e condições de mudança. Falha de uma
    fonte mantém a leitura independente da outra; duas falhas não viram
    síntese inventada.
  - Sete testes novos cobrem regras de prioridade, degradação independente,
    rastreabilidade das datas e composição sintética pelos três motores reais.
    A interface permaneceu inalterada neste incremento; a integração visual é
    o próximo item do plano.
  - Gate final: 168 testes aprovados fora do sandbox; todos os módulos
    compilados; `pip check` sem dependências quebradas; `git diff --check`
    limpo. O primeiro run reproduziu apenas o `WinError 5` ambiental já
    conhecido. A regressão visual real preservou título, Focus, Curva,
    Convergência, skip link e movimento reduzido em 375, 768, 1024, 1440 e
    844×390 px, sempre com `scrollWidth == innerWidth`.
- **Etapa 4 · incremento 2 (2026-08-27)** — hierarquia integrada:
  - `pagina_resumo.py` conecta os caches aos três motores e apresenta na
    primeira dobra prioridade, veredito, duas–quatro provas, datas, fonte,
    limite e condição de mudança. Nenhuma fórmula foi movida para a UI.
  - A Home agora segue Resumo → Expectativas → Curva → Carteira. Focus × Curva
    virou evidência do Resumo; as apresentações antigas de Convergência e
    Radar permanecem no repositório e testadas, mas não duplicam seções.
  - `DadosRadar` carrega o cenário uma vez: no Resumo entra no máximo o sinal
    externo de maior impacto absoluto, sem repetir Focus; o contrato completo
    continua alimentando a Carteira. Falhas de mercado ou notícias ficam
    isoladas no Radar.
  - Gate final: 172 testes aprovados fora do sandbox; módulos compilados;
    `pip check` e `git diff --check` limpos. A página foi validada em 375, 768,
    1024, 1440 e 844×390 px sem rolagem horizontal, com as quatro âncoras,
    primeira dobra legível e significado independente de cor.
- **Etapa 4 · incremento 3 (2026-08-27)** — cenário de curva:
  - `curva_cenarios.py` recebe fotografia e choque explícitos, aplica o mesmo
    deslocamento a cada taxa sem mutar os pontos e devolve comparação,
    inclinação, narrativa e limites. Entradas não finitas, vazias, incoerentes
    ou além de ±200 bps falham fechado.
  - A seção Curva ganhou o controle de −100 a +100 bps, métricas das pontas,
    inclinação inalterada por construção, gráfico Observada × Cenário e tabela
    exata sob divulgação progressiva. Hipótese e limites aparecem antes de
    qualquer interpretação.
  - Treze testes novos cobrem motor, guardrails, apresentação tracejada,
    interação do slider e degradação sem curva. Gate final: 185 testes,
    `py_compile`, `pip check` e `git diff --check` aprovados.
  - Validação visual real em 375, 768, 1024, 1440 e 844×390 px confirmou duas
    curvas, slider, limites, cartões responsivos e ausência de rolagem
    horizontal; o significado não depende somente de cor.
- **Etapa 4 · incremento 4 (2026-08-27)** — metodologia e narrativa:
  - `METODOLOGIA_FOCUSLENS.md` virou o ponto canônico da integração: registra
    a ordem de prioridade, o lugar de cada fato, as janelas por fonte, o papel
    do cenário mecânico e os limites que impedem leitura causal.
  - O Resumo ganhou divulgação progressiva do método. A explicação identifica
    por que a prioridade atual lidera e separa motores, hipótese, contexto do
    Radar e dados locais da carteira, sem duplicar números ou fórmulas.
  - O AppTest do Resumo passou a validar a narrativa integrada. Gate final:
    185 testes, `py_compile`, `pip check` e `git diff --check` aprovados.
  - Validação visual real em 375, 768, 1024, 1440 e 844×390 px confirmou o
    método recolhido por padrão, conteúdo aberto legível e ausência de rolagem
    horizontal.
- **Etapa 4 · incremento 5 (2026-08-27)** — fechamento da publicação:
  - A captura `focuslens-br-v2.0.png` foi gerada da aplicação real; o SVG
    `arquitetura-focuslens-v2.0.svg` documenta fontes, adaptadores, motores,
    orquestração e guardrails com descrição acessível.
  - Release notes, README e texto de LinkedIn foram alinhados à jornada final.
    A auditoria não encontrou segredo, PII, extensão sensível ou vulnerabilidade
    conhecida; os dois caches contêm somente campos públicos documentados.
  - As dependências diretas e 39 distribuições transitivas têm licenças
    permissivas/compatíveis. BACEN/Focus e Tesouro confirmaram ODbL; demais
    fontes ficam atribuídas e não são redistribuídas como bases brutas.
  - Gate final: 185 testes, `py_compile`, `pip check` e `git diff --check`
    aprovados. A primeira dobra passou em 375/768/1024/1440/844×390 px.
  - O repositório segue privado. A licença do código e um e-mail não mascarado
    nos commits são decisões pendentes antes da tag/release e abertura pública.
- **Etapa 5 · FocusLens Mobile `v0.1` (2026-08-27)** — fundação móvel:
  - O Raul redirecionou o produto de um novo polimento Streamlit para um app
    Android/iOS. O protótipo web não publicado foi preservado no stash
    `codex-web-cockpit-before-mobile-pivot-2026-08-27`.
  - `mobile/` nasceu em React Native 0.86, Expo 57, React 19 e TypeScript 6. A
    navegação reúne Hoje, Carteira, Cenários e Entenda sem depender do HTML ou
    do Streamlit em produção.
  - Hoje oferece quatro sinais tocáveis e cruza cada um com a carteira demo;
    Carteira calcula peso e oculta valores; Cenários responde a choques de
    −100 a +100 bps; Entenda explica Sinal → Evidência → Exposição → Limite.
  - Toda posição e valor são sintéticos. O app não conecta conta, não persiste
    carteira real, não recomenda ação e mostra data/fonte junto das leituras.
  - A marca lente + curva foi criada deterministicamente em SVG e rasterizada
    em PNG para ícone, adaptive icon e modo monocromático.
  - Gate móvel: TypeScript limpo, 6 testes de domínio e bundle Android gerado
    pelo Metro. O runtime foi validado em 375×812, 430×932, 768×1024 e 844×390,
    com quatro abas e interações reais, sem overflow horizontal.
  - A suíte Python permaneceu íntegra: 185 testes, `py_compile`, `pip check` e
    `git diff --check` aprovados; nenhum motor `v1.12`–`v2.0` foi alterado.
  - `npm audit --omit=dev` registrou zero vulnerabilidade alta/crítica e dez
    moderadas transitivas do toolchain Expo. O downgrade incompatível sugerido
    por `audit fix --force` não foi aplicado; isso bloqueia produção em loja,
    não o protótipo local.
  - Próximo incremento concluído abaixo: snapshot JSON versionado produzido
    pelos motores Python e provider read-only com fallback demo.
- **Etapa 5 · incremento 2 (2026-08-27)** — contrato vivo Python → mobile:
  - `mobile_snapshot.py` consome os quatro contratos aprovados e gera schema
    `1`, com datas ISO, veredito, provas, fontes, limites e sinais. O artefato
    não aceita `positions`, `amount` nem chaves pessoais.
  - `gerar_mobile_snapshot.py` usa somente os caches públicos locais e grava
    `mobile/src/data/liveSnapshot.json` com ordenação estável, newline final,
    `fsync` e troca atômica.
  - O provider TypeScript valida a borda e combina a carteira demo somente em
    memória. Versão desconhecida, documento inválido ou dado pessoal ativam
    fallback explicitamente rotulado, sem derrubar a navegação.
  - A tela Hoje identifica “Dados públicos”/“Demonstração”, data e fontes. O
    adaptador não inventa efeito da Curva por classe quando o motor não o
    fornece.
  - Gate: 191 testes Python, 10 testes móveis, `py_compile`, `pip check`,
    TypeScript, export Android e `git diff --check` aprovados. Quatro viewports
    passaram sem overflow horizontal.
- **Direção institucional · FocusLens Embedded (2026-08-27)** — roadmap
  aprovado e documentado:
  - `docs/ESTRATEGIA_INSTITUCIONAL.md` define comprador, proposta de valor,
    Intelligence API, Exposure Adapter, alertas explicáveis, Governance Studio,
    SDK, piloto, métricas e modelo de implantação/comercial;
  - `docs/ARQUITETURA_INSTITUCIONAL.md` define fronteiras pública/privada,
    receipts, identidade e consentimento, segurança, observabilidade,
    governança de regra e gates de sandbox, piloto e produção;
  - a seção 14 de `PLANO_FOCUSLENS.md` fecha a ordem 5A → 5B → 5C → 6 → 7 →
    8. A seção 13 continua sendo a próxima execução, sem antecipar API, Open
    Finance ou integração bancária;
  - validação documental: links locais e `git diff --check` aprovados. Como a
    mudança toca documentação raiz e `mobile/`, também passaram a suíte Python
    completa, TypeScript, 10 testes móveis e export Android. As primeiras
    execuções encontraram somente os ruídos ambientais já conhecidos
    (`WinError 5` na limpeza temporária e `spawn EPERM` no Hermes dentro do
    sandbox); a repetição fora do sandbox passou sem mudança de código.
- **Etapa 5 · configuração do development build (2026-08-28)** — em andamento:
  - adicionados `expo-dev-client`, `react-native-safe-area-context` e
    `expo-splash-screen`; Expo atualizado de `57.0.17` para `57.0.18` por
    compatibilidade indicada pelo próprio Expo;
  - `eas.json` define APK de desenvolvimento, simulador iOS e preview interno;
    `app.json` define identificadores nativos, scheme e rotação; safe areas
    deixaram de depender do padding manual do status bar; alvos interativos
    mínimos subiram para 48 px e cabeçalhos aceitam quebra com texto ampliado;
  - dois testes de configuração e um teste do snapshot realmente empacotado
    elevaram o gate móvel de 10 para 13 casos;
  - `expo install --check`, Expo Doctor `21/21`, TypeScript, 13 testes e export
    Android/Hermes com 603 módulos aprovados; npm audit sem alta/crítica e com
    11 moderadas transitivas sem correção compatível;
  - a suíte Python completa aprovou 191 testes e `pip check` não encontrou
    dependência quebrada;
  - `docs/VALIDACAO_DEVELOPMENT_BUILD.md` registra comandos, segurança,
    instalação, offline, checklist físico e rota iOS;
  - login EAS e vínculo de `@raulsallesr/focuslens-br` concluídos; os APKs
    `development` e `preview` foram gerados e instalados no POCO X8 Pro;
  - DB-01 a DB-05 aprovados: quatro abas e snapshot continuaram disponíveis após
    encerrar e reabrir o preview em modo avião; DB-06 segue automatizado;
  - DB-07 a DB-09 aprovados depois da confirmação física de paisagem, safe areas,
    rotação e botão Voltar;
  - o aparelho usa Android 16 (`BP2A.250605.031.A3`); pendência real: DB-10 a
    DB-12. A seção 13 permanece aberta até o fechamento de acessibilidade.
- **Etapa 5B · carteira local segura `v0.3.0` (2026-08-28)** — implementação:
  - contrato privado `v1` separado do snapshot público, limitado a 100 posições
    e validado antes de leitura ou gravação;
  - editor móvel com criar/editar/excluir, teclado decimal, erros junto aos
    campos, ocultação de valores, confirmações destrutivas e alvos de 48 px;
  - chave AES-256 no SecureStore e documento AES-GCM autenticado em
    `Paths.document`, com gravação temporária e substituição do arquivo;
  - falha fechada para chave ausente, conteúdo adulterado ou schema inválido;
    web permanece em demonstração e não persiste carteira;
  - `expo-crypto ~57.0.2`, `expo-file-system ~57.0.6` e
    `expo-secure-store ~57.0.2` adicionados; plugin de backup Android configurado
    e Face ID não declarado;
  - TypeScript, 20 testes, export web e Android/Hermes com 633 módulos aprovados;
    o primeiro Hermes no sandbox falhou com `spawn EPERM` e passou fora dele;
  - preview EAS `67b97c57-ce20-4cb6-8c21-570c4742762e` concluído para o commit
    `9308f02`, fingerprint `a28c993ae571b5d58d7eea95f8fe6fc877c71023`;
  - validação física posterior no `v0.4.0`: CL-02 a CL-10 aprovados; CL-11 a
    CL-13 pendentes.
- **Etapa 5B · importação B3 sanitizada `v0.4.0` (2026-08-28)** — implementação:
  - seletor nativo aceita somente XLSX de até 5 MB e cria cópia temporária no
    cache privado; a cópia é apagada depois da leitura e o original não é alterado;
  - parser ZIP/XML mínimo lê somente as seis abas conhecidas da exportação B3,
    ignora a dimensão `A1` incorreta e mantém apenas ativo, classe e valor;
  - limites de expansão, entradas, XML, strings, linhas, células, posições e
    valores bloqueiam arquivo excessivo ou malformado; macro e DTD/entidade são
    recusados;
  - classes ainda fora do contrato móvel, como cripto e ouro, não são
    remapeadas: aparecem na contagem de exclusões da prévia;
  - a pessoa revisa quantidade, total, abas, exclusões e posições antes de
    confirmar; a importação substitui a carteira inteira, nunca mescla em silêncio;
  - `expo-document-picker ~57.0.1` e `fflate 0.8.3` adicionados; app elevado a
    `v0.4.0`, Android `versionCode 4` e iOS `buildNumber 4`;
  - TypeScript, 25 testes, export web, compatibilidade Expo e bundle
    Android/Hermes com 640 módulos aprovados;
  - preview EAS `c7695638-2f38-42a4-af07-92303f2a5ce0` concluído para o commit
    `c6bb875`, fingerprint `4df3790bd18465bb8a429b23f9814aabf1ac6dc8`,
    app `0.4.0`, build `4`; expira em 2026-09-11;
  - validação física parcial: BI-01 a BI-03 aprovados no Android 16; BI-04 a
    BI-13 pendentes.
- **Etapa 5B · refinamento de utilidade `v0.4.1` (2026-08-28)** — implementação:
  - Home reorganizada para começar pelo recorte da carteira, com quantidade de
    posições/classes, concentração e cobertura real dos sinais;
  - ausência de efeito no snapshot é mostrada como limite, sem inventar relação
    por classe ou alterar o contrato público `v1`;
  - Carteira resume distribuição por classe e mostra só as cinco maiores
    posições inicialmente, com expansão explícita;
  - Hoje deixou de depender de carrossel horizontal; selos e textos distinguem
    corretamente carteira local, demonstração e cofre bloqueado;
  - motores Python, snapshot público, cofre privado, importador e Etapa 5C não
    foram alterados.
- **Etapa 5B · modo discreto e Cenários úteis `v0.4.2` (2026-08-28)** — implementação:
  - ocultação de valores elevada para o estado da sessão no `App.tsx`, mantendo
    a preferência entre Carteira, Hoje e Cenários sem persistir novo dado;
  - Cenários passa a abrir em +50 bps e traduz a régua também para pontos
    percentuais, mantendo 0 e os cinco choques existentes disponíveis;
  - resumo por tom agrega apenas `PortfolioImpact` já produzido pela matriz
    educacional e expõe a parcela sem relação classificada;
  - lista de impactos mostra quatro posições inicialmente e oferece expansão
    explícita, com valores mascarados quando o modo discreto está ativo;
  - TypeScript, 29 testes móveis e Android/Hermes com 640 módulos aprovados;
    quatro viewports, inclusive 375×812 e 844×390, sem overflow horizontal.
    Preview EAS ainda não gerado.
- **Etapa 5B · Home em 10 segundos `v0.4.3` (2026-08-28)** — implementação:
  - a ordem visual passa a ser recorte pessoal → mercado → sinais, corrigindo a
    divergência entre intenção documentada e renderização anterior;
  - maior classe, maior posição e relações atuais aparecem como fatos derivados,
    com percentuais e sem revelar qualquer montante;
  - a Home possui uma ação principal contextual: montar carteira na demonstração
    ou explorar sensibilidade quando a carteira local já existe;
  - `largestPosition` deriva o destaque somente das posições carregadas; nenhum
    contrato público, motor, matriz educacional ou persistência mudou;
  - TypeScript, 30 testes móveis e Android/Hermes com 640 módulos aprovados;
    ordem, conteúdo e ausência de overflow confirmados em 375×812, 430×932,
    768×1024 e 844×390. Preview EAS ainda não gerado.
- **Etapa 5B · sua carteira em 1 minuto `v0.4.4` (2026-08-31)** — implementação:
  - no modo demonstração, a jornada pessoal aparece antes do patrimônio
    fictício e apresenta importação B3 como caminho principal;
  - entrada manual continua visível como alternativa secundária e abre o mesmo
    editor/cofre já aprovado;
  - em carteira local, “Adicionar posição” permanece como ação principal e a
    importação continua no lugar de substituição consciente;
  - sucesso da primeira importação mantém feedback mesmo quando o modo muda de
    demonstração para carteira local;
  - TypeScript, 30 testes móveis e Android/Hermes com 640 módulos aprovados;
    ordem, alvos de 52 px e ausência de overflow confirmados em 375×812,
    430×932, 768×1024 e 844×390. Parser B3, cofre, motores, snapshot público
    `v1`, Etapa 5C e Embedded não mudaram.
  - preview EAS interno `6199d700-82ca-44df-8ede-6987679c2566` concluído no
    commit `565b071c72fcdd4583fb951f8edd97cbec6dde4b`, build `8`, fingerprint
    `60a05723598a9a039fc90320bcf2a45eb945acaf`; o APK expira em 2026-09-14 e
    ainda não possui evidência física deste corte.
- **Etapa 5C · acompanhamento explicável `v0.5.0` (2026-08-31)** — implementação:
  - a decisão explícita do Raul libera o desenvolvimento da 5C sem transformar
    BI-04 a BI-13, CL-11 a CL-13 ou DB-10 a DB-12 em aprovados;
  - linha do tempo local preserva no máximo oito snapshots públicos `v1`, usa
    gravação temporária e rejeita qualquer documento que contenha carteira;
  - comparação usa somente valores, textos, tons e IDs literais entre duas
    fotografias, sem interpretar percentual ou recalcular motor;
  - favoritos persistem somente IDs de sinais no cofre nativo e degradam para
    estado de sessão explícito no renderer web ou quando o storage falha;
  - alerta selecionado mostra o que mudou, o que prova, onde afeta e o que não
    prova; relação vazia permanece vazia, sem efeito inventado;
  - app elevado a `v0.5.0`, Android `versionCode 9` e iOS `buildNumber 9`;
    TypeScript, 37 testes e Android/Hermes com 647 módulos aprovados;
  - layout e interação aprovados em 375×812, 430×932, 768×1024 e 844×390,
    sem overflow horizontal ou alvo abaixo de 44 px. Preview EAS não gerado.
- **Etapa 5C · simulador local de aportes `v0.5.1` (2026-08-31)** — implementação:
  - a pessoa informa um valor hipotético e escolhe explicitamente uma das seis
    classes do contrato privado; não há valor, classe ou produto sugerido;
  - o domínio soma o aporte somente à classe selecionada e compara total e pesos
    antes/depois, inclusive para classe ausente ou carteira vazia;
  - a hipótese vive apenas no estado da tela: não altera carteira, cofre,
    histórico público, favoritos, snapshot ou rede;
  - app elevado a `v0.5.1`, Android `versionCode 10` e iOS `buildNumber 10`;
    TypeScript, 42 testes e Android/Hermes com 649 módulos aprovados;
  - formulário e resultado aprovados em 375×812, 430×932, 768×1024 e 844×390,
    sem overflow horizontal ou alvo abaixo de 44 px. Preview EAS não gerado.
- **Etapa 5C · cobertura automatizada `v0.5.2` (2026-08-31)** — implementação:
  - testes reorganizados por camada, sem misturar domínio, componentes e E2E;
  - `jest-expo ~57.0.5`, Jest `~29.7.0` e React Native Testing Library `14.0.1`
    ficam somente em `devDependencies`; o junction externo de `node_modules`
    foi preservado;
  - 42 testes de domínio, 6 de componentes e 4 contratos Maestro passaram;
  - dois fluxos Maestro usam `testID` de um mapa JSON canônico para percorrer as
    quatro abas e o simulador; execução em Android/iOS ainda pendente;
  - executor Windows portátil valida Java/Maestro/ADB, sintaxe, exclusão mútua,
    autorização USB, package e versão nativa antes de executar; Temurin
    `17.0.20.1`, Maestro `2.9.0` e ADB `37.0.1` foram validados, mas nenhum
    dispositivo estava conectado nesta sessão;
  - app elevado a `v0.5.2`, Android `versionCode 11` e iOS `buildNumber 11`;
    TypeScript e Android/Hermes com 650 módulos aprovados;
  - auditoria npm permanece com zero vulnerabilidade alta/crítica e 11 moderadas
    transitivas no toolchain Expo; `audit fix --force` não foi aplicado porque
    propõe downgrade incompatível para Expo 46;
  - preview EAS interno `c08e5397-427f-42c2-a163-ab5cd815cb55` concluído no
    commit `1c477f5`, build `11`, fingerprint
    `4a0bc79db5a2beeb9b694f3ee8718ff13be38dff`, sem variáveis `Plain text` ou
    `Sensitive`; o APK expira em 2026-09-14 e teve a instalação confirmada pelo
    Raul, sem verificação ADB ou avaliação física nesta sessão;
  - o fechamento documental de 2026-08-31 revalidou TypeScript, 42 testes de
    domínio, 6 de componentes, 4 contratos E2E, export Android/Hermes com 650
    módulos, links locais e `git diff --check`. O primeiro export encontrou o
    `spawn EPERM` já conhecido dentro do sandbox e passou fora dele sem mudança
    de código.
- **Etapa 5C · revisão guiada da semana `v0.5.3` (2026-08-31)** — implementação:
  - Hoje oferece uma entrada opcional depois da fotografia e do histórico; uma
    revisão em andamento pode ser retomada sem deslocar o recorte pessoal do topo;
  - Entenda abre somente um dos cinco passos por vez: mudança literal, prova,
    relação com a carteira, exploração em Cenários e limite;
  - o sinal escolhido, favorito, fonte, data, `effects`, impactos e posições vêm
    somente dos objetos existentes em memória; ausência de histórico ou efeito
    permanece explícita, sem completar lacunas;
  - a ida a Cenários não muda valor, classe ou choque e oferece retorno direto à
    etapa final; todo o progresso vive em `App.tsx` e some ao reiniciar o app;
  - app elevado a `v0.5.3`, Android `versionCode 12` e iOS `buildNumber 12`;
  - TypeScript, 42 testes de domínio, 10 de componentes, 4 contratos E2E e o
    export Android/Hermes com 651 módulos passaram;
  - a jornada completa passou em 375×812, 430×932, 768×1024 e 844×390, sem
    overflow horizontal ou alvo visível abaixo de 44 px;
  - nenhum preview EAS, Maestro ou gate físico foi executado. O APK instalado
    permanece `v0.5.2/11`; os gates físicos anteriores continuam pendentes.
- **Etapa 5C · laboratório do dinheiro `v0.5.4`–`v0.5.6` (2026-08-31)** —
  implementação:
  - `moneyLab.ts` usa taxa anual efetiva informada pela pessoa, converte para
    equivalente mensal e separa capital colocado de juros do cenário;
  - “Quanto vira?” inclui linha do tempo textual/visual e inflação opcional em
    dinheiro do início, sem chamar o resultado de retorno esperado;
  - meta ao contrário resolve aporte mensal sem permitir resultado negativo;
    preço de esperar compara o mesmo horizonte e explicita aportes pulados;
  - hábito diário, semanal ou mensal é convertido para média mensal sem
    julgamento; desafio compara +1 p.p. com +R$ 150/mês depois do palpite;
  - `MoneyLabSession` vive em `App.tsx`, permanece entre abas e some ao
    reiniciar; não existe storage, rede, snapshot ou leitura da carteira;
  - app consolidado em `v0.5.6`, Android `versionCode 15` e iOS
    `buildNumber 15`;
  - TypeScript, 51 testes de domínio, 16 de componentes, 4 contratos E2E e
    export Android/Hermes com 653 módulos passaram;
  - as cinco ferramentas passaram em 375×812, 430×932, 768×1024 e 844×390, sem
    overflow horizontal ou alvo visível abaixo de 44 px;
  - não houve preview EAS, Maestro ou gate físico. O APK instalado permanece
    `v0.5.2/11` e todos os gates pausados continuam pendentes.
- **Etapa 5C · expansão do laboratório `v0.5.7`–`v0.6.0` (2026-09-01)** —
  implementação:
  - “O poder do tempo” calcula dobra com/sem aporte, marcos de R$ 10 mil,
    R$ 50 mil e R$ 100 mil e uma régua tocável de 1 a 50 anos;
  - “Dinheiro que entra” converte taxa anual em equivalente mensal e compara
    aporte extra único ou repetido ao fim de cada ano;
  - “Minha segurança” divide a reserva atual pelo gasto essencial escolhido e
    calcula o caminho mecânico para três, seis ou doze meses, sem rendimento;
  - “Compare completo” põe sem aporte/com aporte lado a lado e revela inflação
    e custo anual hipotético somente quando solicitados; imposto continua fora;
  - `MoneyLabExpansionPanel` reutiliza `MoneyLabSession` mantida por `App.tsx`;
    não existe storage, rede, snapshot, carteira, telemetria ou dependência nova;
  - app consolidado em `v0.6.0`, Android `versionCode 19` e iOS
    `buildNumber 19`; `v0.5.7/16`, `v0.5.8/17` e `v0.5.9/18` são marcos lógicos
    sem builds EAS intermediários;
  - TypeScript, 61 testes de domínio, 22 de componentes, 4 contratos E2E e
    export Android/Hermes com 654 módulos passaram;
  - as quatro trilhas passaram em 375×812, 430×932, 768×1024 e 844×390, sem
    overflow horizontal ou alvo interativo visível abaixo de 44 px;
  - não houve preview EAS, Maestro ou gate físico. O APK instalado permanece
    `v0.5.2/11` e todos os gates pausados continuam pendentes.

## Fila priorizada

Critério atual: publicar valor pequeno e completo, reaproveitando cada motor na
integração seguinte.

| Prioridade | Estado | Melhoria | Impacto | Esforço |
|---|---|---|---|---|
| P0 | Entregue | Focus Semanal (`v1.12`) | Alto | Médio |
| P1 | Entregue | Curva Tesouro (`v1.13`) | Muito alto | Alto |
| P2 | Entregue | Focus × Curva (`v1.14`) | Muito alto | Alto |
| P3 | Release candidate (5/5) | FocusLens BR integrado (`v2.0`) | Muito alto | Alto |
| P4 | Entregue (`v0.1`) | Fundação FocusLens Mobile | Muito alto | Alto |
| P5 | Entregue | Snapshot vivo Python → app móvel | Muito alto | Alto |
| P6 | Pausado | Distribuição aprovada; DB-10 a DB-12 aguardam retomada | Alto | Alto |
| P7 | Entregue (`v0.4.4`) | Refinar utilidade; evidência física parcial preservada | Muito alto | Alto |
| P8 | Entregue (`v0.5.2`) | APK instalado por relato; harness E2E pronto e gates físicos pausados | Muito alto | Alto |
| P8.1 | Entregue (`v0.5.3`) | Revisão guiada da semana e Entenda contextual | Muito alto | Médio |
| P8.2 | Entregue (`v0.5.6`) | Laboratório educacional para iniciantes | Muito alto | Médio |
| P8.3 | Entregue (`v0.6.0`) | Tempo, aportes extras, reserva e comparação completa | Muito alto | Médio |
| P9 | Planejado | Embedded: API, receipt, sandbox e SDK | Muito alto | Muito alto |
| P10 | Planejado | Governance Studio + piloto institucional | Muito alto | Muito alto |
| Depois | Planejado | Open Finance + Advisor Copilot, após gates | Muito alto | Muito alto |
| Depois | Fila | Backtest por horizonte e regime | Muito alto | Alto |
| Depois | Fila | Curva real IPCA+, cupom e forwards | Alto | Alto |
| Depois | Fila | Exportação local | Médio | Médio |

## Bloqueios

- Escolher a licença do código antes da abertura pública.
- Aceitar a exposição do e-mail não mascarado dos commits ou autorizar uma
  reescrita controlada do histórico.
- Tag, release e visibilidade pública dependem dessas decisões e de autorização
  explícita do Raul.
- O app móvel pode ser testado localmente, mas publicação em loja exige
  resolver ou aceitar formalmente as vulnerabilidades moderadas transitivas do
  toolchain Expo, além dos gates de segurança descritos na arquitetura móvel.
- Os APKs internos anteriores foram instalados no POCO X8 Pro e expiram em
  2026-09-11. O preview `v0.4.0` foi instalado no Android 16 e aprovou BI-01 a
  BI-03 e CL-02 a CL-10. O `v0.5.2/11` também teve instalação confirmada pelo
  Raul; os testes restantes estão pausados, não aprovados. Temurin `17.0.20.1`,
  Maestro `2.9.0` e ADB `37.0.1` estão disponíveis em toolchain portátil, mas a
  última consulta ADB encontrou zero aparelhos conectados.

## Conceitos relacionados

(nenhum ainda — projeto começou fora do vault Obsidian do hub da Fits)
