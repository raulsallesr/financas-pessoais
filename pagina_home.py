"""Composição da experiência única de Finanças Pessoais."""

from __future__ import annotations

from datetime import date

import streamlit as st

import pagina_carteira
import pagina_convergencia
import pagina_curva
import pagina_focus
import pagina_macro
from focus_atualizacao import avaliar_atualidade
from focus_data import leitura_mais_recente
from focus_leitura import ErroCacheFocus, carregar_cache
from ui_estilos import aplicar_estilos


def _carregar_status() -> tuple[int, date | None]:
    try:
        historico = carregar_cache()
    except ErroCacheFocus:
        return 0, None
    ultima = leitura_mais_recente(historico)
    indicadores = {leitura.indicador for leitura in historico}
    return len(indicadores), ultima.data_coleta if ultima else None


def _ancora(identificador: str) -> None:
    st.markdown(
        f'<span id="{identificador}" class="fp-section-anchor"></span>',
        unsafe_allow_html=True,
    )


def _renderizar_menu(
    total_indicadores: int,
    ultima_coleta: date | None,
) -> None:
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
                <span>PAINEL PESSOAL</span>
                <strong>Finanças</strong>
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <nav class="fp-section-nav" aria-label="Seções desta página">
              <a href="#boletim-focus">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <path d="M4 19.5V4.5"/>
                  <path d="M4 19.5h16"/>
                  <path d="m7 15 4-4 3 3 5-7"/>
                </svg>
                Boletim Focus
              </a>
              <a href="#curva-tesouro">
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
                Curva Tesouro
              </a>
              <a href="#focus-curva">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <path d="M5 7h12"/>
                  <path d="m14 4 3 3-3 3"/>
                  <path d="M19 17H7"/>
                  <path d="m10 14-3 3 3 3"/>
                </svg>
                Focus × Curva
              </a>
              <a href="#radar-macro">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="8.5"/>
                  <circle cx="12" cy="12" r="3.5"/>
                  <path d="M12 3.5V1.8M20.5 12h1.7M12 20.5v1.7M3.5 12H1.8"/>
                </svg>
                Radar Macro
              </a>
              <a href="#minha-carteira">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <path d="M4 6.5h14.5a1.5 1.5 0 0 1 1.5 1.5v10.5H5.5A2.5 2.5 0 0 1 3 16V7.5A2.5 2.5 0 0 1 5.5 5H17"/>
                  <path d="M15 11h5v4h-5a2 2 0 0 1 0-4Z"/>
                </svg>
                Minha carteira
              </a>
            </nav>
            """,
            unsafe_allow_html=True,
        )
        if ultima_coleta is not None:
            st.caption(
                f"Focus · {total_indicadores} indicadores · "
                f"{ultima_coleta.strftime('%d/%m/%Y')}"
            )
        else:
            st.caption("Focus aguardando a primeira coleta.")


def _renderizar_visao_geral(ultima_coleta: date | None) -> None:
    atualidade = avaliar_atualidade(ultima_coleta, date.today())
    introducao, status = st.columns(
        [4, 1], gap="large", vertical_alignment="bottom"
    )
    with introducao:
        st.caption("PAINEL FINANCEIRO PESSOAL")
        st.title("Finanças pessoais")
        st.write("Expectativas, curva, mercados e carteira em uma leitura só.")
    with status:
        st.badge(
            atualidade.rotulo,
            icon=f":material/{atualidade.icone}:",
            color=atualidade.cor,
        )
        if ultima_coleta is not None:
            st.caption(
                f"Focus em {ultima_coleta.strftime('%d/%m/%Y')}"
            )


def render() -> None:
    st.set_page_config(
        page_title="Finanças Pessoais",
        page_icon=":material/account_balance_wallet:",
        layout="wide",
        initial_sidebar_state="auto",
    )
    aplicar_estilos()
    st.markdown(
        '<a class="fp-skip-link" href="#boletim-focus">'
        "Pular para o conteúdo</a>",
        unsafe_allow_html=True,
    )
    total_indicadores, ultima_coleta = _carregar_status()
    _renderizar_menu(total_indicadores, ultima_coleta)

    _renderizar_visao_geral(ultima_coleta)

    st.divider()
    _ancora("boletim-focus")
    pagina_focus.render_secao()

    st.divider()
    _ancora("curva-tesouro")
    pagina_curva.render_secao()

    st.divider()
    _ancora("focus-curva")
    pagina_convergencia.render_secao()

    st.divider()
    _ancora("radar-macro")
    cenario, series = pagina_macro.render_secao()

    st.divider()
    _ancora("minha-carteira")
    pagina_carteira.render(cenario, series)

    st.divider()
    st.caption(
        "Conteúdo educacional baseado em fontes públicas. Nenhuma informação "
        "exibida constitui orientação de investimento personalizada."
    )
