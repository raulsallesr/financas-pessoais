# Lições dos dados públicos (CVM e B3)

Catálogo das armadilhas reais encontradas ao construir o módulo Ativos, com a decisão
tomada e onde ela vive no código. **Leia antes de mexer em adapters ou métricas.** Cada
item custou uma rodada de correção; a maior parte só apareceu ao conferir números contra
a fonte, não nos testes sintéticos. Datas: dados de 2026-10-08/09.

## Ações (DFP, ITR, FCA, COTAHIST)

| Armadilha | Decisão |
|---|---|
| **Quantidade de ações em milhar** em 94 de 373 empresas (Ambev, Vale, Itaú). Sem corrigir, o P/L sai 1.000× menor | Se `PL ÷ ações > 50 × preço`, multiplica por 1.000 e marca `qtd_em_milhar`. Sem padrão claro (GFSA3, MEAL3), marca `escala_suspeita` e **esvazia** valor de mercado e múltiplos |
| **Plano de contas de bancos** é outro (PL em `2.07`; lucro em `3.09`; DRE sem EBIT) | Mapeamento por código **e** descrição; financeiras só têm o conjunto reduzido de métricas |
| **ITR traz o acumulado do ano e o trimestre** nas mesmas colunas | TTM = DFP + acumulado do ano (`DT_INI_EXERC` = 1º/jan, `ÚLTIMO`) − mesmo acumulado do ano anterior (`PENÚLTIMO`) |
| **DVA subestima dividendos**: a Vale paga de reservas e a DVA vem zerada; LWSA3 e TECN3 saíam negativos | DY = dividendos e JCP **pagos** em 12 meses pela DFC (grupo `6.03`), excluindo linhas de "não controladores" e "recebidos". DVA só como fallback com alerta `dy_dva` |
| **Units** (TAEE11, KLBN11, ENGI11) somam ON + PN | Valor de mercado por empresa; unit sem preço de ON/PN deriva pelo número de ações por unit do FCA (`Composicao_BDR_Unit`), alerta `mcap_por_unit` |
| **Ticker sem CNPJ** no FCA do ano (BPAC, CSNA3, AMAR3) | Casa pelo nome em `cad_cia_aberta.csv` (normalizado), só se for inequívoco; 12 resolvidos assim, registrados no metadado |
| **COTAHIST não ajusta** desdobramento e grupamento (8 saltos > 35% em 2026) | Só o último preço e a liquidez entram; alerta `salto_preco` sinaliza risco |
| **Passivo Total (`2`) inclui o PL** | "Passivo exigível" = `2.01` + `2.02` (P/Ativo Circ. Líq. estava 100% vazio por isso) |
| **PL dos controladores** | `2.03` − `2.03.09` (não controladores) |

## FIIs (informe mensal e trimestral)

| Armadilha | Decisão |
|---|---|
| `Data_Referencia` mensal é o **1º dia do mês**; o último mês só tem poucos fundos; várias `Versao` por mês | Maior versão por (CNPJ, mês); último mês **por fundo**; `pl_defasado` se ficar >2 meses atrás do mês com ≥80% dos fundos |
| `Percentual_Dividend_Yield_Mes` é fração do **VP da cota**, não do preço | rendimento por cota = DY_mês × VP; `dy_12m` = soma ÷ preço atual |
| **Erros de preenchimento**: XPML11 com DY de −5,9% em 2026-01; VISC11 com rentabilidade de −28% em 2026-05 (VP estável) | DY mensal < 0 ou > 5% e rentabilidade fora de ±15% são descartados; DY anualiza pelos meses válidos (mín. 6); alerta `dy_dados_suspeitos`. Valores repetidos entre meses (XPML11, jun–ago) **não** são detectáveis com segurança |
| **Mesmo ISIN em dois CNPJs** (XPML11 × Peninsula; TRXF11 × Liquidez Projetos) | Desempate por nome de pregão (palavras em comum, vencedor único); empate ⇒ pendência |
| `Segmento_Atuacao` é autodeclarado (MXRF11 aparece como "Logística" e é de papel) | `tipo` calculado pela composição do ativo: Tijolo / Papel / Fundo de fundos / Híbrido / Outros (limiar 60%) |
| 16 fundos sem informe mensal correspondente | Ficam pendentes no metadado, sem inventar dado |

## Valor estimado

- Graham, Bazin, Gordon e múltiplos do setor medem **valor e renda atuais**. Empresas de
  crescimento ficam bem abaixo do preço (WEGE3: faixa R$ 9–13 contra R$ 52). Não é bug:
  a tela mostra aviso fixo e o sinal `modelos_valor_limitados` (P/L > 25 ou P/VP > 6).
  O DCF (ver roteiro) existe para tratar isso.
- Resultado agregado em 2026-10-09: 101 de 215 ações acima da faixa, 39 abaixo; FIIs: 90
  abaixo, 26 acima. Leia como retrato dos modelos com as premissas padrão, não como sinal.

## Armadilhas de ferramenta

- **Coluna `flags`** colide com `DataFrame.flags` do pandas: a coluna se chama `alertas`.
- **Testes de UI** com `AppTest` e `selectbox` com `format_func`: selecione pelo **valor**
  (`acao::WEGE3`, `fii::MXRF11`), não pelo rótulo.
- **Sandbox do Codex** é somente leitura sem `--sandbox workspace-write` e não grava em
  `%USERPROFILE%\.cache`; usa `LASTRO_DADOS_DIR` temporário. Rode o pipeline real fora dele.
- **Screenshots do navegador embutido** do Claude Code ficam instáveis (timeout); confirme
  UI também por DOM (`javascript_tool`) ou `AppTest`.
- **OneDrive**: venv e `node_modules` fora da pasta sincronizada.

## Método de reconciliação (use em toda mudança de métrica)

1. Rode o pipeline real e compare 5 tickers contra o CSV da CVM **calculado de forma
   independente** (script descartável, sem reutilizar o código do pipeline).
2. Verifique a distribuição: `min`, `1%`, `mediana`, `99%`, `max` de cada coluna; colunas
   100% vazias ou valores negativos onde não cabem são defeito.
3. Para cada fundo/ação grande com número estranho, abra a **série bruta** (os erros da
   CVM aparecem ali).
4. Confira que o aviso de alertas aparece na tela.

Valores de referência (DFP 2025 + ITR 2T26, cotação de 2026-10-08), úteis como teste de
regressão manual enquanto os dados não forem republicados:

| Ticker | Lucro TTM (controladores) | PL controladores | P/L | P/VP |
|---|---:|---:|---:|---:|
| PETR4 | R$ 133,376 bi | R$ 480,950 bi | 5,72 | 1,59 |
| VALE3 | R$ 10,369 bi | R$ 196,635 bi | 26,57 | 1,40 |
| ABEV3 | — | — | 15,36 | 2,83 |
| ITUB4 | — | — | 12,11 | 2,60 |
| HGLG11 | DY 12m 8,48% (R$ 13,19 de rendimentos ÷ R$ 155,50) | | | P/VP 0,94 |
