# Quadro de itens

Fonte do que está aberto, em andamento e pronto. Origem dos IDs:
`docs/product/DIAGNOSTICO_E_PLANO_2026-10-09.md` (Ciclos 1 a 3) e `0.x` para infraestrutura.
**Status:** `aberto`, `em andamento`, `pronto`, `bloqueado`. **Decisão do Raul:** `sim` = a IA
para e pergunta antes de avançar. Quem muda o status edita só a própria linha e informa o
`equipe fechar`. Regras em `PROTOCOLO.md`.

Atualizado em 2026-10-13.

| ID | Item | Status | Dono | Atualizado | Decisão do Raul | Notas |
|---|---|---|---|---|---|---|
| 0.1 | Protocolo de coordenação entre IAs e máquinas | em andamento | claude-trabalho | 2026-10-13 | | `SPEC_EQUIPE_CLI.md`; fases A a F do plano |
| 0.2 | Dados de mercado iguais nas duas máquinas (workflow + release `dados-ativos` + sincronizar) | em andamento | claude-trabalho | 2026-10-13 |  | É o item 1.4; depende de rodar o workflow no GitHub |
| 1.1 | Calibrar o valuation (Bazin = rf × fator) | pronto | claude-trabalho | 2026-10-13 | | `e121edc`; feito por sessão paralela, reconferido |
| 1.2 | Painel de qualidade de dados | aberto | | 2026-10-13 | | Próximo passo do Ciclo 1 |
| 1.3 | Reconciliação automática contra a CVM no CI | aberto | | 2026-10-13 | | 6 tickers fixos, cálculo independente |
| 1.4 | Atualização automática dos derivados (Actions + release) | aberto | | 2026-10-13 | | Mesmo escopo do 0.2 |
| 1.5 | Sentinela das fontes (layout CVM e B3) | aberto | | 2026-10-13 | | Workflow semanal |
| 1.6 | Vitrine do repositório (screenshots, GIF, README do módulo Ativos) | aberto | | 2026-10-13 | | Sem demo pública |
| 1.6b | Refatoração antes dos ETFs | aberto | | 2026-10-13 | | `pipeline_acoes.py` 940 linhas; telas duplicadas |
| 1.6c | Endurecimento (cache do valuation, constantes nomeadas, teste de ponta a ponta de ações) | aberto | | 2026-10-13 | | Achados A1, A4 a A8 do diagnóstico |
| 1.7 | Limpezas: nome definitivo da plataforma; card Finanças no SuperHub da Fits | aberto | | 2026-10-13 | sim | O nome e o commit no hub dependem do Raul |
| 2.1 | ETFs (tabela curada, exposição, ranking) | aberto | | 2026-10-13 | | Depois da refatoração 1.6b |
| 2.2 | DCF de dois estágios (não financeiras) | aberto | | 2026-10-13 | | Fecha a lacuna do valor estimado para empresas de crescimento |
| 2.3 | Histórico de indicadores (pipeline em datas passadas) | aberto | | 2026-10-13 | | O pipeline já aceita `--data` |
| 2.4 | Spike do preço ajustado (Yahoo × COTAHIST) | aberto | | 2026-10-13 | | Decisão tomada: Yahoo só para preço, adapter isolado |
| 3.1 | Score Lastro | aberto | | 2026-10-13 | | Depende de 2.3 |
| 3.2 | Score Lab (backtest, IC de Spearman) | aberto | | 2026-10-13 | | Depende de 2.3 e 2.4 |
| 3.3 | Risco e carteira (Sharpe, HRP, walk-forward) | aberto | | 2026-10-13 | | Depende de 2.4 |
| 3.4 | Raio-x da carteira real | aberto | | 2026-10-13 | sim | Privacidade: o Raul valida o contrato antes |
