# Estado detalhado do módulo Ativos em 2026-10-09

> Diário do dia em que o módulo nasceu (fases 0 a 4 parcial). Movido do `CONTEXT.md`,
> que deve ficar curto. Para retomar, leia `CONTEXT.md`, `docs/RETOMADA_EM_OUTRA_MAQUINA.md`
> e `docs/product/ROTEIRO_PROXIMAS_FASES.md`. Números mudam com os dados do dia.

- **Nova direção (2026-10-09):** o FocusLens vira o módulo **Macro** de uma plataforma
  maior, provisoriamente chamada **Lastro**.
  - Novo módulo **Ativos B3** (`ativos/`), com plano em `docs/product/PLANO_LASTRO.md`.
  - Decisões do Raul: uso pessoal com repositório público como portfólio; motor Python
    + web Streamlit primeiro; fontes oficiais e gratuitas (CVM + COTAHIST); nome novo
    para a plataforma.
  - A **Fase 0 está concluída**: navegação Macro + Ativos e relatório de cobertura em
    `docs/validation/COBERTURA_ATIVOS_FASE0.md`. Ações e FIIs são viáveis; ETFs pedem
    tabela curada.
  - A primeira fatia vertical de ações está implementada: adapters CVM/COTAHIST,
    base point-in-time, 32 métricas/insumos (incluindo DPA), presets/filtros, pipeline
    Parquet/JSON e página **Busca avançada**. A visão geral **Ativos B3** foi preservada.
  - A segunda fatia vertical, **Busca de FIIs**, também está implementada: informes
    mensais/trimestrais, composição e tipo, renda, vacância, presets/filtros,
    comparador, CSV e derivados `fiis.parquet`/`fiis_meta.json`. O CLI aceita
    `--classe {acoes,fiis,todos}` e usa `todos` por padrão.
  - O corte de valor estimado também está concluído, exceto DCF: taxa livre de risco
    interpolada da curva prefixada local, premissas editáveis, Graham, Bazin, Gordon,
    múltiplos setoriais, modelos patrimonial e de renda para FIIs, faixa P25–P75 e
    página unificada **Ficha do ativo**. As buscas calculam tudo em memória; os parquets
    esquema 3 persistem apenas `dpa` e `rendimento_12m_cota` como novos insumos.
  - Busca avançada no esquema 2: `alertas` substitui o nome anterior; DY usa dividendos
    e JCP pagos TTM da DFC (DVA apenas como fallback `dy_dva`); P/ACL usa passivo
    exigível; units podem derivar valor de mercado pela composição do FCA.
  - Pipeline real em 2026-10-09, com liquidez mínima de R$ 100 mil/dia: 244 tickers,
    82,0% com P/L, 95,5% com DY, 98,8% com DPA e nenhuma pendência de CNPJ. O metadado registra 12
    tickers resolvidos por nome, inclusive `AMAR3`, `BPAC3/5/11` e `CSNA3`.
  - GFSA3 e MEAL3 permanecem com `escala_suspeita` e, por segurança, sem valor de
    mercado nem múltiplos dependentes. GFSA combina grupamento/diluição e composição
    defasada; MEAL tem sequência anômala de quantidades ON/PN nos informes de 2026.
  - Pipeline real de FIIs em 2026-10-09, com cotação até 2026-10-08 e liquidez mínima
    de R$ 100 mil/dia: 155 fundos, 100% com P/VP, 99,4% com DY/rendimento 12m e 47,7% com
    vacância. Tipos: 72 Tijolo, 51 Papel, 22 Fundo de fundos, 4 Híbrido e 6 Outros.
  - O DY 12m agora descarta mês com `Percentual_Dividend_Yield_Mes` negativo ou acima
    de 5%, preserva zero como válido e anualiza pelos meses válidos; menos de 6 válidos
    fica vazio. Rentabilidade mensal fora de `[-15%; +15%]` invalida `rentab_12m` (a faixa de ±50% foi
    apertada depois que o VISC11 mostrou -28% em 2026-05 com VP estável).
    Ambos geram `dy_dados_suspeitos`; a carga real atual registrou 27 fundos. No XPML11,
    o mês negativo de 2026-01 foi excluído e o DY 12m passou de 3,05% para 10,00% pela
    regra solicitada (soma válida de R$ 9,7622, anualizada por 11 meses, sobre R$ 106,50).
  - Colisões do mesmo ISIN em vários CNPJs agora usam desempate nominal estrito e
    auditável. `KISU11`, `SNEL11`, `TRXF11` e `XPML11` foram resolvidos pelo nome de
    pregão. Restam 20 pendências fail-closed: 16 sem informe mensal correspondente,
    3 sem palavra nominal em comum (`PQDP11`, `RBRY11`, `ZAGH11`) e 1 empate nominal
    (`HSAF11`). O metadado esquema 3 registra resolvidos e motivo por pendência.
  - O sandbox bloqueou `%USERPROFILE%\.cache\lastro\derived`; o pipeline conjunto
    foi validado via `LASTRO_DADOS_DIR=.pytest_tmp-derived-real-valuation`, fora do git.
  - Valuation real com a curva de 2026-10-07 (`rf=12,7965%`): ações com 29 linhas sem
    faixa e 215 com faixa; FIIs com 16 sem faixa e 139 com faixa. O alerta calculado
    `valuation_fragil` marcou 21 ações e 32 FIIs, sem ser persistido no parquet.
  - Gate atual (fim do dia): ruff limpo, 363 testes e cobertura de 87,3%. O `tmp_path` sob
    Python 3.13/Windows pode emitir `WinError 5` na limpeza tardia sem indicar falha.
  - **Próximo passo:** DCF de dois estágios, score, tabela curada de ETFs e atualização
    automática dos derivados permanecem como cortes independentes.
  - **Pendente do Raul:** decidir o retorno total para backtest (DVA oficial
    aproximada ou Yahoo ajustado).
