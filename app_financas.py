"""Entrypoint da plataforma Lastro. Execute com: streamlit run app_financas.py

Módulos: Macro (FocusLens BR) e Ativos B3.
"""

import streamlit as st

from ativos.ui import pagina_ativos, pagina_busca, pagina_busca_fiis, pagina_ficha
from focuslens.ui.pagina_home import render as render_macro

pagina = st.navigation(
    [
        st.Page(render_macro, title="Macro · FocusLens", url_path="macro", default=True),
        st.Page(pagina_ativos.render, title="Ativos B3", url_path="ativos"),
        st.Page(pagina_busca.render, title="Busca avançada", url_path="busca-acoes"),
        st.Page(pagina_busca_fiis.render, title="Busca de FIIs", url_path="busca-fiis"),
        st.Page(pagina_ficha.render, title="Ficha do ativo", url_path="ficha"),
    ],
    position="top",
)
pagina.run()
