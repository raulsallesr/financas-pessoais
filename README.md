# Finanças Pessoais

App pessoal (Streamlit) para aprender e acompanhar mercado financeiro,
começando pelo **Boletim Focus** do Banco Central — a pesquisa semanal de
expectativas de mercado (Selic, IPCA, câmbio, PIB...) publicada toda
segunda-feira.

## O que faz hoje (v1.1)

- Busca Selic, IPCA, câmbio, PIB Total, IGP-M e dívida líquida do setor
  público direto da API pública do BACEN (Sistema de Expectativas de Mercado
  / Olinda), sem precisar de PDF nem chave de acesso.
- Compara a leitura mais recente com a semana anterior.
- Mostra um gráfico de série histórica por indicador (evolução ao longo de
  todas as semanas já salvas no cache local).
- Explica em linguagem simples, com analogias, o que mudou.
- Mostra efeitos historicamente esperados por classe de investimento
  (pós-fixado, prefixado, IPCA+, bolsa, câmbio) — conteúdo educacional, não é
  recomendação de investimento personalizada. IGP-M não tem efeito mapeado de
  propósito (não tem uma relação direta e didaticamente honesta com nenhuma
  das classes atuais).

## Como rodar

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app_financas.py
```

Depois abra a página "Boletim Focus" na barra lateral e clique em
"Atualizar com dados mais recentes".

## Roadmap

- Depois: página de carteira (organizar seus investimentos) e calculadora de
  projeção de rentabilidade (juros compostos, aportes).
- Avaliado e descartado por ora: deploy público (Streamlit Community Cloud).

## Fonte oficial dos dados

BACEN — Sistema de Expectativas de Mercado (Boletim Focus):
https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata
