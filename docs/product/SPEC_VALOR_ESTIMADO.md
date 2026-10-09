# Especificação — Valor estimado e ficha do ativo (Lastro)

Responde à pergunta "quanto o ativo valeria vs. quanto está valendo", sempre como
**faixa entre modelos**, com premissas visíveis e editáveis. Preenche a coluna
"Avaliação" da referência do Raul nas duas buscas e cria a página "Ficha do ativo".
Base: [`PLANO_LASTRO.md`](PLANO_LASTRO.md), [`SPEC_BUSCA_AVANCADA_ACOES.md`](SPEC_BUSCA_AVANCADA_ACOES.md),
[`SPEC_BUSCA_FIIS.md`](SPEC_BUSCA_FIIS.md). Valem as mesmas restrições (sem rede nos testes,
sem `git push`, `focuslens/` e `mobile/` intocados, ruff e cobertura ≥ 85%).

## Princípios (não negociáveis)

1. **Faixa, nunca número único.** O "valor central" é a mediana dos modelos aplicáveis; a
   tela sempre mostra a faixa e quantos modelos a compõem.
2. **Modelo inaplicável aparece como "não se aplica" com o motivo**, jamais um valor
   inventado. Menos de 2 modelos aplicáveis ⇒ sem faixa ("dados insuficientes").
3. **Premissas visíveis e editáveis** na própria tela, com padrão documentado e botão
   "restaurar padrão". Nada de caixa-preta.
4. **Linguagem neutra.** Posição relativa à faixa: "abaixo da faixa", "dentro da faixa",
   "acima da faixa". Proibido nos textos: "barato", "caro", "oportunidade", "compre",
   "venda", "recomendo", "preço-alvo". Acrescente `barat[oa]`, `car[oa]` (palavra inteira)
   e `oportunidade` ao guardrail `ativos/core/linguagem.py` e cubra com testes.
5. Cálculo é **puro** (`ativos/core/valuation.py`), vetorizado sobre o DataFrame, e roda na
   hora na tela com as premissas escolhidas. O parquet guarda só os insumos.

## Insumos novos no pipeline

Em `ativos/core/pipeline_acoes.py` e `pipeline_fiis.py` (e metadado/versão do esquema):
- Ações: `dpa` = proventos pagos em 12 meses (DFC, a mesma base do `dy`) ÷ ações da
  empresa. Vazio se não houver provento.
- FIIs: `rendimento_12m_cota` = soma dos rendimentos por cota dos meses válidos usados no
  `dy_12m` (já anualizada como o `dy_12m`).
Teste golden para ambos.

## Taxa livre de risco (reuso do Macro)

`ativos/core/premissas.py`:
- `taxa_livre_de_risco(pontos, anos_alvo=5)`: com a curva do Tesouro Prefixado do cache
  do Macro (`focuslens.adapters.curva_fontes.carregar_cache()`, que **não usa rede**),
  pega a data mais recente e interpola linearmente a taxa para 5 anos de prazo; fora do
  alcance dos vértices usa o vértice mais próximo. Taxa em fração (12,82% = 0,1282).
  Falha de leitura do cache ⇒ fallback 12,0% e marcação `rf_padrao`.
- `PremissasValuation` (dataclass imutável) com padrões:

| Premissa | Padrão | Observação |
|---|---|---|
| `rf` | da curva (≈ 12,8%) | exibir fonte e data da curva |
| `erp` (prêmio de risco de ações) | 5,0% | |
| `k` (custo do capital próprio) | `rf + erp` | derivado |
| `g` (crescimento perpétuo nominal) | 4,0% | |
| `bazin_taxa` | 6,0% | taxa mínima clássica do método Bazin |
| `graham_mult` | 22,5 | |
| `fii_taxa_exigida` | `rf × (1 − 0,15)` | FII é isento de IR para pessoa física; equivale ao Tesouro líquido de 15% |
| `min_pares_setor` | 6 | |

## Modelos de ações (valor por ação, em R$)

| Modelo | Fórmula | Não se aplica quando |
|---|---|---|
| Graham | `√(graham_mult × LPA × VPA)` | LPA ≤ 0 ou VPA ≤ 0 |
| Bazin | `DPA ÷ bazin_taxa` | DPA vazio ou ≤ 0 |
| Gordon | `DPA × (1 + g) ÷ (k − g)` | DPA ≤ 0 ou `k − g < 0,04` |
| Múltiplos do setor | média dos disponíveis entre `LPA × mediana(P/L do setor)` e `VPA × mediana(P/VP do setor)` | setor com menos de `min_pares_setor` empresas distintas (por CNPJ) com o múltiplo válido; LPA/VPA ≤ 0 para a respectiva parcela |

Mediana do setor: sobre empresas distintas (uma linha por CNPJ), excluindo o próprio ativo,
considerando só múltiplos positivos. Financeiras comparam apenas com financeiras.
**DCF fica fora desta fase** (exige fluxo de caixa da DFC e beta); registre no plano como
próxima evolução.

## Modelos de FIIs (valor por cota, em R$)

| Modelo | Fórmula | Não se aplica quando |
|---|---|---|
| Patrimonial | `vp_cota` | vazio ou ≤ 0 |
| Renda capitalizada | `rendimento_12m_cota ÷ fii_taxa_exigida` | rendimento vazio ou ≤ 0 |

## Faixa e posição

- `faixa_baixa` = percentil 25, `faixa_alta` = percentil 75 (interpolação linear) e
  `valor_central` = mediana dos valores aplicáveis. Com exatamente 2 modelos os percentis
  interpolam entre eles (ok).
- `n_modelos` = quantidade de modelos aplicáveis. `< 2` ⇒ faixa, central e margem `NaN`.
- `margem_seguranca` = `valor_central ÷ preço − 1` (positiva = preço abaixo do valor
  central).
- `situacao_faixa`: `abaixo da faixa` se `preço < faixa_baixa`; `acima da faixa` se
  `preço > faixa_alta`; senão `dentro da faixa`; vazio se sem faixa.
- Alerta `valuation_fragil` se `n_modelos == 2` e a razão alta/baixa passar de 3, ou se
  o ativo tem qualquer alerta de dados do pipeline (`dy_dados_suspeitos`, `escala_suspeita`,
  `salto_preco`, `pl_defasado`).

## Telas

1. **Coluna "Avaliação" nas duas buscas** (ações e FIIs): novo grupo de colunas
   "Avaliação" com `valor_central`, `faixa_baixa`, `faixa_alta`, `margem_seguranca`,
   `n_modelos`, `situacao_faixa`, visível por padrão, logo após o preço. Filtro mínimo de
   margem de segurança e um preset por tela: "Margem calculada ≥ 30% com 3+ modelos"
   (ações) e "Abaixo da faixa patrimonial e de renda" (FIIs: `situacao_faixa` = abaixo).
   Tooltip de cada coluna explica a fórmula. Painel **Premissas** (expander) nas duas
   telas, com os valores da tabela acima, reset e a linha "Curva de referência: Tesouro
   Prefixado em AAAA-MM-DD".
2. **Página "Ficha do ativo"** (`ativos/ui/pagina_ficha.py`, `url_path="ficha"`),
   ao lado das buscas. Seleção de ticker (ações e FIIs numa lista só, com rótulo da
   classe). Conteúdo:
   - cabeçalho: nome, setor ou tipo, preço, data da cotação, alertas de dados;
   - **faixa de valor**: gráfico horizontal (altair, já incluído no Streamlit) com a
     faixa baixa–alta, o valor central e uma marca do preço atual, mais `margem_seguranca`
     e `situacao_faixa` em texto;
   - **tabela dos modelos**: modelo, valor, fórmula em texto, premissas usadas e status
     ("não se aplica: LPA negativo");
   - **sensibilidade**: grade de Gordon (k × g) e Bazin (taxa mínima), valor por ação em
     cada célula (use `st.dataframe` com formatação);
   - **indicadores-chave versus o setor**: valor do ativo, mediana do setor e percentil
     para P/L, P/VP, DY, ROE, margem líquida e dívida líquida/EBIT (ações) ou P/VP, DY 12m,
     vacância, cotistas (FIIs);
   - as premissas editáveis do painel valem aqui também (compartilhe o estado).
3. A página "Ativos B3" (visão geral) atualiza o quadro de fases: valor estimado e ficha
   concluídos; DCF, score, ETFs e atualização automática como próximos.

## Testes obrigatórios

- Golden à mão: Graham (LPA 2, VPA 10) = 21,2132; Bazin (DPA 0,60 e 6%) = 10,00;
  Gordon (DPA 1,00, g 4%, k 17,8%) = 7,5362; múltiplos do setor (setor sintético com
  medianas conhecidas, parcelas e média); renda capitalizada de FII; percentis da faixa
  com 2, 3 e 4 modelos; margem e `situacao_faixa` nos três casos.
- Casos "não se aplica" de cada modelo e menos de 2 modelos ⇒ sem faixa; `k − g < 4 pp`.
- `taxa_livre_de_risco`: interpolação a 5 anos, extrapolação nas pontas, fallback.
- Setor com poucos pares; exclusão do próprio ativo da mediana; uma linha por CNPJ.
- Recalcular com premissas diferentes muda o valor e restaurar volta ao padrão.
- UI com `AppTest` (buscas com a nova coluna e preset, ficha com ticker de ação e de
  FII, ficha de ativo sem faixa) e guardrail de linguagem em todos os textos novos.
- Testes das ações, FIIs e Macro continuam verdes.

## Ao terminar

Gate completo, rode os pipelines reais (`--classe todos`), atualize `CONTEXT.md` e
`docs/product/PLANO_LASTRO.md` (fase 4 parcial: sem DCF), **sem push**. Devolva: o que foi
feito, a distribuição real de `situacao_faixa` e `n_modelos` para ações e FIIs, a faixa de
PETR4, VALE3, ITUB4, WEGE3, ABEV3 e HGLG11, KNRI11, MXRF11, e as decisões tomadas fora
desta spec.
