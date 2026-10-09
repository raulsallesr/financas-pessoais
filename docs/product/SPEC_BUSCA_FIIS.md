# Especificação — Busca avançada de FIIs (Lastro)

Segunda tela do módulo Ativos, no mesmo estilo da
[busca de ações](SPEC_BUSCA_AVANCADA_ACOES.md): uma linha por fundo, indicadores em
colunas, filtros, presets, comparador e CSV. **Leia a spec de ações primeiro**: as
restrições, a camada de download/cache, o guardrail de linguagem, o padrão de testes e o
pipeline valem aqui. Esta spec só define o que muda.

## Restrições adicionais

- Reaproveite o que existe; não duplique. Se for preciso, extraia de
  `ativos/ui/pagina_busca.py` um módulo compartilhado (`ativos/ui/componentes_tabela.py`)
  para tabela, formatação, exportação CSV e comparador, **sem quebrar os testes atuais**.
- Não altere `focuslens/` nem `mobile/`. Sem rede nos testes. Sem `git push`.
- Texto da tela passa por `ativos/core/linguagem.py`. Presets com nomes neutros.

## Dados brutos (já baixados, sem rede)

`%USERPROFILE%\.cache\lastro\raw\`:

| Arquivo | Uso |
|---|---|
| `inf_mensal_fii_2025.zip`, `inf_mensal_fii_2026.zip` | `geral`, `complemento`, `ativo_passivo` mensais |
| `inf_trimestral_fii_2025.zip`, `inf_trimestral_fii_2026.zip` | `imovel` (vacância, inadimplência, % do total investido) |
| `COTAHIST_A2025.ZIP`, `COTAHIST_A2026.ZIP` | preço e liquidez (reutilize `ativos/adapters/b3_cotahist.py`) |

Mesmo formato dos demais (`;`, `latin1`, `dtype=str`). Acrescente as funções de download
dos novos arquivos em `ativos/adapters/cvm.py` (mesmo padrão: atômico e idempotente,
testado com mock).

Fatos verificados nos dados reais:
- `Data_Referencia` do informe **mensal** é o **primeiro dia do mês** (2026-08-01 =
  agosto/2026). O mês mais recente costuma ter só alguns fundos; use, por fundo, o
  último mês disponível, mas marque `pl_defasado` se for mais de 2 meses mais antigo que
  o mês mais recente com ≥ 80% dos fundos.
- Cada (`CNPJ_Fundo_Classe`, mês) pode ter várias `Versao`: use a mais alta.
- `Percentual_Dividend_Yield_Mes` é fração do **valor patrimonial da cota** (HGLG11 em
  2026-08: 0,007027 × VP 165,95 ≈ R$ 1,166 por cota).
- Colunas do `complemento`: `Total_Numero_Cotistas`, `Patrimonio_Liquido`,
  `Cotas_Emitidas`, `Valor_Patrimonial_Cotas`, `Percentual_Despesas_Taxa_Administracao`,
  `Percentual_Rentabilidade_Efetiva_Mes`, `Percentual_Rentabilidade_Patrimonial_Mes`,
  `Percentual_Dividend_Yield_Mes`, `Percentual_Amortizacao_Cotas_Mes`.
- `ativo_passivo`: `Total_Investido`, `Direitos_Bens_Imoveis` (e `Imoveis_Renda_*`),
  `Acoes_Sociedades_Atividades_FII`, `Cotas_Sociedades_Atividades_FII`, `CRI`, `CRI_CRA`,
  `LCI`, `LCI_LCA`, `LIG`, `Letras_Hipotecarias`, `Cedulas_Debentures`, `Debentures`,
  `FII`, `Outras_Cotas_FI`, `Fundo_Acoes`, `FDIC`, `Titulos_Publicos`, `Titulos_Privados`,
  `Fundos_Renda_Fixa`, `Disponibilidades`, `Total_Passivo`.
- `geral`: `Codigo_ISIN`, `Nome_Fundo_Classe`, `Segmento_Atuacao` (autodeclarado e
  impreciso), `Tipo_Gestao`, `Mandato`, `Data_Funcionamento`, `Data_Entrega`.
- `imovel` (trimestral): `Percentual_Vacancia`, `Percentual_Inadimplencia`,
  `Percentual_Imovel_Total_Investido`, `Nome_Imovel`, `Classe`.

## Regras

1. **Universo:** tickers com `codbdi == "12"` no COTAHIST, `especi` começando por `CI`,
   liquidez média ≥ R$ 100 mil nos últimos 63 pregões (parametrizável, mesmo padrão das
   ações). Só entram os que casam com um fundo do informe mensal.
2. **Ticker → CNPJ:** pelo `Codigo_ISIN` do `geral` (use também os meses de 2025 para
   cobrir fundos sem ISIN no ano corrente). Quando o mesmo ISIN apontar para vários CNPJs,
   normalize `Nome_Fundo_Classe` e o nome de pregão (`nomres`) removendo acentos,
   pontuação, diferenças de caixa e as palavras genéricas `FII`, `FUNDO`, `DE`,
   `INVESTIMENTO`, `IMOBILIARIO`, `RESP`, `LTDA`, `RL`, `CLASSE` e `SA`. Escolha o
   candidato com mais palavras em comum somente quando houver um vencedor único, com ao
   menos uma palavra em comum e pontuação estritamente maior que a dos demais; use o
   informe mais recente desse candidato. Empate ou zero palavra em comum permanece
   pendente. Fallback: as posições 3–6 (0-based 2:6) do ISIN do COTAHIST são a raiz do
   ticker; case com a raiz do `Codigo_ISIN` do `geral` apenas quando for único. Sem
   casamento ⇒ pendência no metadado (não derruba o pipeline). O metadado registra os
   tickers resolvidos pelo desempate nominal e cada pendência com seu motivo.
3. **Fundo de classe:** use o registro da classe (`Tipo_Fundo_Classe`/`CNPJ_Fundo_Classe`).
4. **Tipo do fundo** (`tipo`), sobre `Total_Investido` do último `ativo_passivo`:
   `imoveis` = `Direitos_Bens_Imoveis` + `Acoes_Sociedades_Atividades_FII` +
   `Cotas_Sociedades_Atividades_FII`; `recebiveis` = `CRI` + `CRI_CRA` + `LCI` +
   `LCI_LCA` + `LIG` + `Letras_Hipotecarias` + `Cedulas_Debentures` + `Debentures`;
   `cotas_fundos` = `FII` + `Outras_Cotas_FI` + `Fundo_Acoes` + `FDIC`.
   Classifique: `Tijolo` se imóveis ≥ 60%; `Papel` se recebíveis ≥ 60%;
   `Fundo de fundos` se cotas_fundos ≥ 60%; `Híbrido` se (imóveis + recebíveis) ≥ 60% e
   nenhum sozinho chega a 60%; senão `Outros`. Guarde os três percentuais.
5. **DY 12 meses:** para cada mês M dos últimos 12 meses disponíveis do fundo
   (a partir do mês mais recente do próprio fundo), `rendimento_cota(M) =
   Percentual_Dividend_Yield_Mes(M) × Valor_Patrimonial_Cotas(M)`. `dy_12m =
   Σ rendimento_cota ÷ preço atual`. Um mês é inválido quando
   `Percentual_Dividend_Yield_Mes < 0` ou `> 0,05`; zero é válido. Exclua meses
   inválidos, anualize pelos meses válidos (`Σ × 12 ÷ n_validos`) e marque
   `dy_dados_suspeitos`; com menos de 6 meses válidos ⇒ `NaN`. Com menos de 12
   meses válidos, marque também `dy_parcial`.
6. **DY do último mês anualizado** (`dy_ultimo_mes`): `rendimento_cota(último mês) × 12 ÷
   preço`.
7. **Rentabilidade efetiva 12m** (`rentab_12m`): produto de `(1 + Percentual_Rentabilidade_
   Efetiva_Mes)` − 1 nos mesmos meses (vazio com menos de 12). Rentabilidade mensal
   fora de `[-0,5; 0,5]` invalida o cálculo (`NaN`) e marca `dy_dados_suspeitos`.
8. **Vacância e inadimplência:** do `imovel` trimestral mais recente por fundo, médias
   ponderadas por `Percentual_Imovel_Total_Investido` (se todos os pesos forem nulos,
   média simples). Só para fundos com imóveis; papel e fundo de fundos ficam `NaN`.
   `concentracao_top_imovel` = maior `Percentual_Imovel_Total_Investido`; `num_imoveis` =
   quantidade de imóveis distintos.
9. **Alavancagem:** `passivo_ativo` = `Total_Passivo` ÷ `Valor_Ativo` do último mês.
10. **Valor de mercado:** `preço × Cotas_Emitidas` do último mês.
11. **Vazio é vazio:** ausente/inaplicável é `NaN`, nunca `0`. Denominador ≤ 0 ⇒ `NaN`.
12. **Alertas** (coluna `alertas`, lista): `pl_defasado`, `dy_parcial`, `sem_cnpj`,
    `fundo_novo` (menos de 12 meses de informe), `p_vp_extremo` (P/VP < 0,3 ou > 3),
    `dy_dados_suspeitos` (DY mensal inválido ou rentabilidade mensal inválida na janela).

## Colunas

`ticker`, `nome`, `cnpj`, `segmento` (declarado), `tipo` (regra 4), `gestao`
(`Tipo_Gestao`), `preco`, `valor_mercado`, `liquidez_media_diaria`, `patrimonio_liquido`,
`cotas_emitidas`, `vp_cota`, `p_vp`, `dy_12m`, `dy_ultimo_mes`, `rendimento_ultimo_mes`
(R$ por cota), `rentab_12m`, `cotistas`, `taxa_adm` (fração do PL),
`pct_imoveis`, `pct_recebiveis`, `pct_cotas_fundos`, `vacancia`, `inadimplencia`,
`num_imoveis`, `concentracao_top_imovel`, `passivo_ativo`, `meses_informe`,
`data_informe` (mês de referência usado), `alertas`.

## Pipeline

Estenda `scripts/atualizar_ativos.py`: `--classe {acoes,fiis,todos}` (padrão `todos`).
Para FIIs grava `fiis.parquet` e `fiis_meta.json` (mesmo contrato do metadado das ações,
mais pendências de ticker, contagem por `tipo` e quantidade de fundos com
`dy_dados_suspeitos`). Imprime resumo (universo, cobertura de P/VP, DY 12m, vacância,
fundos com dados suspeitos e pendências). **Rode contra o cache real ao final.**

## Tela (`ativos/ui/pagina_busca_fiis.py`) e navegação

- Página "Busca de FIIs" (`url_path="busca-fiis"`) ao lado de "Busca avançada".
- Mesma estrutura da busca de ações: cartões de data/base/exibidos, filtros, grupos de
  colunas (Valuation, Renda, Qualidade da carteira, Liquidez e tamanho), tabela com
  ticker fixo e indicadores logo após, cadastro no fim, comparador e CSV.
- Filtros próprios: `tipo` (multiseleção), `segmento` (multiseleção), P/VP, DY 12m,
  vacância, liquidez mínima, ocultar fundos com alerta.
- Presets (módulo puro e testado, ex.: `ativos/core/presets_fiis.py`):
  - Renda com desconto: `p_vp` de 0,70 a 1,00, `dy_12m ≥ 8%`, liquidez ≥ R$ 500 mil;
  - Tijolo com baixa vacância: `tipo = Tijolo`, `vacancia ≤ 10%`, `p_vp` de 0,80 a 1,05;
  - Papel diversificado: `tipo = Papel`, `dy_12m ≥ 10%`, `passivo_ativo ≤ 15%`;
  - Alta liquidez: liquidez ≥ R$ 3 mi e `cotistas ≥ 50 000`.
- Dicionário `METRICAS_FII` (rótulo, grupo, formato, descrição) com tooltip de fórmula em
  cada coluna.

## Testes obrigatórios

- Golden por fórmula (DY 12m, DY do último mês, rentabilidade 12m, vacância ponderada,
  tipo por composição nos limites 60%, alavancagem, valor de mercado), números à mão.
- Versão mais alta por mês; último mês por fundo; `pl_defasado`; menos de 12 e menos de 6
  meses; ticker→CNPJ por ISIN e pelo fallback de raiz (inclusive caso ambíguo ⇒
  pendência).
- Fixtures sintéticas em memória; UI com `AppTest` e parquet sintético
  (`LASTRO_DADOS_DIR`); guardrail de linguagem em todos os textos; presets e filtros.
- Os testes das ações e do Macro continuam verdes.

## Fora de escopo

Prêmio sobre NTN-B, valor justo/avaliação, score, ETFs, workflow do GitHub, mobile.

## Ao terminar

Gate completo (ruff e suíte com cobertura ≥ 85%), atualize `CONTEXT.md`, **sem push**.
Devolva: o que foi feito, resultado do pipeline real (universo, cobertura, pendências,
contagem por tipo) e as decisões tomadas fora desta spec.
