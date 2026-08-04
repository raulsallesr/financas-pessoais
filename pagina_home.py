"""Composição visual da home de Finanças Pessoais."""

from __future__ import annotations

from datetime import date

import streamlit as st

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


def render() -> None:
    st.set_page_config(
        page_title="Finanças Pessoais",
        page_icon=":material/account_balance_wallet:",
        layout="wide",
    )
    aplicar_estilos()
    total_indicadores, ultima_coleta = _carregar_status()
    atualidade = avaliar_atualidade(ultima_coleta, date.today())

    st.caption("VISÃO GERAL")
    st.title("Finanças Pessoais, sem ruído")
    st.write(
        "Comece pelo cenário econômico. O app verifica os dados sozinho, "
        "explica o que mudou e mantém as fontes sempre visíveis."
    )

    with st.container(border=True, key="home_feature_focus"):
        conteudo, acao = st.columns(
            [3, 1],
            gap="large",
            vertical_alignment="center",
        )
        with conteudo:
            st.badge(
                atualidade.rotulo,
                icon=f":material/{atualidade.icone}:",
                color=atualidade.cor,
            )
            st.subheader("Panorama do Boletim Focus")
            st.write(
                "Selic, inflação e câmbio em primeiro plano; impactos, "
                "histórico e três manchetes relevantes nas camadas seguintes."
            )
            if ultima_coleta is not None:
                st.caption(
                    f"{total_indicadores} indicadores · última coleta em "
                    f"{ultima_coleta.strftime('%d/%m/%Y')} · atualização "
                    "automática ao abrir em dias úteis."
                )
            else:
                st.caption(
                    "A primeira abertura do panorama buscará o histórico "
                    "recente automaticamente."
                )
        with acao:
            st.page_link(
                "pages/1_Boletim_Focus.py",
                label="Abrir panorama",
                icon=":material/arrow_forward:",
                use_container_width=True,
            )

    st.subheader("Uma rotina simples")
    etapas = st.columns(3, gap="medium")
    conteudos = (
        (
            "1 · Verificar",
            "O app consulta o BACEN uma vez por dia útil e preserva o cache "
            "se a rede falhar.",
        ),
        (
            "2 · Entender",
            "A leitura principal vem antes dos detalhes e deixa explícito o "
            "intervalo comparado.",
        ),
        (
            "3 · Explorar",
            "Impactos, gráfico e notícias ficam disponíveis sem transformar "
            "cenário em recomendação.",
        ),
    )
    for coluna, (titulo, texto) in zip(etapas, conteudos):
        with coluna:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.write(texto)

    with st.expander(
        "Próximos módulos",
        icon=":material/route:",
    ):
        st.markdown(
            """
            - **Carteira:** organizar posições e concentração.
            - **Simulador:** comparar aportes e juros compostos.
            - **Alertas úteis:** avisar apenas mudanças relevantes, sem ruído.
            """
        )

    st.caption(
        "Conteúdo educacional. Nenhuma informação exibida é orientação de "
        "investimento personalizada."
    )
