# Cobertura das fontes oficiais — módulo Ativos, Fase 0

Spike executado em 2026-10-09 contra os arquivos públicos baixados no mesmo dia. O
código do spike não foi versionado: é descartável e será substituído pelos adapters
da Fase 1. O dado bruto fica fora do repositório, em `%USERPROFILE%\.cache\lastro\raw`.

## Resumo

| Classe | Universo (ADTV) | Cobertura útil | Veredito |
|---|---|---|---|
| Ações | 193 tickers com volume médio ≥ R$ 1 mi/dia | 96% casam ticker→CNPJ; 93% têm P/L e P/VP calculáveis; 66% têm DY | **Viável** com 4 tratamentos obrigatórios (abaixo) |
| FIIs | 110 tickers com volume médio ≥ R$ 500 mil/dia | 85% casam por ISIN e têm P/VP e DY do mês | **Viável**; investigar os 15% sem ISIN casado |
| ETFs | 103 tickers com volume médio ≥ R$ 500 mil/dia | CVM traz CNPJ e PL; **não traz taxa nem índice** de forma utilizável | **Tabela curada** obrigatória |
| Preço ajustado | 8 de 193 ações líquidas com salto > 35% em 2026 | COTAHIST não ajusta eventos | **Ajuste próprio** de desdobramento/grupamento; retorno total fica em decisão |

## Fontes testadas

| Fonte | Arquivo | Uso |
|---|---|---|
| CVM DFP 2025 | `dfp_cia_aberta_2025.zip` | DRE, BP, DFC, DVA e composição do capital anuais; mediana de entrega 2026-03-18 |
| CVM ITR 2026 | `itr_cia_aberta_2026.zip` | 666 empresas no 1T26 e 667 no 2T26: base para TTM |
| CVM FCA 2026 | `fca_cia_aberta_valor_mobiliario_2026.csv` | **Ponte ticker → CNPJ** (`Codigo_Negociacao`) |
| CVM cadastro | `cad_cia_aberta.csv` | Setor (`SETOR_ATIV`) e situação |
| CVM informe mensal FII 2026 | `inf_mensal_fii_*_2026.csv` | ISIN, segmento, VP/cota, DY do mês, taxa de administração (% do PL), cotistas |
| CVM registro de fundos | `registro_fundo_classe.zip` | ETFs aparecem como "Classes de Cotas de Fundos FIIM" (256 classes), com CNPJ e PL |
| CVM extrato FI 2026 | `extrato_fi_2026.csv` | Tem `TAXA_ADM`, mas **não inclui os ETFs** |
| B3 COTAHIST 2026 | `COTAHIST_A2026.ZIP` (94 MB) | 193 pregões até 2026-10-08; preço, volume, ISIN, `CODBDI` (02 ações, 12 FII, 14 ETF) |

## Sanidade (preço de 2026-10-08, lucro e PL do DFP 2025)

| Ticker | P/L | P/VP | DY | Observação |
|---|---|---|---|---|
| ABEV3 | 15,8 | 2,84 | 4,3% | plausível após correção de escala |
| BBAS3 | 8,3 | 0,72 | 3,8% | plausível após mapear PL de banco |
| ITUB4 | 11,9 | 2,53 | 6,2% | plausível |
| PETR4 | 6,5 | 1,71 | 5,8% | plausível |
| WEGE3 | 32,1 | 11,7 | 1,8% | plausível |
| VALE3 | 24,4 | 1,53 | 0,0% | DY errado: rótulo da DVA diferente |
| TAEE11 | 29,9 | 6,20 | 2,4% | **errado**: unit tratada como ação |

| FII | P/VP | DY mês | Segmento declarado |
|---|---|---|---|
| HGLG11 | 0,94 | 0,70% | Multicategoria |
| KNRI11 | 1,00 | 0,67% | Multicategoria |
| XPML11 | 0,97 | 0,78% | Shoppings |
| MXRF11 | 1,01 | 1,01% | Logística (**autodeclarado e impreciso**: é FII de papel) |

## Armadilhas encontradas (viram requisito da Fase 1)

1. **Quantidade de ações em escala mista.** 94 de 373 empresas informam a composição
   do capital em milhar, não em unidade (exemplos: Ambev, Vale, Itaú). Sem correção, o
   P/L sai 1.000 vezes menor.
   - Regra do spike: se o VPA implícito passar de 50× o preço, a quantidade é
     multiplicada por 1.000.
   - A Fase 1 transforma isso em regra testada, com uma tabela de exceções.
2. **Plano de contas por tipo de empresa.** O PL de banco está em `2.07`. Em outras
   empresas o mesmo código é outra conta. O mapeamento é feito pela descrição da conta
   (`DS_CONTA`) e pelo tipo de demonstração, nunca só pelo código.
3. **Units e classes.**
   - Units (TAEE11, KLBN11, BPAC11) somam ON + PN numa só cota.
   - O valor de mercado precisa ser calculado por classe: o preço de cada classe vezes
     a sua quantidade.
   - A composição das units vem do FCA (`Composicao_BDR_Unit`).
4. **Proventos pela DVA.** O rótulo varia entre empresas (a Vale saiu com zero). Regex
   mais amplo e conferência contra o DFC (dividendos pagos).
5. **Ticker sem CNPJ no FCA.** Sete líquidos ficaram sem casar: BPAC11, CMIN3, CSNA3,
   KLBN3, KLBN4, MBRF3 e OBTC3. Causa provável: FCA de uma versão anterior ou listagem
   recente. Fallback: FCA de anos anteriores, depois uma tabela manual pequena.
6. **Point-in-time.** Toda leitura de balanço usa `DT_RECEB` (entrega à CVM), não
   `DT_REFER`. O DFP 2025 chegou, na mediana, 77 dias depois do fim do exercício.
7. **Segmento de FII é autodeclarado.** Para separar tijolo de papel, cruzar com a
   composição do ativo (`inf_mensal_fii_ativo_passivo`: CRI, LCI e imóveis).

## Decisões propostas

| Tema | Proposta | Situação |
|---|---|---|
| Ações e FIIs | CVM + COTAHIST, com os tratamentos acima | adotada |
| ETFs | Tabela curada `dados/ativos/etfs_curados.csv` (ticker, CNPJ, índice, exposição, taxa, fonte, data), cerca de 100 linhas revisadas a cada trimestre; PL e liquidez automáticos (CVM + COTAHIST) | adotada |
| Desdobramento e grupamento | Detectar salto de preço e confirmar pela variação da quantidade de ações no ITR seguinte; fator de ajuste aplicado à série | adotada |
| Retorno total (com proventos) para backtest | Opção A: aproximar pelo DY anual da DVA (oficial, menos preciso). Opção B: Yahoo/yfinance só para série ajustada (gratuito, não oficial) | **decisão do Raul** |
| Volume de dado | COTAHIST anual tem cerca de 90 MB. Bruto fora do git; tabelas derivadas em Parquet publicadas como asset de release | adotada |
