# CONTEXT — Finanças Pessoais

- **Status**: v1.3 (redesign Focus + contexto em manchetes) pronto — 2026-08-04
- **Repositório**: https://github.com/raulsallesr/financas-pessoais (privado)
- **Fonte oficial**: BACEN, Sistema de Expectativas de Mercado (Boletim
  Focus), API pública Olinda/OData
  (`https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata`),
  sem autenticação.
- **Periodicidade**: BACEN publica o Boletim Focus toda segunda-feira; a API
  tem granularidade diária, então o app permite atualizar a qualquer momento.

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
- Streamlit multipage: `app_financas.py` é a home; `pages/1_Boletim_Focus.py`
  é a primeira feature. Nasce como hub multipage (não app isolado) porque a
  visão é crescer para carteira + calculadora de projeção mais adiante —
  assim não precisa migrar path/estrutura quando essas páginas chegarem.
- Separação motor puro / adaptador / UI:
  - `financas_taxonomia.py` — enums compartilhados (ClasseAtivo, Direcao,
    unidades de exibição).
  - `motor_indicadores.py` — motor genérico indicador+direção → efeito por
    classe de ativo (reaproveitável por features futuras).
  - `focus_data.py` — dataclasses e cálculo de delta/tendência (sem I/O).
  - `focus_leitura.py` — adaptador da API Olinda + cache local em
    `dados/focus_cache.json`.
  - `focus_regras.py` — narrativa em linguagem simples + analogias.
  - `focus_apresentacao.py` — priorização, destaques e formatação da camada
    visual (sem Streamlit).
  - `pagina_focus.py` — composição da experiência e dos estados da página;
    `pages/1_Boletim_Focus.py` é apenas o entrypoint multipage.
  - `ui_estilos.py` — tokens e CSS responsivo/acessível compartilhável.
  - `noticias_data.py` — normalização, relevância, deduplicação e seleção
    diversificada das manchetes (sem I/O).
  - `noticias_feed.py` — adaptador RSS isolado para InfoMoney e Brazil
    Journal, com timeout, limite de resposta, allowlist e fallback por fonte.
- Guardrail de conteúdo: o motor de regras nunca recebe dados do usuário e
  nunca usa linguagem imperativa ("invista", "compre") — só descritiva/
  histórica. `tests/test_focus_regras.py` faz lint de vocabulário proibido.
- **Multi-máquina (trabalho + casa)**: mesma conta Claude, mas sem memória de
  conversa compartilhada entre sessões/máquinas — o git é a única fonte de
  verdade. Por isso: `CLAUDE.md` (instruções fixas, lido automaticamente por
  qualquer sessão Claude Code) + este `CONTEXT.md` (estado vivo) substituem a
  memória de chat. E `dados/focus_cache.json` **passou a ser versionado**
  (deixou de ser gitignored) — é só dado público do BACEN, sem nada
  sensível, e assim as duas máquinas acumulam o mesmo histórico em vez de
  cada uma ter o seu. `dados/focus_cache.example.json` foi removido (ficou
  redundante — o cache real agora é o próprio exemplo).

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

## Bloqueios

- Nenhum no momento.

## Próximos passos

- [ ] Página de carteira (organizar investimentos reais do usuário).
- [ ] Calculadora de projeção de rentabilidade (juros compostos, aportes).
- [ ] Deploy público (Streamlit Community Cloud) — avaliado e descartado por
      ora; reconsiderar se o uso semanal justificar acesso do celular.

## Conceitos relacionados

(nenhum ainda — projeto começou fora do vault Obsidian do hub da Fits)
