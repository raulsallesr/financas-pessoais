---
data: 2026-10-09
quem: raul
status: vigente
---
# Retorno total: Yahoo Finance só para preço ajustado
## Decisão
O preço ajustado por desdobramentos e dividendos, necessário para backtest, Score Lab e
otimização de carteira, vem do **Yahoo Finance**, restrito a backtest e risco, num adapter
isolado, com cache local e aviso de fonte não oficial. O app principal (buscas, valor estimado)
não depende dele. Antes de plugar, um spike compara Yahoo e COTAHIST com eventos em 20 tickers
(item 2.4 do quadro).
## Por quê
O COTAHIST não ajusta eventos de capital e reconstruir retorno total só com fontes oficiais é
mais trabalhoso e menos preciso. O Yahoo é gratuito, sem token, e destrava Score e carteira
em dias.
## Alternativas rejeitadas
Só dados oficiais (DVA/DFC mais eventos de capital): mais puro, porém bem mais trabalhoso e
menos preciso. Fonte paga: custo.
