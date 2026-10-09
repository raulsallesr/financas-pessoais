"""Entrypoint da plataforma Lastro. Execute com: streamlit run app_financas.py

Módulos: Macro (FocusLens BR) e Ativos B3.
"""

import streamlit as st

from ativos.ui import pagina_ativos, pagina_busca
from focuslens.ui.pagina_home import render as render_macro

pagina = st.navigation(
    [
        st.Page(render_macro, title="Macro · FocusLens", url_path="macro", default=True),
        st.Page(pagina_ativos.render, title="Ativos B3", url_path="ativos"),
        st.Page(pagina_busca.render, title="Busca avançada", url_path="busca-acoes"),
    ],
    position="top",
)
pagina.run()
