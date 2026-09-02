# Metodologia — Focus × Curva

O módulo Focus × Curva responde se a revisão recente da expectativa de Selic
e o movimento recente das taxas prefixadas apontam a mesma direção. A leitura
é determinística, rastreável e educacional: descreve convergência entre duas
janelas observadas, sem atribuir causalidade ou recomendar operação.

## Fontes oficiais

- **Focus:** Sistema de Expectativas de Mercado do Banco Central, via API
  pública Olinda/OData. O BC informa que as expectativas pertencem aos
  participantes da pesquisa, não ao próprio Banco Central.
- **Curva:** conjunto diário **Taxas dos Títulos Ofertados pelo Tesouro
  Direto**, do Tesouro Transparente, sob licença ODbL 1.0.
- **Campo da curva:** `Taxa Compra Manha`, definido nos metadados como a taxa
  disponível para o investidor comprar o título.

Fontes e metadados:

- https://www.bcb.gov.br/controleinflacao/expectativasmercado
- https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
- https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/1a8eb2e3-4902-4a38-a1eb-6410f23d90de/download/taxa.pdf

## Evidências comparáveis

### Focus

O sinal usa somente a mediana da **Selic para a próxima reunião do Copom**.
A leitura atual é comparada com a coleta anterior apenas quando ambas têm a
mesma referência, por exemplo `R6/2026`. Trocar a reunião e comparar os valores
produziria um falso movimento.

```text
delta Focus (p.p.) = mediana atual - mediana anterior
```

O limiar herdado do Focus Semanal é de 0,10 ponto percentual:

- acima de +0,10 p.p.: mais pressionada;
- abaixo de -0,10 p.p.: mais benigna;
- intervalo fechado de -0,10 a +0,10 p.p.: estável.

### Curva

O sinal usa Tesouro Prefixado sem cupom. Cada taxa atual é comparada apenas
com o mesmo vencimento na quinta observação publicada anteriormente, o D-5.

```text
delta do vencimento (bps) = (taxa atual - taxa D-5) × 100
sinal geral = mediana dos deltas dos vencimentos comparáveis
```

O limiar é de 2 pontos-base:

- acima de +2 bps: mais pressionada;
- abaixo de -2 bps: mais benigna;
- intervalo fechado de -2 a +2 bps: estável.

O uso da mediana evita que um único título domine o veredito. São necessários
ao menos dois vencimentos em comum.

## Ponta curta e ponta longa

Com quatro ou mais vencimentos comparáveis, o motor ordena os títulos pelo
vencimento e cria dois recortes de mesmo tamanho:

- **ponta curta:** os vencimentos comparáveis mais próximos;
- **ponta longa:** os vencimentos comparáveis mais distantes.

Quando a quantidade é ímpar, o vencimento central continua na mediana geral,
mas não é forçado para uma das pontas. Se curta e longa apontarem direções
relevantes e opostas, prevalece `Sinais mistos`.

Também há sinal misto quando a mediana geral fica estável, mas existem
movimentos relevantes de alta e de queda entre os vencimentos.

## Os cinco estados

As direções comparáveis são ordenadas como:

```text
mais benigna < estável < mais pressionada
```

| Focus \ Curva | Mais benigna | Estável | Mais pressionada |
|---|---|---|---|
| **Mais benigna** | Alinhados | Curva mais pressionada | Curva mais pressionada |
| **Estável** | Curva mais benigna | Alinhados | Curva mais pressionada |
| **Mais pressionada** | Curva mais benigna | Curva mais benigna | Alinhados |

Regras adicionais:

- **Sinais mistos:** a curva é internamente ambígua; ela não recebe uma
  direção artificial apenas para completar a matriz.
- **Dados insuficientes:** falta leitura anterior da Selic para a mesma
  reunião, a coleta Focus está defasada, a curva está indisponível/defasada,
  falta D-5 ou existem menos de dois vencimentos em comum.

## O que prova e o que faria mudar

Todo veredito mostra:

- valor anterior e atual da Selic, referência e datas das duas coletas;
- mediana D-5 da curva, quantidade de vencimentos e datas das duas
  fotografias;
- medianas e anos das pontas quando o recorte existe;
- limiares numéricos que fariam cada direção mudar.

As janelas do Focus e da curva podem começar ou terminar em datas diferentes.
O app as exibe separadamente em vez de escondê-las sob o rótulo genérico
"semana".

## Limites

- A taxa de um título público não é uma previsão pura da Selic. Prêmio de
  prazo, risco, liquidez e condições de mercado também podem mover a curva.
- A Selic da próxima reunião é apenas um ponto da trajetória esperada de juros;
  não equivale a toda a estrutura a termo.
- As taxas do Tesouro Direto refletem o mercado secundário e não substituem
  DI futuro ou uma curva soberana construída profissionalmente.
- Convergência de direção não prova causa, antecipação nem acurácia.
- Notícias, Radar Macro e dados pessoais da carteira não entram no cálculo.
- Não há probabilidade, alvo, ordem de compra/venda ou recomendação
  personalizada.

## Implementação verificável

- `focuslens/core/convergencia_modelo.py`: contratos, recortes, regras e narrativa pura;
- `focuslens/ui/convergencia_apresentacao.py`: formatação das métricas, sem Streamlit;
- `focuslens/ui/pagina_convergencia.py`: carregamento dos dois caches e composição visual;
- `tests/test_convergencia_modelo.py`: matriz, limiares, mistura e ausência;
- `tests/test_convergencia_apresentacao.py`: formatação sem falso zero;
- `tests/test_convergencia_ui.py`: veredito, evidência e condição de mudança.
