# Metodologia integrada — FocusLens BR

O FocusLens BR organiza expectativas, taxas observadas e cenários em uma única
jornada. A integração é determinística: ela seleciona a leitura mais íntegra
que os motores já calcularam, preserva as datas de cada fonte e mantém hipótese
separada de evidência. Não produz recomendação, probabilidade ou promessa de
retorno.

Este documento explica a integração. Fórmulas, limiares e estados detalhados
continuam nos contratos e metodologias de cada motor:

- [`METODOLOGIA_FOCUS.md`](METODOLOGIA_FOCUS.md);
- [`METODOLOGIA_CURVA.md`](METODOLOGIA_CURVA.md);
- [`METODOLOGIA_FOCUS_CURVA.md`](METODOLOGIA_FOCUS_CURVA.md);
- [`METODOLOGIA_RADAR.md`](METODOLOGIA_RADAR.md).

## A jornada e o lugar canônico de cada fato

1. **Resumo:** escolhe o que merece atenção agora. É o lugar do veredito, de
   duas a quatro provas, das datas por fonte, do primeiro limite e da condição
   que faria a leitura mudar.
2. **Expectativas:** detalha as revisões do Focus, seus valores, referências,
   estados e histórico. O Resumo não recalcula esses resultados.
3. **Curva:** detalha os pontos prefixados observados, as comparações D-5/D-21
   e o cenário mecânico. O cenário não entra no veredito.
4. **Carteira:** cruza somente dados mantidos na sessão com o cenário do Radar.
   Valores pessoais não alimentam o motor educacional público.

Notícias e Radar podem acrescentar no máximo um contexto externo não redundante
ao Resumo. Esse contexto aparece separado, com fonte, horizonte e confiança, e
não altera o cálculo de Focus × Curva.

## Como o Resumo escolhe a leitura principal

`resumo_integrado.montar_resumo_integrado()` recebe os contratos prontos de
Focus Semanal, Curva Tesouro e Focus × Curva. A primeira condição íntegra nesta
ordem lidera:

| Ordem | Leitura que lidera | Condição |
|---:|---|---|
| 1 | Focus × Curva | a convergência possui evidências comparáveis |
| 2 | Expectativas | o Focus está atual e tem revisão relevante |
| 3 | Curva | a curva está atual ou com histórico parcial utilizável |
| 4 | Expectativas | o Focus está atual, ainda que sem revisão relevante |
| 5 | Qualidade dos dados | nenhuma fonte sustenta uma síntese íntegra |

Estados incompletos nunca são promovidos a uma convergência. Depois da escolha,
o Resumo reutiliza o título, a narrativa e as evidências dos motores, elimina
duplicatas e limita a apresentação a duas–quatro provas. Ele não reproduz
limiares, medianas ou regras direcionais dentro da UI.

## Datas e rastreabilidade

As janelas permanecem separadas por fonte porque não precisam coincidir:

- **Focus:** coleta atual e anterior para o mesmo indicador e a mesma
  referência; na convergência, usa a Selic da mesma reunião do Copom.
- **Curva:** data-base atual e quinta observação publicada anterior; D-21
  aparece no detalhe da Curva, quando disponível.
- **Focus × Curva:** exibe as duas datas do Focus e as duas datas da Curva em
  vez de chamar intervalos diferentes simplesmente de “semana”.
- **Radar:** o contexto informa a própria fonte, o horizonte e a confiança do
  cenário; ele não herda a data do Focus ou da Curva.

Uma data ausente permanece ausente. Falha de uma fonte degrada apenas a camada
dependente dela; as demais continuam utilizáveis e o Resumo explicita o limite.

## Cenário mecânico da curva

O cenário parte da fotografia atual do Tesouro Prefixado sem cupom e soma o
mesmo choque, em pontos-base, a todos os vencimentos:

```text
taxa no cenário = taxa observada + choque em bps ÷ 100
```

A interface oferece de −100 a +100 bps, em passos de 25 bps. Como o deslocamento
é uniforme, a inclinação permanece inalterada por construção. A simulação não
muda a fotografia, o cache, as comparações D-5/D-21, o Resumo, o Radar ou a
carteira.

É uma análise de sensibilidade, não uma previsão. Ela não estima chance de
ocorrência, preço, retorno, duration, impostos, custos ou adequação pessoal.
Choques não paralelos e mudanças de inclinação ficam fora da `v2.0`.

## Fontes e papéis

| Camada | Fonte pública | Papel na integração |
|---|---|---|
| Expectativas | Sistema de Expectativas de Mercado, BACEN/Olinda | revisões de Selic, IPCA, câmbio e PIB |
| Curva | Tesouro Transparente, taxas do Tesouro Direto, ODbL 1.0 | taxas observadas dos prefixados sem cupom |
| Contexto monetário | BACEN/PTAX e SGS | contexto externo e séries realizadas |
| Contexto de mercado | EIA via FRED e Binance | Brent e BTC/BRL, sem alterar o veredito |
| Notícias | feeds RSS das fontes identificadas na interface | atenção editorial, nunca evidência numérica |

ANBIMA não é dependência do MVP. A carteira é uma entrada local do usuário, não
uma fonte pública e não participa do Resumo.

## Limites de interpretação

- Expectativa do Focus não é previsão do Banco Central nem dado realizado.
- Taxa de título não é previsão pura da Selic; prêmio de prazo, liquidez, risco
  e condições de mercado também podem movê-la.
- Convergência de direção não prova causa, antecipação ou acurácia.
- Associação macro não implica causalidade e pode mudar entre regimes.
- Manchetes medem contexto editorial, não sentimento ou veracidade.
- Nenhuma camada produz probabilidade calibrada, alvo de preço, ordem de
  compra/venda ou recomendação personalizada.

## Implementação verificável

- `resumo_integrado.py`: prioridade, provas, datas, limites e condições;
- `pagina_resumo.py`: apresentação e divulgação progressiva do método;
- `curva_cenarios.py`: choque paralelo puro e guardrails;
- `pagina_home.py`: jornada Resumo → Expectativas → Curva → Carteira;
- `tests/test_resumo_integrado.py`: prioridade, degradação e datas;
- `tests/test_resumo_ui.py`: evidência, método e separação entre camadas;
- `tests/test_curva_cenarios.py`: cálculo e limites da hipótese.

Os documentos especializados detalham cada motor; este arquivo é o ponto de
entrada canônico para entender como eles formam o FocusLens BR.
