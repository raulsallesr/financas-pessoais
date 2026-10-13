# Especificação — Calibração das premissas do valuation (Ciclo 1.1)

Data da decisão: 2026-10-09. Este corte executa o item 1.1 de
[`DIAGNOSTICO_E_PLANO_2026-10-09.md`](DIAGNOSTICO_E_PLANO_2026-10-09.md) sem alterar as
fórmulas dos modelos, os dados derivados ou a regra de consolidação da faixa.

## Problema

O modelo de Bazin usa uma taxa mínima fixa de 6%, enquanto os demais modelos partem da
curva do Tesouro usada como taxa livre de risco. A premissa fixa não reage ao regime de
juros e pode ficar incoerente com a mesma sessão de cálculo. Na base de 2026-10-09, com
`rf` de 12,7965%, 101 de 215 ações com faixa válida estavam acima da faixa.

## Decisão

1. A taxa mínima de Bazin passa a ser derivada por `rf × fator de Bazin`.
2. O fator padrão é **0,50**. Ele mantém a referência clássica próxima de 6% quando a
   taxa livre de risco está em 12%, mas reage de forma explícita quando a curva muda.
3. O fator é editável na interface. A taxa resultante aparece ao lado do custo do capital
   próprio e da taxa exigida dos FIIs.
4. ERP permanece em 5% e `g` em 4%. Sem histórico de desfechos ou DCF, alterá-los para
   aproximar a distribuição corrente seria ajuste aos próprios preços que o modelo tenta
   avaliar.
5. A distribuição de posições é diagnóstico, não objetivo de otimização. O relatório de
   validação deve mostrar o antes, o depois e alternativas consideradas.

## Contrato de código

- `PremissasValuation.bazin_fator_rf` é finito e estritamente positivo.
- `PremissasValuation.bazin_taxa` é uma propriedade derivada de
  `rf × bazin_fator_rf`; não existe segunda fonte de verdade para a taxa.
- Alterar `rf` recalcula Bazin, Gordon, FIIs e `k`; alterar o fator recalcula somente
  Bazin.
- Restaurar o padrão repõe o fator 0,50 e a referência vigente da curva.
- O painel explica fórmula, fator e taxa resultante. Nenhum texto pode usar linguagem de
  recomendação.

## Testes e gates

- Golden de Bazin: DPA de R$ 0,60, `rf` de 12% e fator 0,50 produz R$ 10,00.
- Teste de vínculo: mudar `rf` ou o fator muda a taxa e o valor de Bazin de forma
  determinística.
- Testes de validação e restauração do fator.
- Testes existentes de Gordon, Graham, múltiplos, FIIs e UI permanecem verdes.
- `ruff check .` e `python -m pytest tests -q --cov=.` com cobertura mínima de 85%.
- Distribuição real e ativos de referência registrados em
  `docs/validation/CALIBRACAO_VALUATION_2026-10-09.md`.

## Alternativa analisada e rejeitada

Um fator próximo de 0,30 faz a amostra corrente cair dentro do intervalo de sanidade de
20% a 40% por lado. Ele foi rejeitado como padrão porque nasceu da distribuição dos
preços atuais, sem validação histórica independente. O Score Lab, o histórico e o DCF
são os cortes adequados para validar ou ampliar os modelos sem ajuste circular.

## Fora de escopo

- DCF, beta, backtest, Score Lastro e histórico de indicadores.
- Mudança na faixa P25–P75 ou no mínimo de dois modelos.
- Alteração dos Parquets, adapters CVM/B3 ou motores do módulo Macro.
- Publicação de demonstração ou abertura da plataforma a terceiros.
