# Metodologia do Radar Macro

## O que ele faz

O Radar organiza sinais públicos em um cenário direcional de **4 a 12
semanas**. Toda conclusão mostra evidências e condições de invalidação. Ele
não produz alvo de preço, probabilidade calibrada nem recomendação
personalizada.

## Entradas

- **Expectativas:** Boletim Focus/BACEN (Selic, IPCA, câmbio, PIB e dívida).
- **Dólar:** PTAX de venda do Banco Central; referência oficial diária, não
  cotação intradiária de corretora.
- **Petróleo:** Brent spot da EIA distribuído pelo FRED; pode ter defasagem de
  publicação, por isso a data fica visível.
- **Bitcoin:** último preço do candle diário BTC/BRL da API pública de
  mercado da Binance; o candle do dia corrente ainda pode estar aberto.
- **Notícias:** somente título, categoria, fonte e horário dos feeds RSS de
  InfoMoney e Brazil Journal. O corpo das matérias não é raspado nem tratado
  como se tivesse sido lido.

## Como a leitura é formada

1. Cada série vira um sinal explícito: alta, queda ou lateralidade com limiar
   próprio.
2. Os sinais são agrupados em inflação/custos, condições monetárias,
   atividade, fiscal e apetite a risco.
3. Regras condicionais produzem cenário-base, efeitos relativos por classe e
   eventos que fariam a leitura mudar.
4. Séries excessivamente defasadas deixam de sustentar o cenário.
5. A confiança máxima desta versão é **moderada**. Sem cobertura suficiente,
   a saída é marcada como baixa.

## Limites honestos

- Associação macro não prova causalidade e pode mudar entre regimes.
- “Vento favorável” não significa preço barato, retorno garantido ou
  adequação a uma pessoa.
- Frequência de tema em manchete mede atenção editorial, não sentimento nem
  veracidade.
- A projeção ainda não foi calibrada contra um histórico de acertos. O
  próximo gate técnico é um backtest temporal, sem usar informação futura.

## Próxima evolução do motor

1. Backtest e placar de acerto por horizonte/regime.
2. IPCA realizado, atividade, emprego, curva de juros e dados externos.
3. Probabilidades somente depois de calibração fora da amostra.
4. Resumos semânticos via provedor autorizado, caso haja fonte licenciada,
   custo aceito e chave guardada exclusivamente em variável de ambiente.
