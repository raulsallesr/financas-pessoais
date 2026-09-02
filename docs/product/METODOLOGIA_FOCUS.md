# Metodologia — Focus Semanal

O Focus Semanal transforma duas fotografias comparáveis do Boletim Focus em
uma resposta curta: quais expectativas realmente mudaram e qual revisão foi
mais relevante. O cálculo é determinístico, usa somente dados públicos e não
produz recomendação de investimento.

## Fonte e recorte

- Fonte: Sistema de Expectativas de Mercado do Banco Central, pela API pública
  Olinda/OData.
- Indicadores do resumo: Selic, IPCA, Câmbio e PIB Total.
- Comparação: última leitura contra a leitura anterior disponível para o mesmo
  indicador e a mesma referência.
- Evidência preservada: valor atual, valor anterior e datas reais das coletas.

IGP-M e dívida líquida continuam disponíveis nos detalhes do app, mas não
entram no ranking desta etapa.

## O que é uma mudança relevante

Cada indicador tem um limiar de estabilidade adequado à sua unidade:

| Indicador | Limiar |
|---|---:|
| Selic | 0,10 ponto percentual |
| IPCA | 0,05 ponto percentual |
| Câmbio | R$ 0,05 |
| PIB Total | 0,05 ponto percentual |

O delta é `valor atual - valor anterior`. Um movimento só é classificado como
alta ou queda quando seu valor absoluto ultrapassa o limiar; no limite exato,
permanece estável.

Para comparar grandezas diferentes, o ranking usa uma relevância normalizada:

```text
relevância = abs(delta) / limiar do indicador
```

Assim, uma revisão de 0,10 na Selic não é comparada diretamente a R$ 0,10 no
câmbio. O app mostra até os três maiores resultados. Empates seguem a ordem
fixa Selic, IPCA, Câmbio e PIB Total para manter a saída reproduzível.

## Estados da leitura

- **Atualizado:** há coleta recente e ao menos uma revisão relevante, ou é a
  primeira fotografia disponível.
- **Sem mudança relevante:** todos os indicadores comparáveis ficaram dentro
  dos próprios limiares.
- **Defasado:** a coleta mais recente tem mais de cinco dias úteis. Os números
  continuam visíveis, acompanhados da ressalva de atualidade.
- **Indisponível:** não existe fotografia íntegra de nenhum dos indicadores
  acompanhados.

## Limites

- O Focus representa a mediana das expectativas dos participantes; não é dado
  realizado nem previsão do Banco Central.
- O ranking mede tamanho relativo da revisão, não importância econômica
  absoluta, causalidade ou probabilidade de acerto.
- Mudanças de referência, especialmente na próxima reunião da Selic, não são
  tratadas como comparáveis.
- Notícias são contexto editorial e não alteram o cálculo numérico.
- A tela é educacional e analítica; não indica compra, venda ou alocação.

## Implementação verificável

O motor puro está em `focuslens/core/focus_semanal.py`; formatação e narrativa ficam em
`focuslens/ui/focus_apresentacao.py`; a composição Streamlit está em
`focuslens/ui/pagina_focus.py`.
Os testes cobrem normalização, ranking, empates, estados, primeira fotografia
e integração visual.
