"""Adaptação e apresentação do Resumo integrado do FocusLens BR."""

from __future__ import annotations

from datetime import date

import streamlit as st

from focuslens.adapters.curva_fontes import (
    ErroCacheCurva,
)
from focuslens.adapters.curva_fontes import (
    carregar_cache as carregar_cache_curva,
)
from focuslens.adapters.focus_leitura import (
    ErroCacheFocus,
)
from focuslens.adapters.focus_leitura import (
    carregar_cache as carregar_cache_focus,
)
from focuslens.core.convergencia_modelo import montar_leitura_convergencia
from focuslens.core.curva_modelo import montar_leitura_curva
from focuslens.core.focus_data import montar_comparativos
from focuslens.core.focus_semanal import montar_resumo_semanal
from focuslens.core.macro_modelo import CenarioMacro
from focuslens.core.resumo_integrado import (
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

_EXPLICACAO_PRIORIDADE = {
    PrioridadeResumo.FOCUS_CURVA: (
        "Focus × Curva lidera porque as duas fontes têm janelas "
        "comparáveis e sustentam uma leitura conjunta."
    ),
    PrioridadeResumo.EXPECTATIVAS: (
        "Expectativas lideram quando a convergência ainda não é comparável, "
        "mas o Focus permanece atual e informativo."
    ),
    PrioridadeResumo.CURVA: (
        "A Curva lidera quando ela permanece atual e o Focus não sustenta "
        "uma convergência comparável."
    ),
    PrioridadeResumo.QUALIDADE_DOS_DADOS: (
        "Qualidade dos dados lidera quando as fontes ainda não oferecem "
        "evidência mínima para uma síntese íntegra."
    ),
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


def _renderizar_metodologia(resumo: ResumoIntegrado) -> None:
    with st.expander(
        "Como o FocusLens BR chega a esta leitura",
        icon=":material/account_tree:",
    ):
        st.markdown(f"**Por que {resumo.prioridade.value} lidera**")
        st.write(_EXPLICACAO_PRIORIDADE[resumo.prioridade])
        st.markdown("**O que cada camada pode afirmar**")
        st.markdown(
            "- O veredito e as provas vêm dos motores de Focus, Curva e "
            "Focus × Curva; o Resumo apenas escolhe a melhor leitura "
            "disponível.\n"
            "- As datas acima são as janelas efetivamente usadas por cada "
            "fonte, sem esconder intervalos diferentes sob o rótulo "
            "‘semana’.\n"
            "- O choque paralelo é uma hipótese mecânica separada: não "
            "altera o veredito, o Radar nem a carteira.\n"
            "- Radar e notícias oferecem contexto; dados pessoais da "
            "carteira ficam na sessão e não entram no cálculo público."
        )
        st.caption(
            "Método determinístico e educacional. Associação entre sinais "
            "não prova causa, probabilidade ou retorno futuro."
        )


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

        _renderizar_metodologia(resumo)


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
