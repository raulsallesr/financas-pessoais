# Validação da calibração do valuation — 2026-10-09

Evidência do item 1.1 do Ciclo 1. O pipeline real foi regenerado com dados públicos do
cache local: 244 ações e 155 FIIs. Nenhum dado de carteira ou identificador pessoal foi
lido, gravado ou enviado.

## Premissas resultantes

| Premissa | Valor |
|---|---:|
| Taxa livre de risco (`rf`) | 12,7965% |
| Data da curva do Tesouro | 2026-10-07 |
| Fator de Bazin | 0,50 |
| Taxa mínima de Bazin (`rf × fator`) | 6,3983% |
| ERP | 5,00% |
| Custo do capital próprio (`k`) | 17,7965% |
| Crescimento perpétuo (`g`) | 4,00% |
| Taxa exigida dos FIIs | 10,8770% |

ERP e `g` foram mantidos. Não há histórico de desfechos nem DCF para justificar mudança;
ajustá-los à distribuição do próprio dia seria circular.

## Distribuição observada

Somente ativos com ao menos dois modelos aplicáveis entram nas porcentagens.

| Cenário das ações | Abaixo | Dentro | Acima | Válidos |
|---|---:|---:|---:|---:|
| Antes: Bazin fixo em 6% | 39 (18,1%) | 75 (34,9%) | 101 (47,0%) | 215 |
| Padrão aprovado: `rf × 0,50` | 39 (18,1%) | 74 (34,4%) | 102 (47,4%) | 215 |
| Contrafactual rejeitado: `rf × 0,30` | 49 (22,8%) | 84 (39,1%) | 82 (38,1%) | 215 |

O fator 0,30 faria a distribuição caber no intervalo de sanidade de 20% a 40% por lado,
mas foi rejeitado porque foi escolhido a partir dos preços que o modelo pretende avaliar.
O fator 0,50 mantém a premissa clássica próxima de 6% quando `rf` está em 12% e torna a
regra sensível ao regime de juros. A concentração acima da faixa permanece evidência da
limitação dos modelos atuais para crescimento; DCF e validação histórica são os próximos
instrumentos corretos, não ajuste do fator.

Nos FIIs não houve mudança de fórmula: 139 têm os dois modelos aplicáveis; 90 (64,7%)
ficaram abaixo, 23 (16,5%) dentro e 26 (18,7%) acima da faixa.

### Quantidade de modelos aplicáveis

| Classe | 0 modelos | 1 modelo | 2 modelos | 3 modelos | 4 modelos |
|---|---:|---:|---:|---:|---:|
| Ações | 13 | 16 | 16 | 86 | 113 |
| FIIs | 0 | 16 | 139 | 0 | 0 |

## Ativos de referência após a calibração

| Ticker | Preço | Faixa baixa | Central | Faixa alta | Posição | Modelos |
|---|---:|---:|---:|---:|---|---:|
| ABEV3 | R$ 16,15 | R$ 8,97 | R$ 11,63 | R$ 12,37 | acima da faixa | 3 |
| ITUB4 | R$ 49,35 | R$ 29,27 | R$ 37,62 | R$ 43,88 | acima da faixa | 4 |
| PETR4 | R$ 55,48 | R$ 34,45 | R$ 46,48 | R$ 69,84 | dentro da faixa | 3 |
| VALE3 | R$ 67,64 | R$ 47,65 | R$ 52,59 | R$ 70,57 | dentro da faixa | 3 |
| WEGE3 | R$ 51,77 | R$ 9,36 | R$ 12,28 | R$ 12,81 | acima da faixa | 3 |
| HGLG11 | R$ 155,50 | R$ 132,45 | R$ 143,62 | R$ 154,78 | acima da faixa | 2 |
| KNRI11 | R$ 163,25 | R$ 131,30 | R$ 142,05 | R$ 152,80 | acima da faixa | 2 |
| MXRF11 | R$ 9,35 | R$ 9,60 | R$ 9,94 | R$ 10,28 | abaixo da faixa | 2 |

## Regressão dos insumos públicos

O pipeline regenerado preservou os valores de referência já documentados: PETR4 P/L
5,72 e P/VP 1,59; VALE3 26,57 e 1,40; ABEV3 15,36 e 2,83; ITUB4 12,11 e 2,60; HGLG11
DY 12 meses 8,48% e P/VP 0,94. A calibração altera somente a premissa de Bazin em memória;
não muda Parquet, adapter ou métrica de origem.

## Gates executados

- `ruff check .`: aprovado.
- Testes-alvo de premissas e valuation: 35 aprovados.
- `python -m pytest tests -q --cov=.`: 369 aprovados; cobertura total 87,32% (piso 85%).
- `python -m scripts.atualizar_ativos`: aprovado; 244 ações e 155 FIIs, sem pendência de
  ticker em ações e com as 20 pendências de FIIs já conhecidas.
- A primeira execução da suíte dentro do OneDrive sofreu `WinError 5` nos temporários e
  cobertura incompleta; a repetição em pasta temporária isolada terminou verde sem mudança
  de código.
