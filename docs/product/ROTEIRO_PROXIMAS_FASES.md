# Roteiro das próximas fases (Lastro / Ativos B3)

Complementa [`PLANO_LASTRO.md`](PLANO_LASTRO.md) com o **desenho já pensado** de cada
corte que falta, para retomar sem refazer decisões. Cada item termina com os gates e o
que ainda depende do Raul. Método de trabalho de cada corte: escrever
`docs/product/SPEC_<corte>.md` → Codex implementa → Claude reconcilia contra a fonte
(ver [`LICOES_DADOS_PUBLICOS.md`](../validation/LICOES_DADOS_PUBLICOS.md)) → commit.

Estado em 2026-10-09: concluídos Fase 0, base de dados, busca de ações, busca de FIIs,
valor estimado (sem DCF) e ficha do ativo. Veja os specs `SPEC_BUSCA_AVANCADA_ACOES.md`,
`SPEC_BUSCA_FIIS.md` e `SPEC_VALOR_ESTIMADO.md` como modelo de especificação.

> **Atualização 2026-10-11:** a ordem abaixo foi revista. Vale
> [`DIAGNOSTICO_E_PLANO_2026-10-11.md`](DIAGNOSTICO_E_PLANO_2026-10-11.md): primeiro o Ciclo 1
> (confiança: calibrar valuation, qualidade de dados, reconciliação, automação, refatoração),
> depois ETFs, DCF, histórico e preço ajustado, e só então Score, risco e carteira. A decisão
> sobre retorno total está tomada: Yahoo só para preço (ver seção D).

## Ordem sugerida

1. **Atualização automática** (pequeno, destrava o uso diário).
2. **ETFs** (pedido original do Raul: "melhores ETFs pelo que investem e quanto cobram").
3. **DCF** (fecha a lacuna do valor estimado para empresas de crescimento).
4. **Score Lastro + Score Lab** (o "rating da plataforma").
5. **Risco e carteira** (pulverizada com bom risco × retorno).
6. Extras.

## A. Atualização automática dos derivados

- **Problema:** hoje o Raul roda `scripts.baixar_dados_ativos` e `scripts.atualizar_ativos`
  à mão em cada máquina; o app nem existe fora do PC dele.
- **Desenho:** workflow `.github/workflows/atualizar-ativos.yml` (dias úteis, depois do
  fechamento): `actions/cache` para o cache bruto (anos encerrados não mudam; só o corrente
  baixa), roda os dois scripts, publica `acoes.parquet`, `fiis.parquet` e os `*_meta.json`
  como **assets de uma release fixa `dados-ativos`** (sobrescrita a cada rodada). O app, se
  não achar derivados locais, baixa os assets da release (`requests`, sem token por ser
  repositório público). Nunca commitar Parquet no histórico.
- **Cuidados:** o workflow existente `atualizar-curva.yml` commita `dados/curva_*`; evitar
  corrida de commits (job separado, sem commit). Teste com cliente HTTP simulado.
- **Gate:** workflow verde em execução manual; app abre numa pasta de derivados vazia e se
  recupera; testes do downloader de assets.

## B. ETFs por exposição, custo e liquidez

- **Universo:** `codbdi == "14"` no COTAHIST (264 papéis, 103 com liquidez ≥ R$ 500 mil em
  2026-10). Exemplos: BOVA11, SMAL11, IVVB11, DIVO11, GOLD11, NASD11, HASH11.
- **O que a CVM dá e o que não dá:** `registro_classe.csv` traz CNPJ, PL e situação dos ETFs
  (aparecem como "Classes de Cotas de Fundos FIIM" — não confunda com FII); `extrato_fi`
  **não** inclui ETFs, então **taxa de administração e índice de referência não vêm de
  fonte oficial estruturada**.
- **Decisão já tomada:** tabela **curada** `dados/ativos/etfs_curados.csv` (≈100 linhas):
  `ticker, cnpj, nome, indice, exposicao, moeda, taxa_adm, fonte, data_revisao`. **Nenhum
  valor entra sem fonte e data** (site da gestora/B3/lâmina). Exposições: ações Brasil amplo,
  dividendos, small caps, setoriais, internacional (EUA etc.), renda fixa (pré, IPCA, CDI),
  ouro/commodities, cripto, imobiliário. PL e liquidez são automáticos (CVM + COTAHIST).
- **Ranking dentro de cada exposição:** custo (taxa), liquidez (ADTV 63 pregões), PL, e
  tracking difference **apenas quando houver série do índice** (provavelmente fica para
  depois). Cuidado com ETFs sem histórico suficiente.
- **Tela:** `Busca de ETFs`, mesmo molde das buscas (componentes em
  `ativos/ui/componentes_tabela.py`), filtros por exposição, taxa máxima, liquidez; preset
  "mais barato por exposição" (linguagem neutra: "menor taxa").
- **Pesquisa web necessária:** quem curar a tabela precisa de acesso à internet para
  confirmar taxas (o Claude Code em casa tem WebSearch/WebFetch).
- **Gate:** conferência manual de 10 ETFs conhecidos contra a lâmina; testes golden do
  ranking; guardrail de linguagem.

## C. DCF de dois estágios (só não financeiras)

- **Insumos novos no pipeline:** fluxo de caixa operacional (DFC `6.01`) e investimentos
  em imobilizado/intangível (`6.02.*`, "aquisição"), TTM como as demais; FCFF = CFO −
  capex (+ juros líquidos após IR se partir do CFO do método indireto; documentar).
- **Beta:** do COTAHIST contra um proxy do mercado (BOVA11, ou cesta ponderada das ações
  líquidas), 3 a 5 anos, com o aviso de que é aproximação (o COTAHIST não tem o índice).
- **WACC:** `Ke = rf + beta × ERP` (rf da curva do Macro, ERP editável); `Kd` = despesa
  financeira ÷ dívida bruta × (1 − 34%); pesos por valor de mercado e dívida.
- **Projeção:** 5 anos com crescimento inicial = CAGR de receita limitado por teto e
  convergindo linearmente para `g` terminal (≤ crescimento nominal do PIB); valor terminal
  Gordon; `valor por ação = (EV − dívida líquida − minoritários) ÷ ações`.
- **Saídas:** entra como 5º modelo na faixa (`modelo_dcf`), grade de sensibilidade WACC × g,
  e **"não se aplica"** com motivo para FCF negativo, financeiras e dados insuficientes.
- **Gate:** golden test à mão (fluxos fixos), sensibilidade, caso FCF negativo, fixtures
  sintéticas; reconciliar PETR4/WEGE3/VALE3 contra a DFC.

## D. Score Lastro e Score Lab (o "rating")

- **Seis fatores:** Valor, Qualidade, Saúde financeira, Crescimento, Dividendos, Risco.
- **Construção:** cada métrica vira **percentil dentro do setor** (winsorizado 5/95;
  invertido onde menor é melhor), fator = média das métricas disponíveis. Nota 0–100 e
  letra A–E por quintil. Pesos editáveis com perfis prontos (Equilibrado, Qualidade,
  Valor, Dividendos). Cobertura de dados < 70% ⇒ "não avaliado". Liquidez mínima.
- **Transparência:** toda nota mostra a **decomposição** (quanto cada fator puxou) e a
  fórmula; financeiras com subconjunto próprio de métricas.
- **Score Lab:** backtest point-in-time do score: a cada rebalanceamento trimestral monta
  quintis só com balanços entregues até a data (`DT_RECEB`), mede retorno em 12 meses por
  quintil e o **IC de Spearman**. É onde a fórmula se calibra antes de qualquer confiança.
- **Dependência crítica (decisão do Raul):** retorno total ajustado de desdobramento e
  dividendos. Opção A: aproximar só com dados oficiais (DY da DFC/DVA + ajuste por eventos
  de capital), menos preciso. Opção B (ESCOLHIDA em 2026-10-11): Yahoo Finance (gratuito, não oficial) apenas para
  preço ajustado. **Sem esta decisão o Score Lab não começa.** Também precisa dos
  COTAHIST de 2020 em diante e de fundamentos históricos (DFP/ITR 2020+, já baixados).
- **Gate:** teste dedicado **anti look-ahead**; golden da decomposição; monotonicidade
  quando se melhora uma métrica; não avaliado abaixo de 70%.

## E. Risco e carteira pulverizada

- **Métricas:** volatilidade, beta, drawdown máximo, Sharpe e Sortino contra o CDI (série
  SGS já acessível em `focuslens/adapters/mercado_fontes.py`), correlação média, razão de
  diversificação, HHI.
- **Otimizadores (implementar nós mesmos, sem caixa-preta):** pesos iguais (baseline),
  mínima variância, média-variância com covariância **Ledoit-Wolf**, **HRP** (o mais robusto
  para carteira pulverizada). Restrições: máximo por ativo/setor/classe, número mínimo de
  ativos. Dependências novas aceitas: `scipy`.
- **Saídas:** fronteira eficiente e **backtest walk-forward** (rebalanceamento trimestral,
  custos). Sempre rotulado como simulação para estudo, nunca como carteira recomendada.
- **Raio-x da carteira real:** estender `focuslens/adapters/b3_importacao.py` de forma
  retrocompatível para guardar ticker e quantidade (hoje só `ativo, classe, valor_atual`);
  mostra concentração, correlação, score médio, exposição setorial e sobreposição de ETFs.
  A carteira real **nunca** sai do aparelho: não versionar, não enviar a rede, não usar
  dados pessoais em testes.
- **Gate:** pesos somam 1, restrições respeitadas, HRP determinístico, sem look-ahead.

## F. Ideias extras

Watchlist com alertas de fato relevante e calendário de proventos (CVM IPE); simulador de
renda passiva ligado ao Laboratório do dinheiro; "ação vs. Tesouro IPCA+" (earnings yield
menos NTN-B real); sensibilidade setorial ao cenário do Focus (Selic/IPCA); painel de
qualidade e cobertura dos dados; diário de tese e checklist pessoal por ativo; app mobile
consumindo um snapshot `ativos-v1` (o snapshot `v1` do FocusLens não muda).

## Qualidade pendente (pequena)

- SANB11 sem DY; 20 FIIs sem casamento de ticker (16 sem informe mensal); GFSA3 e MEAL3 com
  `escala_suspeita`; repetição de valores mensais da CVM (XPML11) não detectável.
- O rótulo "Alertas de dados" da ficha também lista correções já aplicadas (`qtd_em_milhar`);
  separar "corrigido" de "atenção".
- A conferência visual completa (screenshot) das telas de FIIs e da ficha foi parcial:
  validadas por DOM e `AppTest`. Vale uma olhada humana de cada página.
- Paridade de tema e acessibilidade da tabela (`st.dataframe` é canvas) não foi auditada.

## Decisões abertas do Raul

1. ~~Retorno total para o backtest~~ **Decidido em 2026-10-11: opção B, Yahoo só para preço**
   (adapter isolado, cache, aviso de fonte não oficial; spike de comparação antes de plugar).
2. Nome definitivo da plataforma ("Lastro" é provisório).
3. Abrir a plataforma para outras pessoas? Isso exige validação jurídica/compliance
   (CVM Res. 19 e 20/2021, analista e consultor); enquanto for pessoal, vale o aviso de uso
   próprio já presente em todas as telas.
