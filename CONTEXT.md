# CONTEXT — Finanças Pessoais

- **Status**: Etapa 4 do FocusLens BR (`v2.0`) concluída tecnicamente em
  2026-08-27. O release candidate está em 5/5; tag, release e abertura pública
  aguardam decisões de governança sobre licença e e-mail histórico.
- **Repositório**: https://github.com/raulsallesr/financas-pessoais (privado)
- **Fonte oficial**: BACEN, Sistema de Expectativas de Mercado (Boletim
  Focus), API pública Olinda/OData
  (`https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata`),
  sem autenticação.
- **Periodicidade**: BACEN publica o Boletim Focus toda segunda-feira; a API
  tem granularidade diária, então o app permite atualizar a qualquer momento.
- **Curva oficial**: Tesouro Transparente, conjunto diário “Taxas dos Títulos
  Ofertados pelo Tesouro Direto”, CSV aberto sob ODbL 1.0.

## Handoff para um novo chat — 2026-08-27

### Ponto de partida verificado

- O produto está estável e versionado até a `v1.14`; o commit funcional dessa
  entrega é `0f1458c` e recebeu a tag `v1.14`.
- A branch de trabalho é `main`, sincronizada com `origin/main` em 2026-08-27.
- A **Etapa 4 — FocusLens BR integrado (`v2.0`)** está concluída tecnicamente
  como release candidate. Não refazer as Etapas 1–3 nem os cinco incrementos
  da Etapa 4.
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

### Ordem de leitura e preparação

1. Trabalhe dentro deste repositório, nunca no git do hub que o contém.
2. Rode `git pull --ff-only` e confirme `git status --short --branch` limpo.
3. Leia `CLAUDE.md`, este `CONTEXT.md` e `PLANO_FOCUSLENS.md`, nessa ordem.
4. Leia `docs/AUDITORIA_PUBLICACAO_V2.0.md` e
   `docs/RELEASE_V2.0.md`; eles registram o gate e o pacote final.
5. Antes de abrir o repositório, obtenha do Raul a decisão sobre licença do
   código e sobre aceitar ou sanear o e-mail não mascarado dos commits.

### Decisões que não devem ser reabertas

- A experiência continua em uma página Streamlit, com Resumo, Expectativas,
  Curva e Carteira numa hierarquia única.
- Os motores existentes são a fonte dos cálculos. A integração não deve
  duplicar regras numéricas dentro da UI.
- BACEN/Focus, SGS e Tesouro Transparente são as fontes públicas do produto;
  ANBIMA continua opcional e fora do caminho crítico do MVP.
- Notícias, Radar e dados da carteira não entram no cálculo de convergência
  Focus × Curva. A carteira permanece local à sessão.
- Taxa de título não é previsão pura da Selic. O app continua educacional,
  sem recomendação, promessa, causalidade inventada ou probabilidade falsa.
- O visual preserva tema claro, verde-petróleo, dourado discreto, números e
  fontes perto da conclusão e detalhes por divulgação progressiva. Não criar
  dependência de fonte, ícone ou biblioteca apenas por estética.
- IPCA+, títulos com cupom, bootstrap, forwards e backtest continuam fora da
  `v2.0`, salvo nova decisão explícita do Raul.

### Prompt pronto para abrir o próximo chat

> Abra o projeto `01_Projetos/Financas-Pessoais`, rode `git pull --ff-only` e
> leia `CLAUDE.md`, `CONTEXT.md`, `PLANO_FOCUSLENS.md`,
> `docs/AUDITORIA_PUBLICACAO_V2.0.md` e `docs/RELEASE_V2.0.md`. A `v2.0` está
> pronta como release candidate; não altere motores ou refaça os cinco
> incrementos. Confirme com o Raul a licença do código e se o e-mail não
> mascarado do histórico pode permanecer público. Somente após autorização
> explícita, crie tag/release `v2.0`, altere a visibilidade e valide os links
> em sessão anônima.

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
- Streamlit em página única: `app_financas.py` chama `pagina_home.py`, que
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

## Fila priorizada

Critério atual: publicar valor pequeno e completo, reaproveitando cada motor na
integração seguinte.

| Prioridade | Estado | Melhoria | Impacto | Esforço |
|---|---|---|---|---|
| P0 | Entregue | Focus Semanal (`v1.12`) | Alto | Médio |
| P1 | Entregue | Curva Tesouro (`v1.13`) | Muito alto | Alto |
| P2 | Entregue | Focus × Curva (`v1.14`) | Muito alto | Alto |
| P3 | Release candidate (5/5) | FocusLens BR integrado (`v2.0`) | Muito alto | Alto |
| Depois | Fila | Backtest por horizonte e regime | Muito alto | Alto |
| Depois | Fila | Curva real IPCA+, cupom e forwards | Alto | Alto |
| Depois | Fila | Exportação local e simulador de aportes | Médio | Médio |

## Bloqueios

- Escolher a licença do código antes da abertura pública.
- Aceitar a exposição do e-mail não mascarado dos commits ou autorizar uma
  reescrita controlada do histórico.
- Tag, release e visibilidade pública dependem dessas decisões e de autorização
  explícita do Raul.

## Conceitos relacionados

(nenhum ainda — projeto começou fora do vault Obsidian do hub da Fits)
