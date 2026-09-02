# Post — FocusLens BR v2.0

## Texto pronto

O que merece atenção agora: as expectativas do Focus, a curva de juros ou a
qualidade dos dados?

Essa pergunta guiou a `v2.0` do FocusLens BR, um produto educacional que
transforma dados públicos do mercado brasileiro em uma leitura rastreável —
com números, datas, fontes e limites perto de cada conclusão.

Eu já havia construído três entregas independentes:

- um monitor das revisões do Boletim Focus;
- uma leitura da curva prefixada do Tesouro;
- um motor determinístico de convergência Focus × Curva.

Na `v2.0`, conectei os três contratos em uma única jornada:

**Resumo → Expectativas → Curva → Carteira**

O Resumo não inventa uma quarta fórmula. Ele escolhe a leitura mais íntegra já
produzida pelos motores, preserva as janelas reais de cada fonte e mostra de
duas a quatro provas, o principal limite e a condição que faria o veredito
mudar.

A Curva também ganhou um cenário de choque paralelo. É uma análise de
sensibilidade explícita, não uma previsão: todas as taxas recebem o mesmo
deslocamento, sem estimar probabilidade, preço de título ou retorno de carteira.

Algumas decisões de engenharia que considero centrais:

- motores puros separados de rede, cache e Streamlit;
- falha de uma fonte degrada somente a camada dependente dela;
- carteira e planilha B3 ficam apenas na sessão;
- notícias e Radar entram como contexto, nunca no cálculo de convergência;
- metodologia e guardrails são parte do produto, não uma nota de rodapé.

O release candidate fechou com **185 testes**, validação real em mobile,
tablet, desktop e paisagem, além de auditoria de segredos, dados pessoais,
licenças, dependências e histórico Git.

Stack: Python, Streamlit, Pandas, BACEN/Focus, Tesouro Transparente, SGS e APIs
públicas de mercado.

GitHub: https://github.com/raulsallesr/financas-pessoais

#Python #Streamlit #DataEngineering #Finanças #RendaFixa #OpenData #Portfolio

## Imagens sugeridas

1. `docs/assets/focuslens-br-v2.0.png`
2. `docs/assets/arquitetura-focuslens-v2.0.svg`

## Antes de publicar

- escolher e registrar a licença do código;
- aceitar ou sanear o e-mail não mascarado dos commits históricos;
- criar a tag/release `v2.0` e tornar o repositório público;
- abrir o link em sessão anônima e confirmar imagens, README e release;
- publicar somente depois de trocar “release candidate” por “release” se a
  abertura pública já tiver sido concluída.
