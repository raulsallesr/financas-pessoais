"""Composição da experiência única de Finanças Pessoais."""

from __future__ import annotations

import streamlit as st

import pagina_carteira
import pagina_curva
import pagina_focus
import pagina_macro
import pagina_resumo
from ui_estilos import aplicar_estilos


def _ancora(identificador: str) -> None:
    st.markdown(
        f'<span id="{identificador}" class="fp-section-anchor"></span>',
        unsafe_allow_html=True,
    )


def _renderizar_menu() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="fp-sidebar-brand">
              <span class="fp-sidebar-brand__mark" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round">
                  <path d="M4 17.5 9 12l3.2 3.2L20 7.5"/>
                  <path d="M15.5 7.5H20V12"/>
                </svg>
              </span>
              <span class="fp-sidebar-brand__text">
                <span>FINANÇAS PESSOAIS</span>
                <strong>FocusLens BR</strong>
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <nav class="fp-section-nav" aria-label="Seções desta página">
              <a href="#resumo">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <path d="M4 19.5V4.5"/>
                  <path d="M4 19.5h16"/>
                  <path d="m7 15 4-4 3 3 5-7"/>
                </svg>
                Resumo
              </a>
              <a href="#expectativas">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <path d="M4 19.5V4.5"/>
                  <path d="M4 19.5h16"/>
                  <path d="M7 15.5c3-1 4-6 7-6s3 2 5 2"/>
                  <circle cx="7" cy="15.5" r="1"/>
                  <circle cx="14" cy="9.5" r="1"/>
                  <circle cx="19" cy="11.5" r="1"/>
                </svg>
                Expectativas
              </a>
              <a href="#curva">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <path d="M5 7h12"/>
                  <path d="m14 4 3 3-3 3"/>
                  <path d="M19 17H7"/>
                  <path d="m10 14-3 3 3 3"/>
                </svg>
                Curva
              </a>
              <a href="#carteira">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <path d="M4 6.5h14.5a1.5 1.5 0 0 1 1.5 1.5v10.5H5.5A2.5 2.5 0 0 1 3 16V7.5A2.5 2.5 0 0 1 5.5 5H17"/>
                  <path d="M15 11h5v4h-5a2 2 0 0 1 0-4Z"/>
                </svg>
                Carteira
              </a>
            </nav>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Dados públicos · BACEN e Tesouro Transparente")


def _renderizar_visao_geral() -> None:
    st.caption("FINANÇAS PESSOAIS · DADOS PÚBLICOS BR")
    st.title("FocusLens BR")
    st.write(
        "Expectativas, curva e carteira em uma sequência única, com prova, "
        "data e limite perto de cada leitura."
    )


def render() -> None:
    st.set_page_config(
        page_title="FocusLens BR",
        page_icon=":material/account_balance_wallet:",
        layout="wide",
        initial_sidebar_state="auto",
    )
    aplicar_estilos()
    st.markdown(
        '<a class="fp-skip-link" href="#resumo">'
        "Pular para o conteúdo</a>",
        unsafe_allow_html=True,
    )
    _renderizar_menu()

    _renderizar_visao_geral()

    st.divider()
    _ancora("resumo")
    resumo = pagina_resumo.carregar_resumo()
    pagina_resumo.render_secao(resumo)
    with st.spinner("Atualizando o contexto de mercado...", show_time=True):
        dados_radar = pagina_macro.carregar_dados_radar()
    pagina_resumo.renderizar_contexto_radar(dados_radar.cenario)

    st.divider()
    _ancora("expectativas")
    pagina_focus.render_secao()

    st.divider()
    _ancora("curva")
    pagina_curva.render_secao()

    st.divider()
    _ancora("carteira")
    pagina_carteira.render(dados_radar.cenario, list(dados_radar.series))

    st.divider()
    st.caption(
        "Conteúdo educacional baseado em fontes públicas. Nenhuma informação "
        "exibida constitui orientação de investimento personalizada."
    )
