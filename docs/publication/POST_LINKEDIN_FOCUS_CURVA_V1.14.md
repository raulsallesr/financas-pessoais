# Post — Focus × Curva v1.14

## Texto pronto

O mercado está precificando a mesma história que declara no Focus?

Essa foi a pergunta da terceira entrega do FocusLens BR.

Depois de construir um monitor do Boletim Focus e uma leitura da curva
prefixada do Tesouro, conectei os dois em um motor determinístico e explicável.

Na prática, o projeto:

- compara a revisão da Selic para a mesma reunião do Copom;
- calcula a variação mediana D-5 dos mesmos vencimentos prefixados;
- separa ponta curta e longa quando há cobertura suficiente;
- classifica o resultado como alinhado, curva mais pressionada, curva mais
  benigna, sinais mistos ou dados insuficientes;
- mostra “O que prova” e “O que faria mudar” junto do veredito.

Na fotografia desta versão, a expectativa de Selic ficou estável, enquanto a
curva caiu mediana de 24 bps. O estado foi **Curva mais benigna**.

O ponto metodológico mais importante: taxa de título público não é previsão
pura da Selic. Prêmio de prazo, risco, liquidez e janelas diferentes também
importam. Por isso, o app descreve convergência de direção, sem inventar
causalidade.

Stack: Python, Streamlit, BACEN/Focus, Tesouro Transparente, testes unitários e
AppTest. A versão fechou com 160 testes aprovados e layout validado em mobile,
intermediário e desktop.

GitHub: https://github.com/raulsallesr/financas-pessoais

#Python #Streamlit #DataEngineering #Finanças #RendaFixa #OpenData

## Imagens sugeridas

1. `docs/assets/focus-curva-v1.14.png`
2. `docs/assets/arquitetura-focus-curva-v1.14.svg`

## Antes de publicar

- confirmar que o repositório já está público;
- revisar histórico Git, licenças, segredos e dados pessoais;
- trocar o texto da fotografia se a captura ou o cache tiverem sido atualizados.
