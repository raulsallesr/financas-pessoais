import streamlit as st

import pagina_curva
from ui_estilos import aplicar_estilos


st.set_page_config(layout="wide")
aplicar_estilos()
pagina_curva.render_secao()
