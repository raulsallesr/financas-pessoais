"""Adaptação e apresentação do Resumo integrado do FocusLens BR."""

from __future__ import annotations

from datetime import date

import streamlit as st

from convergencia_modelo import montar_leitura_convergencia
from curva_fontes import (
    ErroCacheCurva,
    carregar_cache as carregar_cache_curva,
)
from curva_modelo import montar_leitura_curva
from focus_data import montar_comparativos
from focus_leitura import (
    ErroCacheFocus,
    carregar_cache as carregar_cache_focus,
)
from focus_semanal import montar_resumo_semanal
from macro_modelo import CenarioMacro
from resumo_integrado import (
    DatasFonteResumo,
    PrioridadeResumo,
    ResumoIntegrado,
    montar_resumo_integrado,
    selecionar_contexto_radar,
)


_ESTILO_PRIORIDADE = {
    PrioridadeResumo.FOCUS_CURVA: ("compare_arrows", "blue"),
    PrioridadeResumo.EXPECTATIVAS: ("query_stats", "green"),
    PrioridadeResumo.CURVA: ("show_chart", "orange"),
    PrioridadeResumo.QUALIDADE_DOS_DADOS: ("data_alert", "gray"),
}


def carregar_resumo(hoje: date | None = None) -> ResumoIntegrado:
    """Lê cada cache de forma independente e compõe os motores existentes."""
    data_referencia = hoje or date.today()
    try:
        historico_focus = carregar_cache_focus()
    except ErroCacheFocus:
        historico_focus = []
    try:
        pontos_curva = carregar_cache_curva()
    except ErroCacheCurva:
        pontos_curva = []

    comparativos = montar_comparativos(historico_focus)
    focus = montar_resumo_semanal(comparativos, data_referencia)
    curva = montar_leitura_curva(pontos_curva, data_referencia)
    convergencia = montar_leitura_convergencia(
        comparativos,
        curva,
        data_referencia,
    )
    return montar_resumo_integrado(focus, curva, convergencia)


def _formatar_datas(item: DatasFonteResumo) -> str:
    datas = item.datas
    if not datas:
        return f"{item.fonte}: sem data disponível"
    if len(datas) == 1:
        periodo = datas[0].strftime("%d/%m/%Y")
    elif len(datas) == 2:
        periodo = " e ".join(data.strftime("%d/%m/%Y") for data in datas)
    else:
        periodo = (
            f"{datas[0].strftime('%d/%m/%Y')}–"
            f"{datas[-1].strftime('%d/%m/%Y')} ({len(datas)} coletas)"
        )
    return f"{item.fonte}: {periodo}"


def _renderizar_lista(titulo: str, itens: tuple[str, ...]) -> None:
    st.markdown(f"**{titulo}**")
    st.write(itens[0] if itens else "Nenhum ponto adicional neste estado.")


def render_secao(resumo: ResumoIntegrado) -> None:
    st.caption("FOCUSLENS BR · RESUMO")
    st.header("O que merece atenção agora")
    st.write(
        "Uma leitura integrada das expectativas e da curva, com a evidência "
        "e os limites no mesmo lugar."
    )

    icone, cor = _ESTILO_PRIORIDADE[resumo.prioridade]
    with st.container(border=True, key="resumo_integrado"):
        st.badge(
            resumo.prioridade.value,
            icon=f":material/{icone}:",
            color=cor,
        )
        st.caption("LEITURA PRINCIPAL")
        st.subheader(resumo.veredito)
        for prova in resumo.provas:
            st.markdown(f"- **{prova.origem}:** {prova.descricao}")
        st.caption(
            "Datas das fontes · "
            + " · ".join(_formatar_datas(item) for item in resumo.datas_fontes)
        )

        limite, mudanca = st.columns(2, gap="large")
        with limite:
            _renderizar_lista("Limite desta leitura", resumo.limites)
        with mudanca:
            _renderizar_lista(
                "O que faria a leitura mudar",
                resumo.condicoes_de_mudanca,
            )

        outros_limites = resumo.limites[1:]
        outras_condicoes = resumo.condicoes_de_mudanca[1:]
        if outros_limites or outras_condicoes:
            with st.expander(
                "Ver demais limites e condições",
                icon=":material/rule:",
            ):
                if outros_limites:
                    st.markdown("**Outros limites**")
                    for item in outros_limites:
                        st.markdown(f"- {item}")
                if outras_condicoes:
                    st.markdown("**Outras condições de mudança**")
                    for item in outras_condicoes:
                        st.markdown(f"- {item}")


def renderizar_contexto_radar(cenario: CenarioMacro | None) -> None:
    contexto = selecionar_contexto_radar(cenario)
    if contexto is None:
        return
    with st.container(border=True, key="resumo_contexto_radar"):
        st.caption("CONTEXTO EXTERNO QUE COMPLEMENTA A LEITURA")
        st.markdown(f"**{contexto.titulo}**")
        st.write(contexto.evidencia)
        st.caption(
            f"{contexto.fonte} · Horizonte: {contexto.horizonte} · "
            f"Confiança do cenário: {contexto.confianca}"
        )
