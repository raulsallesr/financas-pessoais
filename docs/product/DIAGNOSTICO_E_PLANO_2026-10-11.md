# Diagnóstico do Lastro e plano dos próximos ciclos (2026-10-11)

Avaliação honesta do estado do projeto logo depois do dia em que o módulo Ativos nasceu
(`210b1df`), com a ordem de trabalho que o Raul aprovou. Complementa
[`ROTEIRO_PROXIMAS_FASES.md`](ROTEIRO_PROXIMAS_FASES.md) (desenho técnico de cada corte) e
[`PLANO_LASTRO.md`](PLANO_LASTRO.md) (visão e princípios). Quando este plano e o roteiro
divergirem na **ordem**, vale este documento.

## Decisões do Raul (2026-10-11)

1. **Foco do próximo ciclo: confiança primeiro** (automação, qualidade de dados,
   calibração do valuation, vitrine), só depois novas telas.
2. **Retorno total: Yahoo Finance só para preço ajustado**, restrito a backtest e risco,
   isolado num adapter com cache e aviso de fonte não oficial. O app principal não pode
   depender dele. Antes de plugar, fazer o spike de comparação (item 2.4).
3. **Sem demonstração pública hospedada por ora** (evita exposição regulatória).

## 1. O que está bom

| Ponto | Evidência |
|---|---|
| Entrega rápida e verificável | 5 commits de produto em um dia; ~4,7 mil linhas em `ativos/`, 363 testes, cobertura 87,3% |
| Conferência contra a fonte | Cada revisão achou defeito real que testes sintéticos não pegavam (DY zerado pela DVA, P/Ativo Circ. Líq. 100% vazio, ações em milhar, ISIN duplicado, DY negativo do XPML11, rentabilidade de −28% do VISC11). Ver `docs/validation/LICOES_DADOS_PUBLICOS.md` |
| Princípios que seguram a qualidade | "Vazio é vazio", faixa e nunca número único, modelo inaplicável com motivo, guardrail de linguagem testado até nos literais da UI |
| Fontes oficiais e gratuitas | CVM Dados Abertos + COTAHIST; curva do Tesouro reaproveitada do módulo Macro |
| Base de backtest já existe | O pipeline é point-in-time: `selecionar_versoes` (`ativos/core/normalizacao.py`) filtra `DT_RECEB ≤ data de referência` e `scripts.atualizar_ativos` aceita `--data` |
| Continuidade comprovada | Guia de retomada, roteiro, lições, `CLAUDE.md` e `CONTEXT.md`; clone limpo reproduziu tudo (18 arquivos, 308 MB, tabelas idênticas) |
| Divisão de trabalho que funciona | Spec → Codex implementa → Claude reconcilia contra a fonte → commit |

## 2. O que está ruim ou frágil

### Críticos (afetam a confiança no que a tela mostra)

1. **Premissas do valor estimado incoerentes.** Bazin usa 6% fixo (`ativos/core/premissas.py`,
   `BAZIN_TAXA_PADRAO`) enquanto a taxa livre de risco é ~12,8% e o custo do capital próprio
   ~17,8%. Efeito: 101 de 215 ações "acima da faixa" e 90 de 155 FIIs "abaixo". Quase metade
   do mercado fora da faixa tira credibilidade, e **nada valida** o valuation contra
   desfechos reais.
2. **Modelos só de valor e renda.** Empresas de crescimento ficam bem abaixo do preço
   (WEGE3: faixa R$ 9–13 contra R$ 52). Há aviso na ficha (`modelos_valor_limitados`), mas
   falta o DCF.
3. **Dados sujos tratados caso a caso.** 27 FIIs com `dy_dados_suspeitos`, 20 FIIs
   pendentes, `qtd_em_milhar` por heurística em 71 ações, GFSA3 e MEAL3 sem múltiplos. Falta
   painel de qualidade e alerta de mudança de layout das fontes.

### Estruturais

4. **Atualização 100% manual**: os dados só existem no PC que rodou o pipeline.
5. **Sem histórico de indicadores**: só o instantâneo do dia.
6. **Retorno total** (decidido, ainda não medido) trava Score, backtest e carteira.
7. **Verificação visual fraca**: tabela em canvas (`st.dataframe`), navegador embutido
   instável em screenshots; FIIs e ficha validados por DOM e `AppTest`; README sem imagem do
   módulo novo.

### Processo e manutenção

8. **Manutenção do código novo** (medido em 2026-10-11): `ativos/core/pipeline_acoes.py` tem
   940 linhas em um módulo só; as duas páginas de busca somam ~900 linhas (481 + 417) com só
   133 de componente compartilhado (`componentes_tabela.py`); a suíte tem 7,9 mil linhas de
   teste contra 4,7 mil de código. ETFs seriam a terceira cópia.
9. **Conferência numérica manual e repetida** (carga sobre o Claude).
10. **Repositório com dois produtos e nome desalinhado**: Streamlit + app Expo dormente (APK
    expirou em 2026-09-16), repo `financas-pessoais` x plataforma Lastro (nome provisório),
    commits automáticos do Macro poluindo o histórico.
11. **Risco regulatório silencioso**: repo público mostra "faixas de valor". Há aviso em
    todas as telas; qualquer abertura a terceiros exige validação jurídica (CVM Res. 19 e
    20/2021).
12. **Fora do repo**: a remoção do card Finanças do SuperHub da Fits segue sem commit no hub.

## 2b. Auditoria de código (2026-10-11, leitura sem execução)

Feita por varredura (grep e leitura), não por revisão linha a linha. As duas alegações de
maior peso foram conferidas à mão.

**Bom:** nenhum `except Exception` nem `except:` em `ativos/` ou `scripts/` (os `except` são
estreitos); `ativos/core` não usa `st` nem `session_state` (a UI fica na camada de UI); todo
módulo de `core` tem teste correspondente; nenhum teste lê dado real do cache do usuário;
só grava em `~/.cache/lastro` e no repositório; sem segredos; sem `iterrows`.

**Achados (com evidência):**

| # | Achado | Onde | Gravidade |
|---|---|---|---|
| A1 | **Valuation recalculado a cada interação, sem cache** (confirmado). `st.cache_data` só cobre a leitura do Parquet e do JSON. Com 244 + 155 ativos não pesa; com 10× o universo o gargalo seria `_estatisticas_pares` | `pagina_busca.py:423`, `pagina_busca_fiis.py:341`, `pagina_ficha.py:278,284` | média |
| A2 | **Duplicação entre ações e FIIs**: janela e filtro de liquidez (63 pregões, 100 mil, 40 pregões) repetidos; "versão mais recente por data"; `divisao`/`divisao_segura` e `_numero` idênticos; par `carregar_*`/`carregar_meta_*`; `render` quase gêmeo; `_executar_acoes` e `_executar_fiis` quase gêmeos (85 e 82 linhas) | `pipeline_acoes.py:119-134` x `pipeline_fiis.py:75-87`; `metricas_acoes.py:72` x `metricas_fiis.py:63`; `scripts/atualizar_ativos.py:197,326` | média |
| A3 | **Funções longas**: `construir_tabela_fiis` (150 linhas, 19 ramos), `_fluxo_empresa` (98), `_capital_e_mercado` (82 linhas, 12 ramos, sem teste dedicado) | `pipeline_fiis.py:320`, `pipeline_acoes.py:330,765` | média |
| A4 | **Constantes mágicas** sem nome: 50, 40 e 1000 (escala de ações), 0,35 (salto de preço), 0,82 e 0,05, 0,80 (cobertura), 6 e 12 (meses mínimos), 0,04 (Gordon) | `normalizacao.py:136,148,149`, `pipeline_acoes.py:148,238,240`, `pipeline_fiis.py:285`, `metricas_fiis.py:145`, `valuation.py` | baixa (mas são decisões de método: merecem nome e doc) |
| A5 | `fillna(0)` só em ações em tesouraria (correto: ausente = zero ações) e em contagem de pares; falta comentário dizendo por quê | `pipeline_acoes.py:689,692`, `valuation.py:162` | baixa |
| A6 | Fallback da `rf` para 12% já é sinalizado (`rf_padrao`), mas não registra a causa em log | `premissas.py:85` | baixa |
| A7 | **Teste de ponta a ponta com fixture sintética só para FIIs** (golden em `test_pipeline_fiis.py:239`); ações não têm equivalente | `tests/` | média |
| A8 | Divisão `preco_unit / acoes_por_unit` sem guarda confirmada | `pipeline_acoes.py:811` | baixa (verificar) |

## 3. Plano

Ordem pelo caminho crítico: confiança → profundidade → inteligência.

### Ciclo 1 — Confiança e operação (próximo)

| # | Entrega | Detalhe | Gate |
|---|---|---|---|
| 1.1 | Calibrar o valuation | Bazin ligado à `rf` (ex.: `rf × fator`, editável) em vez de 6% fixo; revisar ERP e `g`; sanidade: distribuição de `situacao_faixa` entre 20% e 40% por lado, senão rever a premissa | distribuição documentada; golden tests atualizados |
| 1.2 | Painel de qualidade de dados | Cobertura por coluna, alertas por tipo, pendências, data de cada fonte; separar "corrigido" de "atenção" na ficha | UI testada; números batem com o metadado |
| 1.3 | Reconciliação automática | `scripts/reconciliar_referencias.py`: recalcula de forma independente lucro TTM, PL e DY de 6 tickers fixos direto do CSV e falha se divergir; roda no CI | teste e workflow verdes |
| 1.4 | Atualização automática | `.github/workflows/atualizar-ativos.yml` (dias úteis, `actions/cache` para o bruto), publica Parquet e metadados como assets da release fixa `dados-ativos`; o app baixa os assets se não achar derivados locais | execução manual verde; app abre em pasta vazia |
| 1.5 | Sentinela das fontes | Teste agendado contra as URLs reais (cabeçalhos dos CSV, layout do COTAHIST); abre issue se mudar | workflow semanal |
| 1.6 | Vitrine do repositório | Screenshots e GIF das telas, diagrama da arquitetura, README do módulo Ativos | revisão visual do Raul |
| 1.6b | Refatoração antes dos ETFs (achados A2, A3) | Extrair base comum dos pipelines (janela de liquidez, versão mais recente, divisão segura, número); quebrar `pipeline_acoes.py` em módulos e `construir_tabela_fiis`; unificar `_executar_acoes/_fiis`; extrair para `componentes_tabela.py` o que as buscas repetem (filtros, presets, premissas, comparador, carga) para ETFs entrarem como configuração | suíte inalterada verde; cobertura mantida; `pagina_busca*` abaixo de ~250 linhas |
| 1.6c | Endurecimento (A1, A4, A5, A6, A7, A8) | Cachear o valuation com as premissas como chave (`st.cache_data`); dar nome e documentação às constantes de método; comentar os `fillna(0)`; registrar em log a causa do fallback da `rf`; teste de ponta a ponta de ações com fixture sintética; testar `_capital_e_mercado` e conferir a guarda de `acoes_por_unit` | teste novo de pipeline de ações; sem `except` amplo; cobertura mantida |
| 1.7 | Limpezas | Card Finanças no SuperHub (aguarda o Raul); `.coverage` e `.pytest-*` fora do fluxo; nome definitivo da plataforma | — |

### Ciclo 2 — Profundidade

| # | Entrega | Detalhe |
|---|---|---|
| 2.1 | ETFs | Tabela curada (~100 linhas, cada taxa com fonte e data), exposição, ranking por custo/liquidez/PL |
| 2.2 | DCF de dois estágios (não financeiras) | FCFF da DFC, beta contra proxy, WACC pela curva do Macro, 5º modelo com grade WACC × g |
| 2.3 | Histórico de indicadores | Rodar o pipeline em datas passadas (`--data`) e guardar série trimestral; evolução de P/L, DY e margens na ficha |
| 2.4 | Spike do preço ajustado | Yahoo × COTAHIST+eventos em 20 tickers; adapter isolado com cache e aviso "não oficial" |

### Ciclo 3 — Inteligência

| # | Entrega | Dependência |
|---|---|---|
| 3.1 | Score Lastro | histórico (2.3) |
| 3.2 | Score Lab (backtest por quintil, IC de Spearman, anti look-ahead) | preço ajustado (2.4) e histórico |
| 3.3 | Risco e carteira (Sharpe vs CDI, mínima variância, Ledoit-Wolf, HRP, walk-forward) | preço ajustado (2.4) |
| 3.4 | Raio-x da carteira real (privado, nunca versionar) | 3.3 |

### Visão de produto

Um painel pessoal que une o macro ao micro: o cenário do Focus e a curva do Tesouro
alimentam a leitura de cada ativo. Só existem pela integração: sensibilidade setorial à
Selic e ao IPCA projetados; "ação vs Tesouro IPCA+"; renda passiva ligada ao Laboratório do
dinheiro; watchlist com proventos e fatos relevantes (CVM IPE); briefing semanal. Mobile
volta depois, com snapshot próprio `ativos-v1`.

## 4. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| CVM ou B3 mudam o layout | Sentinela (1.5) e reconciliação no CI (1.3) |
| Yahoo muda ou bloqueia | Adapter isolado e cache; só backtest e risco; o app principal não depende dele |
| Faixa lida como recomendação | Linguagem neutra testada, aviso fixo, premissas editáveis, sem demo pública |
| Dependência do Codex e do sandbox | Specs em `docs/product/`, método de reconciliação documentado, tudo reproduzível sem memória de chat |
| Excesso de teste dificulta mudança | Priorizar golden tests de fórmula e contrato; cortar teste de implementação na refatoração |

## 5. Como cada entrega é validada

`ruff check .`, `python -m pytest tests -q --cov=.` (piso 85%) e reconciliação de 5 tickers
contra o CSV da CVM (método em `docs/validation/LICOES_DADOS_PUBLICOS.md`). Depois do item
1.4, abrir o app numa máquina sem derivados e confirmar que baixa os assets. Atualizar
`CONTEXT.md` e `ROTEIRO_PROXIMAS_FASES.md` a cada ciclo; commit e push no git do projeto.
