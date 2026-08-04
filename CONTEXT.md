# CONTEXT — Finanças Pessoais

- **Status**: v1.2 (multi-máquina) pronto — 2026-08-04
- **Repositório**: https://github.com/raulsallesr/financas-pessoais (privado)
- **Fonte oficial**: BACEN, Sistema de Expectativas de Mercado (Boletim
  Focus), API pública Olinda/OData
  (`https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata`),
  sem autenticação.
- **Periodicidade**: BACEN publica o Boletim Focus toda segunda-feira; a API
  tem granularidade diária, então o app permite atualizar a qualquer momento.

## Arquitetura

- Projeto pessoal, **sem relação com FitBank/Fits** — repositório próprio,
  separado do hub de tesouraria.
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
- Guardrail de conteúdo: o motor de regras nunca recebe dados do usuário e
  nunca usa linguagem imperativa ("invista", "compre") — só descritiva/
  histórica. `tests/test_focus_regras.py` faz lint de vocabulário proibido.
- Fluxo de código: Claude Code escreve direto (sem protocolo de brief/Codex
  do hub da Fits — aqui é só o Raul).
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

## Bloqueios

- Nenhum no momento.

## Próximos passos

- [ ] Página de carteira (organizar investimentos reais do usuário).
- [ ] Calculadora de projeção de rentabilidade (juros compostos, aportes).
- [ ] Deploy público (Streamlit Community Cloud) — avaliado e descartado por
      ora; reconsiderar se o uso semanal justificar acesso do celular.

## Conceitos relacionados

(nenhum ainda — projeto começou fora do vault Obsidian do hub da Fits)
