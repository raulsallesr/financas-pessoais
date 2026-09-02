import streamlit as st

from focuslens.ui import pagina_curva
from focuslens.ui.ui_estilos import aplicar_estilos


st.set_page_config(layout="wide")
aplicar_estilos()
pagina_curva.render_secao()
