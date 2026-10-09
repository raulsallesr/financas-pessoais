# CONTEXT — Finanças Pessoais

> Fonte de verdade operacional curta para retomada. Não é changelog.
> O histórico detalhado está no Git e nas seções 24–35 de
> `docs/product/PLANO_FOCUSLENS.md`.
> O último handoff extenso, anterior a esta condensação, está no commit `54382df`.

## Estado em uma tela

- **Nova direção (2026-10-09):** o FocusLens vira o módulo **Macro** de uma plataforma
  maior, provisoriamente chamada **Lastro**.
  - Novo módulo **Ativos B3** (`ativos/`), com plano em `docs/product/PLANO_LASTRO.md`.
  - Decisões do Raul: uso pessoal com repositório público como portfólio; motor Python
    + web Streamlit primeiro; fontes oficiais e gratuitas (CVM + COTAHIST); nome novo
    para a plataforma.
  - A **Fase 0 está concluída**: navegação Macro + Ativos e relatório de cobertura em
    `docs/validation/COBERTURA_ATIVOS_FASE0.md`. Ações e FIIs são viáveis; ETFs pedem
    tabela curada.
  - A primeira fatia vertical de ações está implementada: adapters CVM/COTAHIST,
    base point-in-time, 32 métricas/insumos (incluindo DPA), presets/filtros, pipeline
    Parquet/JSON e página **Busca avançada**. A visão geral **Ativos B3** foi preservada.
  - A segunda fatia vertical, **Busca de FIIs**, também está implementada: informes
    mensais/trimestrais, composição e tipo, renda, vacância, presets/filtros,
    comparador, CSV e derivados `fiis.parquet`/`fiis_meta.json`. O CLI aceita
    `--classe {acoes,fiis,todos}` e usa `todos` por padrão.
  - O corte de valor estimado também está concluído, exceto DCF: taxa livre de risco
    interpolada da curva prefixada local, premissas editáveis, Graham, Bazin, Gordon,
    múltiplos setoriais, modelos patrimonial e de renda para FIIs, faixa P25–P75 e
    página unificada **Ficha do ativo**. As buscas calculam tudo em memória; os parquets
    esquema 3 persistem apenas `dpa` e `rendimento_12m_cota` como novos insumos.
  - Busca avançada no esquema 2: `alertas` substitui o nome anterior; DY usa dividendos
    e JCP pagos TTM da DFC (DVA apenas como fallback `dy_dva`); P/ACL usa passivo
    exigível; units podem derivar valor de mercado pela composição do FCA.
  - Pipeline real em 2026-10-09, com liquidez mínima de R$ 100 mil/dia: 244 tickers,
    82,0% com P/L, 95,5% com DY, 98,8% com DPA e nenhuma pendência de CNPJ. O metadado registra 12
    tickers resolvidos por nome, inclusive `AMAR3`, `BPAC3/5/11` e `CSNA3`.
  - GFSA3 e MEAL3 permanecem com `escala_suspeita` e, por segurança, sem valor de
    mercado nem múltiplos dependentes. GFSA combina grupamento/diluição e composição
    defasada; MEAL tem sequência anômala de quantidades ON/PN nos informes de 2026.
  - Pipeline real de FIIs em 2026-10-09, com cotação até 2026-10-08 e liquidez mínima
    de R$ 100 mil/dia: 155 fundos, 100% com P/VP, 99,4% com DY/rendimento 12m e 47,7% com
    vacância. Tipos: 72 Tijolo, 51 Papel, 22 Fundo de fundos, 4 Híbrido e 6 Outros.
  - O DY 12m agora descarta mês com `Percentual_Dividend_Yield_Mes` negativo ou acima
    de 5%, preserva zero como válido e anualiza pelos meses válidos; menos de 6 válidos
    fica vazio. Rentabilidade mensal fora de `[-50%; 50%]` invalida `rentab_12m`.
    Ambos geram `dy_dados_suspeitos`; a carga real atual registrou 27 fundos. No XPML11,
    o mês negativo de 2026-01 foi excluído e o DY 12m passou de 3,05% para 10,00% pela
    regra solicitada (soma válida de R$ 9,7622, anualizada por 11 meses, sobre R$ 106,50).
  - Colisões do mesmo ISIN em vários CNPJs agora usam desempate nominal estrito e
    auditável. `KISU11`, `SNEL11`, `TRXF11` e `XPML11` foram resolvidos pelo nome de
    pregão. Restam 20 pendências fail-closed: 16 sem informe mensal correspondente,
    3 sem palavra nominal em comum (`PQDP11`, `RBRY11`, `ZAGH11`) e 1 empate nominal
    (`HSAF11`). O metadado esquema 3 registra resolvidos e motivo por pendência.
  - O sandbox bloqueou `%USERPROFILE%\.cache\lastro\derived`; o pipeline conjunto
    foi validado via `LASTRO_DADOS_DIR=.pytest_tmp-derived-real-valuation`, fora do git.
  - Valuation real com a curva de 2026-10-07 (`rf=12,7965%`): ações com 29 linhas sem
    faixa e 215 com faixa; FIIs com 16 sem faixa e 139 com faixa. O alerta calculado
    `valuation_fragil` marcou 21 ações e 32 FIIs, sem ser persistido no parquet.
  - Gate atual: 354 testes, cobertura total de 87,15% e Ruff limpo. O `tmp_path` sob
    Python 3.13/Windows foi executado com criação `0777` isolada; diretórios temporários
    ainda podem emitir `WinError 5` na limpeza tardia sem indicar falha funcional.
  - **Próximo passo:** DCF de dois estágios, score, tabela curada de ETFs e atualização
    automática dos derivados permanecem como cortes independentes.
  - **Pendência de ambiente:** `requirements.txt` tem ACL legado e não aceitou escrita
    neste sandbox. `numpy` e `pyarrow` ficaram explicitados em `requirements-dev.txt`;
    movê-los para o arquivo base quando a ACL for normalizada.
  - **Pendente do Raul:** decidir o retorno total para backtest (DVA oficial
    aproximada ou Yahoo ajustado).
- Produto (módulo Macro): **FocusLens BR**, educacional e orientado à privacidade.
  `mobile/` é a interface principal; o app Streamlit permanece como referência funcional.
- Branch: `main`. Corte funcional: mobile `v0.6.4`, Android `versionCode 23`,
  iOS `buildNumber 23`.
- Entrega atual: revisão semanal opcional e laboratório do dinheiro organizados
  por intenção, com estado somente na sessão.
- Aceite manual: em 2026-09-02, o Raul informou que testou o app atual no POCO
  X8 Pro e considerou a experiência satisfatória para o beta pessoal.
- Preview candidato: `v0.6.4`, build `23`, EAS
  `6ac1268d-5902-46b4-8108-457977bb7e1f`, commit `a2bb4b5`, `FINISHED` em
  2026-09-02. Sem ADB, não há confirmação independente de que o binário
  avaliado manualmente corresponde exatamente a esse package/build.
- Sprint de publicação iniciado no commit `f2ed931`: licença MIT, commits via
  GitHub `noreply`, CI Python/mobile, Ruff, cobertura com piso de 85%, README,
  carrossel e demonstração MP4/GIF. O Raul tornou o repositório público em
  2026-09-02; o workflow remoto `quality` já concluiu verde.
- A raiz pública está organizada por responsabilidade: motores em
  `focuslens/core/`, I/O em `focuslens/adapters/`, Streamlit em `focuslens/ui/`,
  executáveis em `scripts/` e documentos em quatro categorias sob `docs/`.
- Decisão vigente do Raul: o aceite manual encerra a Fase A para o escopo de
  beta pessoal/portfólio. USB/ADB e validação iOS foram dispensados e não
  bloqueiam a continuação; não devem ser apresentados como testes aprovados.
- Não rodar Maestro automaticamente. Os fluxos agora são não destrutivos e o
  runner recusa `clearState: true`, mas a execução continua manual e deliberada.
- BI-04–BI-13, CL-11–CL-13, DB-10–DB-12 e E2E nativo não foram registrados
  item a item. Deixaram de ser gates do beta por decisão do titular e ficam
  como checklists opcionais antes de eventual publicação em loja/produção.
- Polimento pós-publicação (2026-09-03): `pyproject.toml` ampliou o lint do
  Ruff (`E5`, `I`, `B`, `UP`, com `UP042` ignorado por risco/ganho — trocar
  `class X(str, Enum)` por `StrEnum` fica para depois, se quiser); imports
  reordenados em ~50 arquivos (auto-fix, cosmético); 9 `zip()` na UI ganharam
  `strict=True`; 11 blocos `try/assert False/except` nos testes viraram
  `pytest.raises(...)`. Badge de cobertura (86%) no README. `CONTRIBUTING.md`
  novo, linkado no README. `pytest tests/ -q --cov=.` e `ruff check .`
  confirmados verdes antes do commit (194 testes, 86,1%).

## Retomada segura

No repositório `01_Projetos/Financas-Pessoais`:

```powershell
git pull --ff-only
git status --short --branch
git stash list
```

Leia, nesta ordem:

1. `CLAUDE.md`;
2. este `CONTEXT.md`;
3. `docs/product/PLANO_FOCUSLENS.md`;
4. `mobile/README.md`;
5. `docs/architecture/ARQUITETURA_MOBILE.md`.

Use somente o Git interno deste projeto. Não faça `git add`, commit ou push no
Git da raiz do hub.

## Contrato de produto que não deve ser reaberto

### Experiência

- Manter as quatro abas: **Hoje, Carteira, Cenários e Entenda**.
- A Home começa pelo recorte pessoal e explica a relação com a fotografia
  pública; não vira mural genérico de mercado.
- Diferenciar sempre **demonstração** de **carteira local**.
- Em demonstração, oferecer a entrada B3 antes da carteira fictícia.
- Preservar modo discreto, revelação progressiva, feedback de toque, rótulos
  acessíveis e alvos mínimos de 44 px.
- Não criar urgência, streak, gamificação, promessa ou incentivo a giro.

### Dados, privacidade e fronteiras

- Os motores Python `v1.12`–`v2.0` continuam sendo a fonte das leituras. Não os
  reescrever durante a evolução mobile.
- `focuslens/adapters/mobile_snapshot.py` entrega somente fotografia pública já calculada no
  contrato `v1`; `snapshotProvider.ts` valida o JSON e usa fallback demo
  explícito quando necessário.
- A carteira local permanece separada do snapshot público, cifrada com
  AES-256-GCM, com chave pequena no cofre nativo e documento no filesystem
  privado do app.
- O importador B3, históricos, favoritos e persistências existentes permanecem
  com seus contratos atuais.
- Revisão guiada, família escolhida e entradas do laboratório vivem apenas em
  memória durante a sessão. Reiniciar o processo descarta esse estado.
- Não solicitar nem versionar planilha de carteira real, valores pessoais,
  identificadores ou capturas sensíveis. Evidência física deve ser sintética.

### Fora de escopo

- Alterar motores Python, fórmulas financeiras existentes, cofre, importador B3,
  persistências ou o snapshot público `v1`.
- Adicionar dependência, rede, telemetria, retorno previsto, recomendação,
  produto, ordem, autenticação, Open Finance ou Embedded.
- Preencher hipóteses com carteira, produto, instituição ou fonte externa.
- Chamar projeção educacional de garantia, plano financeiro ou taxa indicada.
- Iniciar Etapa 6 antes da decisão explícita e dos gates correspondentes.

## O que já está implementado

### Base móvel

- Fotografia pública com fonte/data, histórico, favoritos, `effects`, impactos e
  relação com posições já compostos.
- Carteira local privada, entrada manual e importação B3 sanitizada com prévia.
- Estados de demonstração, fallback/offline, modo discreto e navegação pelas
  quatro abas.
- Camadas de utilidade anteriores a `v0.5.3`: leitura pessoal da Home,
  comparação de fotografias, favoritos e exploração de impactos.

### Revisão guiada `v0.5.3`

- Entrada opcional “Revisar a semana” em Hoje.
- Sequência curta em Entenda: o que mudou, o que prova, onde toca a carteira,
  o que explorar em Cenários e o que não prova.
- Usa somente fotografia pública, favoritos, fonte/data, `effects`, impactos e
  posições já presentes em memória.
- Sem histórico, declara que não há comparação. Sem efeito, não inventa posição
  ou impacto.
- A ida a Cenários preserva o que já estava digitado, não preenche hipótese e
  permite voltar ao encerramento da revisão.

### Laboratório do dinheiro `v0.5.4`–`v0.6.4`

As experiências estão agrupadas por três intenções — começar do zero, enxergar
o caminho e testar situações da vida real — com uma família visível por vez:

- “Quanto vira?”: valor inicial, aporte mensal, taxa efetiva anual e prazo;
- meta mensal e custo de esperar para começar;
- inflação opcional, equivalente de hábitos e desafio taxa × aporte;
- dobra, marcos de patrimônio e régua temporal de 1 a 50 anos;
- equivalente mensal e aportes extras únicos ou anuais;
- caminho da reserva sem rendimento e com meta escolhida pela pessoa;
- comparação completa entre capital, aportes, juros, inflação e custo hipotético;
- plano flexível com aumento anual e pausa de aportes;
- à vista × parcelado, incluindo taxa implícita somente quando ela existe.
- duração de um saldo sob retiradas mensais, com reajuste anual opcional.

Convenções completas, fórmulas, limites e evidências de cada incremento estão
nas seções 24–35 de `docs/product/PLANO_FOCUSLENS.md` e em
`docs/architecture/ARQUITETURA_MOBILE.md`.

## Evidência automatizada do corte `v0.6.4/23`

Executado em 2026-09-01 e ampliado em 2026-09-02:

- `npm run typecheck`: aprovado;
- `npm test`: 70 testes de domínio, 33 de componentes e 4 contratos E2E;
- `npm run export:android`: aprovado, bundle Android/Hermes com 656 módulos;
- viewports 375×812, 430×932, 768×1024 e 844×390: sem overflow horizontal e
  sem alvo interativo visível abaixo de 44 px, inclusive com movimento reduzido.
- Python: 194 testes, Ruff aprovado e cobertura de branches em 86,1%, com
  piso de 85% configurado no CI.

O `spawn EPERM` do export e o `WinError 5` do navegador já foram reproduzidos
dentro do sandbox e passaram em execução isolada/fora dele sem mudança de
código. Trate-os primeiro como ruído do Windows/OneDrive, não como motivo para
afrouxar gates.

O preview EAS `v0.6.4/23` terminou. O Raul informou ter testado o app atual no
POCO e aceitou a experiência do beta. Não houve Maestro, ADB nem validação iOS;
por isso a versão exata do binário não foi comprovada de forma independente.

## Estado físico e toolchain

- Aparelho de referência: POCO X8 Pro, Android 16
  (`BP2A.250605.031.A3`).
- Evidência já aprovada: DB-01–DB-05 e DB-07–DB-09; DB-06 é automatizado;
  BI-01–BI-03; CL-02–CL-10.
- DB-10–DB-12, BI-04–BI-13, CL-11–CL-13 e E2E nativo permanecem sem evidência
  individual, mas foram dispensados como bloqueadores do beta pessoal.
- Temurin `17.0.20.1`, Maestro `2.9.0` e ADB `37.0.1` estão disponíveis em
  toolchain portátil. A consulta de 2026-09-02 encontrou zero aparelhos.
- O comando `npm run e2e:maestro:device:windows` confere aparelho, package e
  versão sem abrir o app; os fluxos preservam o estado local.
- O APK candidato `v0.6.4/23` expira em 2026-09-16.

Se esses testes forem retomados antes de loja/produção, usar estado descartável
ou fazer backup fora do chat. Nunca inferir aprovação pela automação e nunca
enviar evidência com dados reais da carteira.

## Stashes preservados

Não aplicar, remover, renomear ou reordenar sem pedido explícito:

```text
stash@{0}: On main: codex-focus-cache-before-mobile-handoff-2026-08-27
stash@{1}: On main: codex-web-cockpit-before-mobile-pivot-2026-08-27
stash@{2}: On main: codex-pre-focuslens-cache-2026-08-26
```

## Gates de desenvolvimento

Para mudança em `mobile/`:

```powershell
cd mobile
npm run typecheck
npm test
npm run export:android
```

Validar também os quatro viewports já usados e os alvos de 44 px. Bundles de
export, quadros e perfis de captura são temporários e não devem permanecer
versionados; somente as mídias finais aprovadas em `docs/assets/` permanecem.

Para mudança Python, usar o `.venv` externo ao OneDrive indicado no `README.md`
e rodar a suíte completa:

```powershell
pip install -r requirements-dev.txt
ruff check .
python -m pytest tests/ --cov=.
```

Maestro é sempre manual e deliberado. O comando existir não autoriza executá-lo.

## Próxima decisão

- **Lastro / Ativos B3:** base, métricas, buscas de ações/FIIs, valor estimado sem DCF
  e ficha unificada estão concluídos. Próximos cortes possíveis: DCF de dois estágios,
  Score Lastro, tabela curada de ETFs ou atualização automática dos derivados.
  Workflow, asset de release e preço ajustado continuam fora do corte atual.
- Os itens abaixo referem-se ao módulo Macro e ao mobile.
- Se o Raul quiser iniciar a Etapa 6, o próximo trabalho é fechar o contrato de
  receipt e o threat model inicial antes do sandbox institucional, seguindo a
  seção 14 de `docs/product/PLANO_FOCUSLENS.md`.
- Publicar o post do LinkedIn com o MP4/GIF já preparado é opcional e não
  altera o estado técnico do produto.
- Não planejar USB/ADB, Maestro ou iOS no escopo atual. Reabrir esses roteiros
  somente por nova decisão ou antes de distribuição em loja/produção.

## Estado da publicação pública

- O repositório é público desde 2026-09-02 por decisão explícita do Raul; o
  workflow `quality` foi conferido verde no GitHub Actions.
- Licença MIT registrada; o histórico foi preservado e os próximos commits usam
  o endereço `noreply` oficial do GitHub.
- A exposição do e-mail antigo no histórico foi aceita como custo de preservar
  hashes e rastreabilidade; não exibir o endereço em documentação ou relatório.
- A prerelease pública
  [`v0.6.4-beta`](https://github.com/raulsallesr/financas-pessoais/releases/tag/v0.6.4-beta)
  foi criada em 2026-09-02, sem APK temporário anexado.
- O ruleset ativo `Proteção da main` (`22142158`) bloqueia exclusão, force-push
  e histórico não linear sem impedir os pushes fast-forward dos workflows de
  cache. Pull request e status obrigatório não foram impostos.
- A demo pública de 21,2 segundos existe em MP4 e GIF, usa somente fotografia
  pública, carteira fictícia e estado de sessão; nenhum código do app mudou.
- Publicação em loja também depende dos gates de segurança e da decisão sobre
  vulnerabilidades moderadas transitivas do toolchain Expo.

## Prompt curto para o próximo chat

> Abra `01_Projetos/Financas-Pessoais`, rode `git pull --ff-only`, confira
> `git status --short --branch` e `git stash list`, e leia `CLAUDE.md`,
> `CONTEXT.md`, `docs/product/PLANO_FOCUSLENS.md`, `mobile/README.md` e
> `docs/architecture/ARQUITETURA_MOBILE.md`. Preserve os três stashes
> documentados. O corte
> funcional é mobile `v0.6.4/23`; o Raul informou que testou o app atual no
> POCO e aceitou o beta pessoal. O preview candidato `v0.6.4/23` terminou no
> EAS `6ac1268d-5902-46b4-8108-457977bb7e1f`; sem ADB, não associe a avaliação
> a esse package/build como evidência independente. USB/ADB e iOS foram
> dispensados e não bloqueiam o roadmap, mas também não contam como aprovados.
> Preserve quatro abas, Home pessoal,
> distinção demo × local, modo discreto, B3 antes da carteira fictícia e estado
> novo somente na
> sessão. Não altere motores Python, snapshot `v1`, cofre, importador B3 ou
> persistências; não adicione dependência, rede, telemetria, recomendação ou
> produto. Não rode Maestro automaticamente. Os fluxos preservam estado e o
> runner recusa `clearState: true`. Os checklists BI-04–BI-13, CL-11–CL-13,
> DB-10–DB-12 e E2E nativo ficam opcionais para loja/produção. A prerelease
> pública `v0.6.4-beta` e o ruleset `Proteção da main` estão ativos. A próxima
> decisão técnica é preparar receipt/threat model para a Etapa 6. Ao concluir,
> rode os gates,
> atualize a documentação sem recriar um changelog no `CONTEXT.md`, remova
> temporários e faça commit/push somente no Git interno.
