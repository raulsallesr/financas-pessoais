"""Composição visual da leitura Focus × Curva."""

from __future__ import annotations

from datetime import date

import streamlit as st

from focuslens.ui.convergencia_apresentacao import (
    detalhe_curva,
    detalhe_focus,
    detalhe_ponta,
    valor_curva,
    valor_focus,
    valor_ponta,
)
from focuslens.core.convergencia_modelo import (
    EstadoConvergencia,
    LeituraConvergencia,
    montar_leitura_convergencia,
)
from focuslens.adapters.curva_fontes import (
    CURVA_FONTE_URL,
    ErroCacheCurva,
    carregar_cache as carregar_curva,
)
from focuslens.core.curva_modelo import montar_leitura_curva
from focuslens.core.focus_data import montar_comparativos
from focuslens.adapters.focus_leitura import (
    ErroCacheFocus,
    carregar_cache as carregar_focus,
)


FOCUS_FONTE_URL = "https://www.bcb.gov.br/controleinflacao/expectativasmercado"

_ESTILO_ESTADO = {
    EstadoConvergencia.ALINHADOS: ("compare_arrows", "green"),
    EstadoConvergencia.CURVA_MAIS_PRESSIONADA: ("trending_up", "orange"),
    EstadoConvergencia.CURVA_MAIS_BENIGNA: ("trending_down", "blue"),
    EstadoConvergencia.SINAIS_MISTOS: ("swap_vert", "orange"),
    EstadoConvergencia.DADOS_INSUFICIENTES: ("pending", "gray"),
}


def _carregar_leitura(hoje: date) -> LeituraConvergencia:
    try:
        historico_focus = carregar_focus()
    except ErroCacheFocus:
        historico_focus = []
    try:
        pontos_curva = carregar_curva()
    except ErroCacheCurva:
        pontos_curva = []
    comparativos = montar_comparativos(historico_focus)
    curva = montar_leitura_curva(pontos_curva, hoje)
    return montar_leitura_convergencia(comparativos, curva, hoje)


def _renderizar_cabecalho() -> None:
    st.caption("FOCUSLENS BR · EXPECTATIVA × PRECIFICAÇÃO")
    st.header("Focus e curva contam a mesma história?")
    st.write(
        "Comparamos a revisão da Selic para a mesma reunião com o movimento "
        "D‑5 dos mesmos vencimentos prefixados."
    )


def _renderizar_resumo(leitura: LeituraConvergencia) -> None:
    icone, cor = _ESTILO_ESTADO[leitura.estado]
    with st.container(border=True, key="focus_curva_resumo"):
        estado, origem = st.columns(
            [2, 3],
            gap="medium",
            vertical_alignment="center",
        )
        with estado:
            st.badge(
                leitura.estado.value,
                icon=f":material/{icone}:",
                color=cor,
            )
        with origem:
            st.caption("BACEN Focus · Tesouro Transparente · comparação D‑5")

        st.caption("VEREDITO")
        st.subheader(leitura.titulo)
        st.write(leitura.resumo)

        metricas = st.columns(4, gap="medium")
        configuracoes = (
            (
                "Focus · Selic",
                valor_focus(leitura.focus),
                detalhe_focus(leitura.focus),
            ),
            (
                "Curva geral",
                valor_curva(leitura.curva),
                detalhe_curva(leitura.curva),
            ),
            (
                "Ponta curta",
                valor_ponta(leitura.ponta_curta),
                detalhe_ponta(leitura.ponta_curta),
            ),
            (
                "Ponta longa",
                valor_ponta(leitura.ponta_longa),
                detalhe_ponta(leitura.ponta_longa),
            ),
        )
        for coluna, (rotulo, valor, detalhe) in zip(metricas, configuracoes):
            with coluna:
                st.metric(
                    rotulo,
                    valor,
                    delta=detalhe,
                    delta_color="off",
                    border=True,
                )


def _renderizar_evidencias(leitura: LeituraConvergencia) -> None:
    prova, mudanca = st.columns(2, gap="medium")
    with prova:
        with st.container(border=True, key="focus_curva_prova"):
            st.subheader("O que prova", divider=False)
            for evidencia in leitura.evidencias:
                st.markdown(f"- {evidencia}")
    with mudanca:
        with st.container(border=True, key="focus_curva_mudanca"):
            st.subheader("O que faria mudar", divider=False)
            for condicao in leitura.condicoes_de_mudanca:
                st.markdown(f"- {condicao}")


def _renderizar_metodo(leitura: LeituraConvergencia) -> None:
    with st.expander(
        "Método, fontes e limites",
        icon=":material/rule:",
    ):
        st.markdown(
            """
            1. O **Focus** usa a última mediana da Selic contra a coleta
               anterior para a mesma reunião do Copom.
            2. A **curva** usa a mediana das variações D‑5 dos vencimentos
               presentes nas duas datas.
            3. A ponta curta usa os vencimentos comparáveis mais próximos; a
               longa, os mais distantes. Esse recorte aparece com quatro ou
               mais pontos.
            4. As direções são ordenadas como mais benigna, estável e mais
               pressionada. Pontas opostas permanecem como sinal misto.
            """
        )
        for ressalva in leitura.ressalvas:
            st.warning(ressalva, icon=":material/info:")
        st.markdown(
            f"[Fonte oficial do Focus]({FOCUS_FONTE_URL}) · "
            f"[Fonte oficial da Curva Tesouro]({CURVA_FONTE_URL})"
        )


def render_secao() -> None:
    _renderizar_cabecalho()
    leitura = _carregar_leitura(date.today())
    _renderizar_resumo(leitura)
    _renderizar_evidencias(leitura)
    _renderizar_metodo(leitura)
    st.caption(
        "Leitura educacional e direcional. O resultado descreve convergência "
        "entre duas janelas observadas; não prova causalidade nem recomenda "
        "operação."
    )
