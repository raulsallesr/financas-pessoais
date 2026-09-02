# Metodologia — Curva Tesouro

A Curva Tesouro organiza pontos observados de títulos prefixados para responder
como as taxas oferecidas à pessoa física mudaram. O cálculo é determinístico,
rastreável e educacional; não recomenda título, vencimento ou operação.

## Fonte oficial e licença

- Fonte: conjunto **Taxas dos Títulos Ofertados pelo Tesouro Direto**, do
  Tesouro Transparente.
- Recurso: CSV diário `precotaxatesourodireto.csv`.
- Recorte do MVP: somente `Tesouro Prefixado`, sem juros semestrais.
- Campo usado: `Taxa Compra Manha`, definido nos metadados oficiais como a
  taxa disponível para o investidor comprar o título.
- Licença dos dados: Open Data Commons Open Database License, ODbL 1.0.

O CSV validado em 26/08/2026 continha 175.462 registros, oito famílias e
histórico efetivo desde 31/12/2004. O produto preserva a atribuição ao Tesouro
Transparente no cache, na interface e nesta documentação.

Fonte e metadados:

- https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
- https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/1a8eb2e3-4902-4a38-a1eb-6410f23d90de/download/taxa.pdf

## Contrato do ponto

```text
data_referencia, tipo_titulo, vencimento, taxa_compra,
taxa_venda, pu_compra, pu_venda, fonte
```

Campos ausentes permanecem ausentes. A taxa de compra, a data-base e o
vencimento são obrigatórios; um registro inválido interrompe a atualização em
vez de receber zero ou estimativa.

## Fotografias D-5 e D-21

As datas são selecionadas entre as observações realmente publicadas:

- atual: última data-base disponível;
- D-5: quinta observação anterior à atual;
- D-21: vigésima primeira observação anterior à atual.

Fins de semana, feriados e dias sem publicação não são preenchidos. Uma taxa
só é comparada quando o mesmo vencimento existe nas duas fotografias.

```text
variação em bps = (taxa atual - taxa anterior) × 100
```

Um ponto percentual equivale a 100 pontos-base. O movimento central mostrado
no resumo é a mediana das variações D-5 dos vencimentos comparáveis, evitando
que um único título domine a conclusão.

O limiar de estabilidade é de 2 bps por vencimento. Valores acima de 2 bps
contam como alta, abaixo de -2 bps como queda e o intervalo fechado entre eles
como estabilidade.

## Inclinação e gráfico

A inclinação é a taxa do vencimento mais longo menos a taxa do vencimento mais
curto da fotografia atual, em pontos-base. Ela descreve apenas os títulos
disponíveis naquele dia.

As linhas do gráfico conectam os marcadores para facilitar a leitura visual.
Somente os marcadores são pontos observados: não há bootstrap, spline,
interpolação de taxa ou construção de vértices sintéticos. Os valores exatos
ficam disponíveis em tabela.

## Cenário mecânico de choque paralelo

O cenário da `v2.0` parte exclusivamente da fotografia atual e aplica uma
hipótese explícita, igual para todos os vencimentos:

```text
taxa no cenário = taxa observada + choque em bps ÷ 100
```

Assim, um choque de `+25 bps` soma `0,25 p.p.` a cada taxa; `-50 bps` subtrai
`0,50 p.p.`. A função pura aceita de `-200` a `+200 bps`; a interface oferece
o recorte mais contido de `-100` a `+100 bps`, em passos de 25 bps.

Como o mesmo valor é somado a todos os pontos, a inclinação permanece
inalterada por construção. O gráfico compara a curva observada, em linha
sólida, com a hipótese, em linha tracejada; a tabela mantém os valores exatos.
O cenário não modifica a fotografia, o cache nem a leitura D-5/D-21.

Este recurso é uma análise de sensibilidade mecânica. Ele não estima chance de
ocorrência, causalidade, preço de título, retorno, duration, impostos, custos
ou adequação à carteira. Choques não paralelos e mudanças de inclinação ficam
fora deste contrato.

## Estados

- **Atualizada:** há curva recente, ao menos dois vencimentos e histórico
  suficiente para D-5 e D-21.
- **Histórico parcial:** a fotografia atual existe, mas falta algum horizonte
  ou há menos de dois vencimentos.
- **Defasada:** a última data-base tem mais de dois dias úteis.
- **Indisponível:** não existe fotografia íntegra salva.

Uma falha do Tesouro não derruba Focus, Radar ou Carteira. Se existir cache
válido, a interface o mantém visível com o estado correspondente.

## Cache e automação

O adaptador baixa no máximo 20 MB, valida o schema, filtra a família exata e
mantém as 45 datas publicadas mais recentes. O cache JSON é pequeno, contém
somente dados públicos e é atualizado em dias úteis pelo GitHub Actions. Uma
gravação atômica impede que uma interrupção deixe o arquivo pela metade.

## Limites

- Taxa de título público não é previsão pura da Selic. Ela também pode refletir
  prêmio de prazo, liquidez e condições de mercado.
- A curva do Tesouro Direto não substitui DI futuro nem curva soberana
  construída com metodologia profissional.
- O MVP não mistura prefixados com cupom, IPCA+, Selic, Educa+ ou Renda+.
- Taxas indicativas podem ser revistas pela fonte.
- A leitura não considera impostos, custódia, spread de corretora ou situação
  financeira individual.

## Implementação verificável

- `focuslens/core/curva_data.py`: contrato e consolidação pura;
- `focuslens/adapters/curva_fontes.py`: download, parsing, validação e cache;
- `focuslens/core/curva_modelo.py`: fotografias, variações, estados e narrativa;
- `focuslens/core/curva_cenarios.py`: choque paralelo puro, narrativa e guardrails;
- `focuslens/ui/curva_apresentacao.py`: formatação, séries do gráfico e linhas da tabela,
  incluindo a comparação Observada × Cenário, sem dependência do Streamlit;
- `focuslens/ui/pagina_curva.py`: apresentação Streamlit;
- `scripts/atualizar_curva_cache.py`: automação sem Streamlit.
