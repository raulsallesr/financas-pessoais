# CONTEXT — Finanças Pessoais

- **Status**: v1 pronto e validado ponta a ponta — 2026-08-03
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
    `dados/focus_cache.json` (gitignored; `dados/focus_cache.example.json`
    versionado como exemplo).
  - `focus_regras.py` — narrativa em linguagem simples + analogias.
- Guardrail de conteúdo: o motor de regras nunca recebe dados do usuário e
  nunca usa linguagem imperativa ("invista", "compre") — só descritiva/
  histórica. `tests/test_focus_regras.py` faz lint de vocabulário proibido.
- Fluxo de código: Claude Code escreve direto (sem protocolo de brief/Codex
  do hub da Fits — aqui é só o Raul).

## Estado atual

- v1 implementado: Selic (próxima reunião do Copom), IPCA e câmbio (ano
  corrente), comparação semana-a-semana, narrativa e efeitos por classe de
  ativo.
- Endpoints e campos confirmados ao vivo em 2026-08-03 via curl:
  `ExpectativasMercadoSelic` (campo `Reuniao`, ex. `"R5/2026"`) e
  `ExpectativasMercadoAnuais` (campo `DataReferencia`, ex. `"2026"`);
  `baseCalculo=0` = todos os respondentes (o número usado no Boletim Focus
  oficial).
- 30 testes pytest passando; app testado ao vivo no navegador (Selic 14,00%,
  IPCA 5,03%, Câmbio R$5,20 em 2026-08-03 — bate com o print manual que já
  existia no deck antigo do hub da Fits).
- **Bug encontrado e corrigido na validação**: a API da BACEN (Olinda) não
  decodifica corretamente o `+` que a biblioteca `requests` usa por padrão
  para espaços em query params — devolve 400 ("types not compatible") mesmo
  em filtros OData válidos. `focus_leitura._get()` agora monta a query string
  manualmente com `urllib.parse.quote` (força `%20`).

## Bloqueios

- Nenhum no momento.

## Próximos passos

- [ ] Rodar `git add` + primeiro commit (feito localmente, mas o commit em si
      fica a critério do Raul).
- [ ] v2: mais indicadores (PIB, IGP-M), gráfico de série histórica.
- [ ] Página de carteira (organizar investimentos reais do usuário).
- [ ] Calculadora de projeção de rentabilidade (juros compostos, aportes).

## Conceitos relacionados

(nenhum ainda — projeto começou fora do vault Obsidian do hub da Fits)
