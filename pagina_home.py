"""Composição da experiência única de Finanças Pessoais."""

from __future__ import annotations

from datetime import date

import streamlit as st

import pagina_carteira
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
        st.caption("FINANÇAS PESSOAIS")
        st.header("Navegação")
        st.markdown(
            """
            <nav class="fp-section-nav" aria-label="Seções desta página">
              <a href="#visao-geral">
                <span class="material-symbols-rounded">home</span>
                Visão geral
              </a>
              <a href="#boletim-focus">
                <span class="material-symbols-rounded">query_stats</span>
                Boletim Focus
              </a>
              <a href="#radar-macro">
                <span class="material-symbols-rounded">monitoring</span>
                Radar Macro
              </a>
              <a href="#minha-carteira">
                <span class="material-symbols-rounded">account_balance_wallet</span>
                Minha carteira
              </a>
            </nav>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        if ultima_coleta is not None:
            st.caption(
                f"{total_indicadores} indicadores do Focus · última coleta "
                f"em {ultima_coleta.strftime('%d/%m/%Y')}."
            )
        else:
            st.caption(
                "O Focus será consultado quando houver conexão disponível."
            )
        st.caption(
            "Use os links acima para ir direto ao tópico sem trocar de página."
        )


def _renderizar_visao_geral(
    total_indicadores: int,
    ultima_coleta: date | None,
) -> None:
    atualidade = avaliar_atualidade(ultima_coleta, date.today())
    st.caption("VISÃO GERAL")
    st.title("Finanças Pessoais, sem ruído")
    st.write(
        "Expectativas, mercados e carteira reunidos em uma única leitura. "
        "Role a página ou use o menu à esquerda para ir direto ao tópico."
    )

    with st.container(border=True, key="home_overview"):
        st.badge(
            atualidade.rotulo,
            icon=f":material/{atualidade.icone}:",
            color=atualidade.cor,
        )
        st.subheader("Do cenário à sua carteira")
        st.write(
            "Primeiro, veja o que o mercado espera no Boletim Focus. Depois, "
            "compare dólar, petróleo, Bitcoin, CDI e Selic no ano. Por fim, "
            "adicione suas posições para enxergar alocação, resultado e "
            "exposição ao cenário."
        )
        if ultima_coleta is not None:
            st.caption(
                f"{total_indicadores} indicadores acompanhados · dados do "
                f"Focus até {ultima_coleta.strftime('%d/%m/%Y')}."
            )

    etapas = st.columns(3, gap="medium")
    conteudos = (
        (
            "1 · Expectativas",
            "O Focus mostra como Selic, inflação, câmbio e atividade estão "
            "mudando na visão do mercado.",
        ),
        (
            "2 · Mercados",
            "O Radar organiza os sinais e compara cinco referências desde o "
            "início do ano em uma base comum.",
        ),
        (
            "3 · Carteira",
            "Seus valores ficam apenas na sessão e são cruzados com o "
            "cenário de forma descritiva.",
        ),
    )
    for coluna, (titulo, texto) in zip(etapas, conteudos):
        with coluna:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.write(texto)


def render() -> None:
    st.set_page_config(
        page_title="Finanças Pessoais",
        page_icon=":material/account_balance_wallet:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    aplicar_estilos()
    total_indicadores, ultima_coleta = _carregar_status()
    _renderizar_menu(total_indicadores, ultima_coleta)

    _ancora("visao-geral")
    _renderizar_visao_geral(total_indicadores, ultima_coleta)

    st.divider()
    _ancora("boletim-focus")
    pagina_focus.render_secao()

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
