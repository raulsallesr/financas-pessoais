"""Finanças Pessoais -- home. Ponto de entrada: streamlit run app_financas.py"""

import streamlit as st

st.set_page_config(page_title="Finanças Pessoais", page_icon="💡", layout="wide")

st.title("Finanças Pessoais")
st.caption(
    "Um app pessoal para entender mercado financeiro e organizar a vida "
    "financeira, começando pelo Boletim Focus do BACEN."
)

st.markdown(
    """
### O que tem aqui hoje
- **Boletim Focus** -- abra a página na barra lateral para ver o que mudou
  esta semana nas expectativas de Selic, IPCA e câmbio, explicado em
  linguagem simples.

### O que vem por aí
- Organização da sua carteira de investimentos
- Calculadora de projeção de rentabilidade (juros compostos, aportes)

---
*Conteúdo educacional. Nada aqui é recomendação de investimento
personalizada.*
"""
)
