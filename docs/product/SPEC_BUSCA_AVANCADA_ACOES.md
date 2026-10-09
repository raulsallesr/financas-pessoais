# Especificação — Busca avançada de ações (Lastro, fatia vertical)

Primeira entrega visível do módulo Ativos: uma tabela larga, uma linha por ticker, com
dezenas de indicadores calculados a partir de fontes oficiais, ordenável e filtrável.
Contexto: [`PLANO_LASTRO.md`](PLANO_LASTRO.md) e
[`COBERTURA_ATIVOS_FASE0.md`](../validation/COBERTURA_ATIVOS_FASE0.md) (leia este antes: lista as
armadilhas dos dados).

## Restrições

- Mesmo padrão do projeto: `ativos/adapters` (I/O), `ativos/core` (puro, sem I/O),
  `ativos/ui` (Streamlit). Não alterar `focuslens/` nem `mobile/`.
- **Testes sem rede.** Use fixtures sintéticas geradas em memória (ZIP/CSV/linha de
  largura fixa). Nunca versione dado real da CVM ou da B3.
- Todo texto exibido passa por `ativos/core/linguagem.py` (sem ordem de compra/venda,
  sem preço-alvo). Rótulos neutros.
- `ruff check .` limpo; `python -m pytest tests/ --cov=.` verde com cobertura ≥ 85%.
- Git: só o repositório do projeto, **sem `git push`** (o Claude revisa e publica).
- Dependências permitidas: `pandas`, `numpy`, `pyarrow` (já instalado no venv),
  `requests`, `streamlit`. Acrescente `numpy` e `pyarrow` a `requirements.txt`.
- Python do projeto: `C:\Users\raul.rolim\.venvs\financas-pessoais\Scripts\python.exe`.

## Dados brutos já baixados (cache local, sem rede)

Pasta `%USERPROFILE%\.cache\lastro\raw\` (sobrescrevível por `LASTRO_CACHE_DIR`):

| Arquivo | Conteúdo |
|---|---|
| `dfp_cia_aberta_{2020..2025}.zip` | DFP: DRE/BPA/BPP/DFC/DVA consolidado e individual + `composicao_capital` |
| `itr_cia_aberta_{2025,2026}.zip` | ITR: mesmos relatórios, trimestrais |
| `fca_cia_aberta_{2025,2026}.zip` | `fca_cia_aberta_valor_mobiliario_*.csv`: ticker ↔ CNPJ |
| `cad_cia_aberta.csv` | setor (`SETOR_ATIV`) e situação |
| `COTAHIST_A{2025,2026}.ZIP` | cotações diárias da B3 |

Todos os CSVs: `;` como separador, `latin1`, valores como texto (`dtype=str`).
Adapters também precisam de função de **download** (requests, gravação atômica,
idempotente: ano fechado nunca rebaixa; ano corrente rebaixa se > 1 dia) — testada com
mock, não executada nos testes.

## Camada de dados (`ativos/adapters`)

- `paths.py` em `ativos/`: raiz do cache (bruto) e pasta de derivados
  (`%USERPROFILE%\.cache\lastro\derived\`, sobrescrevível por `LASTRO_DADOS_DIR`).
- `cvm.py`: leitura de DFP/ITR por relatório (`DRE`, `BPA`, `BPP`, `DFC_MI`, `DFC_MD`, `DVA`,
  `composicao_capital`, cabeçalho com `DT_RECEB`), FCA e cadastro.
- `b3_cotahist.py`: layout posicional (0-based, fim exclusivo):
  `tipreg 0:2`, `data 2:10` (AAAAMMDD), `codbdi 10:12`, `ticker 12:24`, `tpmerc 24:27`,
  `nomres 27:39`, `especi 39:49`, `preult 108:121`, `totneg 147:152`, `voltot 170:188`,
  `fatcot 210:217`, `isin 230:242`. Registros `tipreg == "01"` e `tpmerc == "010"`.
  `preço = preult / 100 / fatcot`; `volume = voltot / 100`.

## Regras de normalização (`ativos/core`)

1. **Escala monetária:** `ESCALA_MOEDA == "MIL"` ⇒ valor × 1000.
2. **Versão:** por (`CNPJ_CIA`, `DT_REFER`) usar a `VERSAO` mais alta. Point-in-time:
   só entram documentos com `DT_RECEB ≤` data de referência da base.
3. **Consolidado primeiro:** usar demonstração consolidada (`_con`); se a empresa não
   tem, usar individual (`_ind`).
4. **Contas pela descrição + código** (nunca só pelo código):
   - DRE: receita `3.01`; resultado bruto `3.03`; EBIT `3.05` ("Resultado Antes do
     Resultado Financeiro e dos Tributos"); lucro atribuível aos controladores `3.11.01`
     (se ausente, `3.11`).
   - BPA: ativo total `1`; ativo circulante `1.01`; caixa `1.01.01`; aplicações
     financeiras `1.01.02`.
   - BPP: passivo total `2`; passivo circulante `2.01`; passivo não circulante `2.02`;
     passivo exigível = `2.01 + 2.02`; empréstimos curto prazo
     `2.01.04`; empréstimos longo prazo `2.02.01`; PL consolidado `2.03`; participação
     de não controladores `2.03.09`. **PL dos controladores = `2.03` − `2.03.09`** (se
     `2.03.09` não existe, `2.03`).
   - DFC: dividendos e JCP pagos são linhas do grupo `6.03` cuja descrição contém
     "dividend", ou "juros sobre" + "capital", ou "JCP". Excluir descrições com
     "não controlador", "recebid" ou "receb". Somar os valores em módulo.
     Prioridade: `DFC_MI_con`, `DFC_MD_con`, `DFC_MI_ind`, `DFC_MD_ind`.
   - DVA: somente fallback quando a DFC não traz linha; proventos = `7.08.04.01` (JCP)
     + `7.08.04.02` (Dividendos), do último DFP, com alerta `dy_dva`.
5. **TTM (12 meses) para fluxos** (receita, resultado bruto, EBIT, lucro e pagamentos
   da DFC):
   `DFP do último exercício + acumulado do ano corrente − acumulado do mesmo período do
   ano anterior`. No ITR, o acumulado é a linha com `DT_INI_EXERC` = 1º de janeiro: a
   `ÚLTIMO` é o ano corrente e a `PENÚLTIMO` é o ano anterior. Sem ITR posterior ao DFP,
   TTM = DFP. Proventos TTM negativos ou sem fonte ficam `NaN`, nunca negativos.
6. **Balanço (estoque):** posição mais recente (ITR mais novo, senão DFP), sempre com
   `ORDEM_EXERC == "ÚLTIMO"`. Registrar `data_balanco`.
7. **Quantidade de ações:** `QT_ACAO_*_CAP_INTEGR − QT_ACAO_*_TESOURO` por classe (ON e
   PN), da `composicao_capital` mais recente. **Escala mista:** se `PL ÷ ações total >
   50 × preço`, a quantidade veio em milhar ⇒ multiplicar por 1000 e marcar o alerta
   `qtd_em_milhar`. Se depois da correção `PL ÷ ações total` continuar fora do intervalo
   entre `preço ÷ 40` e `40 × preço`, marcar o alerta `escala_suspeita`. Nesse caso, o
   valor de mercado e os múltiplos que dependem dele ficam `NaN`.
8. **Ticker → empresa:** FCA (`Codigo_Negociacao` ↔ `CNPJ_Companhia`), do arquivo mais
   recente; se faltar, do anterior; se ainda faltar, casar `DENOM_SOCIAL`/`DENOM_COMERC`
   pelo nome normalizado no `cad_cia_aberta.csv`, incluindo os aliases de prefixo
   `LOJAS MARISA → MARISA LOJAS`, `BTGP BANCO → BANCO BTG PACTUAL` e
   `SID NACIONAL → CIA SIDERURGICA NACIONAL`. Resultado ambíguo não é aceito. Tickers
   sem casamento vão para uma lista de pendências; os resolvidos por nome ficam listados
   separadamente no metadado.
9. **Universo:** `codbdi == "02"` com `especi` começando por `ON`, `PN` ou `UNT`.
   Excluir BDR, ETF, FII, direitos, bônus. Liquidez mínima parametrizável, padrão
   R$ 100 mil de volume médio diário nos últimos 63 pregões (e ao menos 40 pregões com
   negócio).
10. **Valor de mercado da empresa:** Σ (ações da classe × preço da classe). Classe ON
    usa o preço de um ticker terminado em 3; PN, terminado em 4/5/6; units (terminadas
    em 11) não somam valor próprio. Se uma classe não tem preço, usar o da outra. Todas
    as métricas por empresa (P/L, DY etc.) usam o valor de mercado da **empresa** e se
    repetem em cada ticker dela; só `preco` e `liquidez_media_diaria` são do ticker.
    Se não houver preço ON nem PN, usar a composição `Composicao_BDR_Unit` do FCA:
    preço equivalente por ação = preço da unit ÷ ações por unit, com alerta
    `mcap_por_unit`. A unit continua sem dupla contagem.
11. **Financeiras** (`financeira = True`) quando o setor do cadastro contém "Bancos",
    "Seguradoras" ou "Intermediação Financeira", **ou** a empresa não tem a conta
    `1.01` "Ativo Circulante". Para elas calcular só: preço, valor de mercado,
    liquidez, `p_l`, `lpa`, `p_vp`, `vpa`, `dy`, `roe`, `roa`, `patrimonio_ativos`,
    `passivos_ativos`, `cagr_lucros_5a` (e `peg`); o resto fica vazio.
12. **Vazio é vazio:** dado ausente ou inaplicável é `NaN`, nunca `0`. Denominador
    ≤ 0 ⇒ `NaN`.
13. **Evento de capital recente:** se algum retorno diário nos últimos 252 pregões
    passar de ±35%, marcar o alerta `salto_preco`. Não alterar o cálculo.

## Métricas (`ativos/core/metricas_acoes.py`, funções puras)

Convenção: valores em reais; razões em fração (0,25 = 25%); a tela formata.

| Coluna | Fórmula |
|---|---|
| `preco` | último fechamento do ticker |
| `valor_mercado` | regra 10 |
| `liquidez_media_diaria` | volume médio dos últimos 63 pregões |
| `lpa` | lucro TTM ÷ ações da empresa |
| `p_l` | valor de mercado ÷ lucro TTM (vazio se lucro ≤ 0) |
| `vpa` | PL controladores ÷ ações |
| `p_vp` | valor de mercado ÷ PL controladores |
| `dy` | dividendos e JCP pagos TTM (regra 4) ÷ valor de mercado |
| `peg` | `p_l ÷ (cagr_lucros_5a × 100)`; vazio se `p_l` vazio ou CAGR ≤ 0 |
| `p_ativos` | valor de mercado ÷ ativo total |
| `p_cap_giro` | valor de mercado ÷ (ativo circulante − passivo circulante); vazio se ≤ 0 |
| `p_ativo_circ_liq` | valor de mercado ÷ (ativo circulante − passivo exigível); vazio se ≤ 0 |
| `psr` | valor de mercado ÷ receita TTM |
| `p_ebit` | valor de mercado ÷ EBIT TTM |
| `ev_ebit` | (valor de mercado + dívida líquida) ÷ EBIT TTM |
| `margem_bruta` | resultado bruto TTM ÷ receita TTM |
| `margem_ebit` | EBIT TTM ÷ receita TTM |
| `margem_liquida` | lucro TTM ÷ receita TTM |
| `divida_bruta` | `2.01.04` + `2.02.01` |
| `divida_liquida` | dívida bruta − (caixa `1.01.01` + aplicações `1.01.02`) |
| `div_liq_ebit` | dívida líquida ÷ EBIT TTM (vazio se EBIT ≤ 0) |
| `div_liq_patrimonio` | dívida líquida ÷ PL controladores |
| `roe` | lucro TTM ÷ PL controladores |
| `roa` | lucro TTM ÷ ativo total |
| `roic` | EBIT TTM × (1 − 0,34) ÷ (dívida bruta + PL controladores − caixa − aplicações) |
| `liquidez_corrente` | ativo circulante ÷ passivo circulante |
| `patrimonio_ativos` | PL controladores ÷ ativo total |
| `passivos_ativos` | (ativo total − PL consolidado) ÷ ativo total |
| `giro_ativos` | receita TTM ÷ ativo total |
| `cagr_receitas_5a` | (receita do último DFP ÷ receita 5 exercícios antes)^(1/5) − 1; vazio se algum ≤ 0 |
| `cagr_lucros_5a` | idem com lucro dos controladores |

Metadados por linha: `ticker`, `empresa`, `cnpj`, `origem_cnpj`, `setor`, `financeira`,
`data_balanco`, `data_entrega` (DT_RECEB do balanço usado), `alertas` (lista de strings:
`qtd_em_milhar`, `escala_suspeita`, `mcap_por_unit`, `dy_dva`, `salto_preco`,
`sem_cnpj`).

## Pipeline (`scripts/atualizar_ativos.py`)

`python -m scripts.atualizar_ativos [--data AAAA-MM-DD] [--liquidez-minima 100000]`
lê o cache bruto, monta a tabela e grava `acoes.parquet` e `acoes_meta.json` (data de
referência da cotação, data de geração, contagem de linhas, coberturas de P/L e DY,
pendências de ticker, tickers resolvidos por nome e versão do esquema) na pasta de
derivados. Imprime um resumo: universo, coberturas e pendências. A renomeação da coluna
de alertas incrementou o esquema para a versão 2. **Rode o pipeline contra o cache real
ao final e informe o resumo.**

## Tela (`ativos/ui/pagina_busca.py`) e navegação

- Nova página "Busca avançada" dentro do módulo Ativos em `app_financas.py`, mantendo a
  página "Ativos B3" como visão geral e a página Macro como padrão. Atualize os testes
  do entrypoint que dependem do texto atual.
- Carrega o parquet (cache `st.cache_data`). Sem parquet: mensagem clara com o comando
  do pipeline.
- Tabela com `st.dataframe` e `column_config`:
  - ticker fixo à esquerda (`pinned`); preço e valor de mercado em R$ com abreviação
    K/M/B; razões em %; múltiplos com 2 casas; vazio exibido como "—";
  - cabeçalhos em pt-BR curtos, com tooltip (`help`) explicando a fórmula de cada um.
- Painel de filtros: setor (multiseleção), liquidez mínima, excluir financeiras,
  ocultar linhas com alertas; mínimo/máximo por indicador, gerado a partir de um dicionário
  `METRICAS` (rótulo, grupo, formato, descrição). Seletor de grupos de colunas:
  Valuation, Rentabilidade, Endividamento, Crescimento, Liquidez e tamanho.
- Presets (módulo `ativos/core/presets.py`, puro e testado):
  - Graham defensivo: `p_l ≤ 15`, `p_vp ≤ 1,5`, `p_l × p_vp ≤ 22,5`,
    `liquidez_corrente ≥ 1,5`, `dy > 0`, `financeira = False`;
  - Bazin: `dy ≥ 6%` e `div_liq_ebit ≤ 3`;
  - Magic Formula: ordenar pela soma dos postos de `1/ev_ebit` (earnings yield) e
    `roic`, sem financeiras, com `ev_ebit > 0` e `roic > 0`;
  - Qualidade com dívida baixa: `roe ≥ 15%`, `margem_liquida ≥ 10%`,
    `div_liq_ebit ≤ 2`.
- Exportar CSV (UTF-8 com BOM, separador `;`, decimal `,`) do que está na tela.
- Comparador: seleção de até 5 tickers mostra as colunas lado a lado.
- Mostrar no topo a data da cotação, a data de geração e a contagem exibida/total.
- A coluna "Avaliação" (faixa de valor e score) **não** aparece ainda.
- Aviso de uso pessoal já usado na página atual (`pagina_ativos.AVISO`) reaproveitado.

## Testes obrigatórios

- Um golden test por fórmula da tabela, com números calculados à mão.
- Normalização: escala MIL, `PL = 2.03 − 2.03.09`, TTM com acumulado do ano, ações em
  milhar, units sem dupla contagem, financeira só com as colunas permitidas, `NaN` para
  denominador ≤ 0.
- Parser de COTAHIST com linha sintética de 245 caracteres.
- Presets e filtros (incluindo `NaN` fora dos filtros que o exigem).
- UI via `AppTest` com um parquet sintético em pasta temporária (`LASTRO_DADOS_DIR`).
- Guardrail de linguagem sobre todos os textos da tela (rótulos, ajuda, presets).

## Fora de escopo

FIIs, ETFs, valuation, score, risco, carteira, mobile, GitHub Actions e preço ajustado.
Não crie workflow nem asset de release agora.

## Ao terminar

Rode o gate completo, atualize `CONTEXT.md` (estado e próximo passo), **não faça push**,
e devolva um resumo curto: o que foi feito, o resultado do pipeline real (universo,
cobertura de P/L, pendências) e qualquer decisão que tenha precisado tomar fora desta
especificação.
