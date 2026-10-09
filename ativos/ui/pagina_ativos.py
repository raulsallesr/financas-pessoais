"""Página inicial do módulo Ativos — estado da construção, sem dado ainda."""

import streamlit as st

from focuslens.ui.ui_estilos import aplicar_estilos

ETAPAS = (
    ("Fase 0", "Fundação e cobertura das fontes oficiais", "concluída"),
    ("Fase 1", "Base de dados point-in-time (CVM + COTAHIST)", "próxima"),
    ("Fase 2", "Métricas, ficha do ativo e screener (ações e FIIs)", "planejada"),
    ("Fase 3", "ETFs por exposição, custo e liquidez", "planejada"),
    ("Fase 4", "Valor intrínseco estimado em faixa multi-modelo", "planejada"),
    ("Fase 5", "Score Lastro e laboratório de backtest", "planejada"),
    ("Fase 6", "Risco, otimizador de carteira e raio-x", "planejada"),
)

AVISO = (
    "Ferramenta de uso pessoal com metodologia aberta. Scores, faixas de valor e "
    "carteiras simuladas são cálculos quantitativos para estudo, sem caráter de "
    "aconselhamento."
)


def render() -> None:
    st.set_page_config(
        page_title="Ativos · Lastro",
        page_icon=":material/query_stats:",
        layout="wide",
    )
    aplicar_estilos()
    st.title("Ativos B3")
    st.write(
        "Métricas, filtros, score e carteira para ações, FIIs e ETFs, "
        "calculados a partir de fontes oficiais e gratuitas."
    )
    st.caption(AVISO)
    st.dataframe(
        [{"Fase": fase, "Entrega": entrega, "Situação": situacao}
         for fase, entrega, situacao in ETAPAS],
        hide_index=True,
        width="stretch",
    )
