"""Composição visual da Curva Tesouro prefixada."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from focuslens.ui.curva_apresentacao import (
    especificacao_grafico_cenario,
    especificacao_grafico,
    formatar_bps,
    formatar_numero,
    linhas_grafico_cenario,
    linhas_grafico,
    linhas_tabela_cenario,
    linhas_tabela,
)
from focuslens.core.curva_cenarios import simular_choque_paralelo
from focuslens.core.curva_data import PontoCurva
from focuslens.adapters.curva_fontes import (
    CURVA_FONTE_URL,
    ErroCacheCurva,
    ErroFonteCurva,
    atualizar_e_obter_curva,
    carregar_cache,
    data_ultima_atualizacao_cache,
)
from focuslens.core.curva_modelo import (
    EstadoCurva,
    LeituraCurva,
    descricao_leitura_curva,
    montar_leitura_curva,
    titulo_leitura_curva,
)
from focuslens.core.focus_atualizacao import deve_verificar_automaticamente


_ESTILO_ESTADO = {
    EstadoCurva.ATUALIZADA: ("check_circle", "green"),
    EstadoCurva.DEFASADA: ("history", "orange"),
    EstadoCurva.PARCIAL: ("pending", "blue"),
    EstadoCurva.INDISPONIVEL: ("cloud_off", "gray"),
}


def _renderizar_cabecalho() -> bool:
    titulo, acoes = st.columns([4, 1], vertical_alignment="bottom")
    with titulo:
        st.caption("FOCUSLENS BR · CURVA TESOURO")
        st.header("Como mudaram as taxas prefixadas")
        st.write(
            "Pontos observados do Tesouro Prefixado contra D-5 e D-21 "
            "sessões disponíveis."
        )
    with acoes:
        atualizar = st.button(
            "Atualizar curva",
            icon=":material/refresh:",
            type="primary",
            width="stretch",
        )
        with st.popover(
            "Como ler",
            icon=":material/info:",
            width="stretch",
        ):
            st.write(
                "Usamos a taxa de compra da manhã: a taxa disponível para "
                "a pessoa física comprar o título. D-5 e D-21 são datas "
                "efetivamente publicadas, não dias inventados."
            )
            st.caption(
                "A linha apenas conecta os pontos observados para facilitar "
                "a leitura; não representa interpolação ou recomendação."
            )
    return atualizar


def _obter_pontos(atualizar: bool) -> list[PontoCurva]:
    try:
        pontos = carregar_cache()
    except ErroCacheCurva:
        pontos = []
        st.warning(
            "O cache local da curva precisa ser reconstruído. O app tentará "
            "buscar uma cópia íntegra no Tesouro Transparente."
        )
    try:
        ultima_verificacao = data_ultima_atualizacao_cache()
    except ErroCacheCurva:
        ultima_verificacao = None

    hoje = date.today()
    atualizar_automaticamente = (
        not atualizar
        and deve_verificar_automaticamente(ultima_verificacao, hoje)
    )
    if atualizar_automaticamente:
        chave = hoje.isoformat()
        if st.session_state.get("curva_auto_tentada_em") == chave:
            return pontos
        st.session_state["curva_auto_tentada_em"] = chave

    if not atualizar and not atualizar_automaticamente:
        return pontos

    mensagem = (
        "Verificando a curva mais recente no Tesouro Transparente..."
        if atualizar_automaticamente
        else "Atualizando a curva do Tesouro Transparente..."
    )
    with st.spinner(mensagem, show_time=True):
        try:
            atualizados = list(atualizar_e_obter_curva())
            st.toast("Curva do Tesouro verificada.", icon=":material/check_circle:")
            return atualizados
        except (ErroFonteCurva, ErroCacheCurva) as erro:
            if pontos:
                st.warning(
                    "O Tesouro Transparente não respondeu agora. Mantivemos "
                    "a última curva salva."
                )
            else:
                st.error(str(erro))
            return pontos


def _renderizar_resumo(leitura: LeituraCurva) -> None:
    icone, cor = _ESTILO_ESTADO[leitura.estado]
    with st.container(border=True, key="curva_resumo"):
        estado, origem = st.columns(
            [1, 3],
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
            if leitura.atual is None:
                st.caption("Tesouro Transparente · CSV público diário")
            else:
                st.caption(
                    "Curva de "
                    f"{leitura.atual.data_referencia.strftime('%d/%m/%Y')} · "
                    f"{len(leitura.atual.pontos)} vencimentos observados"
                )
        st.caption("O QUE MUDOU")
        st.subheader(titulo_leitura_curva(leitura))
        st.write(descricao_leitura_curva(leitura))

        if leitura.atual is None:
            return
        curta = leitura.atual.pontos[0]
        longa = leitura.atual.pontos[-1]
        metricas = st.columns(4, gap="medium")
        with metricas[0]:
            st.metric(
                "Mediana D-5",
                formatar_bps(leitura.movimento_mediano_d5_bps),
                delta=(
                    f"{sum(item.delta_d5_bps is not None for item in leitura.comparacoes)} "
                    "em comum"
                ),
                delta_color="off",
                border=True,
            )
        with metricas[1]:
            st.metric(
                "Ponta curta",
                f"{formatar_numero(curta.taxa_compra)}%",
                delta=f"Vence em {curta.vencimento.year}",
                delta_color="off",
                border=True,
            )
        with metricas[2]:
            st.metric(
                "Ponta longa",
                f"{formatar_numero(longa.taxa_compra)}%",
                delta=f"Vence em {longa.vencimento.year}",
                delta_color="off",
                border=True,
            )
        with metricas[3]:
            st.metric(
                "Inclinação atual",
                formatar_bps(leitura.inclinacao_atual_bps),
                delta="longa menos curta",
                delta_color="off",
                border=True,
            )


def _renderizar_grafico(leitura: LeituraCurva) -> None:
    if leitura.atual is None:
        return
    st.subheader("Curva por vencimento")
    st.caption(
        "Taxa de compra da manhã. Marcadores são observações publicadas; "
        "os segmentos apenas conectam esses pontos."
    )
    linhas = linhas_grafico(leitura)
    dados = pd.DataFrame(linhas)
    especificacao = especificacao_grafico(linhas)
    st.vega_lite_chart(
        dados,
        especificacao,
        width="stretch",
    )


def _renderizar_detalhes(leitura: LeituraCurva) -> None:
    if leitura.atual is None:
        return
    with st.expander(
        "Ver taxas e variações por título",
        icon=":material/table_chart:",
    ):
        st.dataframe(
            pd.DataFrame(linhas_tabela(leitura)),
            hide_index=True,
            width="stretch",
            column_config={
                "Vencimento": st.column_config.DateColumn(
                    "Vencimento", format="DD/MM/YYYY"
                ),
                "Atual (% a.a.)": st.column_config.NumberColumn(
                    "Atual (% a.a.)", format="%.2f"
                ),
                "D-5 (% a.a.)": st.column_config.NumberColumn(
                    "D-5 (% a.a.)", format="%.2f"
                ),
                "D-21 (% a.a.)": st.column_config.NumberColumn(
                    "D-21 (% a.a.)", format="%.2f"
                ),
                "Δ D-5 (bps)": st.column_config.NumberColumn(
                    "Δ D-5 (bps)", format="%+.1f"
                ),
                "Δ D-21 (bps)": st.column_config.NumberColumn(
                    "Δ D-21 (bps)", format="%+.1f"
                ),
            },
        )
        st.caption(
            "D-5 e D-21 usam a quinta e a vigésima primeira observações "
            "anteriores disponíveis. Título ausente numa data permanece vazio."
        )
        st.markdown(f"[Abrir fonte oficial no Tesouro Transparente]({CURVA_FONTE_URL})")


def _renderizar_cenario(leitura: LeituraCurva) -> None:
    if leitura.atual is None:
        return

    st.caption("FOCUSLENS BR · CENÁRIO MECÂNICO")
    st.subheader("E se toda a curva se mover?")
    st.write(
        "Aplique o mesmo choque a todos os pontos observados e compare a "
        "hipótese com a fotografia atual."
    )
    with st.container(border=True, key="curva_cenario"):
        st.badge(
            "Hipótese, não previsão",
            icon=":material/science:",
            color="gray",
        )
        choque_bps = st.slider(
            "Choque paralelo sobre todas as taxas",
            min_value=-100,
            max_value=100,
            value=25,
            step=25,
            format="%d bps",
            help=(
                "Pontos-base medem a variação da taxa: 100 bps equivalem "
                "a 1 ponto percentual."
            ),
            key="choque_paralelo_bps",
        )
        st.caption(
            "Use − para taxas mais baixas e + para taxas mais altas. "
            "O controle não estima chance de ocorrência."
        )

        cenario = simular_choque_paralelo(leitura.atual, choque_bps)
        st.subheader(cenario.titulo)
        st.write(cenario.resumo)

        curto = cenario.pontos[0]
        longo = cenario.pontos[-1]
        if curto == longo:
            st.metric(
                "Taxa no cenário",
                f"{formatar_numero(curto.taxa_cenario)}%",
                delta=formatar_bps(cenario.choque_bps),
                delta_color="off",
                border=True,
            )
        else:
            metricas = st.columns(3, gap="medium")
            with metricas[0]:
                st.metric(
                    "Ponta curta no cenário",
                    f"{formatar_numero(curto.taxa_cenario)}%",
                    delta=formatar_bps(cenario.choque_bps),
                    delta_color="off",
                    border=True,
                )
            with metricas[1]:
                st.metric(
                    "Ponta longa no cenário",
                    f"{formatar_numero(longo.taxa_cenario)}%",
                    delta=formatar_bps(cenario.choque_bps),
                    delta_color="off",
                    border=True,
                )
            with metricas[2]:
                st.metric(
                    "Inclinação no cenário",
                    formatar_bps(cenario.inclinacao_cenario_bps),
                    delta="inalterada por construção",
                    delta_color="off",
                    border=True,
                )

        linhas = linhas_grafico_cenario(cenario)
        st.vega_lite_chart(
            pd.DataFrame(linhas),
            especificacao_grafico_cenario(linhas),
            width="stretch",
        )

        with st.expander(
            "Ver taxas simuladas e limites",
            icon=":material/rule:",
        ):
            st.dataframe(
                pd.DataFrame(linhas_tabela_cenario(cenario)),
                hide_index=True,
                width="stretch",
                column_config={
                    "Vencimento": st.column_config.DateColumn(
                        "Vencimento", format="DD/MM/YYYY"
                    ),
                    "Observada (% a.a.)": st.column_config.NumberColumn(
                        "Observada (% a.a.)", format="%.2f"
                    ),
                    "Cenário (% a.a.)": st.column_config.NumberColumn(
                        "Cenário (% a.a.)", format="%.2f"
                    ),
                    "Choque (bps)": st.column_config.NumberColumn(
                        "Choque (bps)", format="%+.0f"
                    ),
                },
            )
            st.markdown("**Limites deste cenário**")
            for limite in cenario.limites:
                st.markdown(f"- {limite}")


def render_secao() -> None:
    atualizar = _renderizar_cabecalho()
    pontos = _obter_pontos(atualizar)
    leitura = montar_leitura_curva(pontos, date.today())
    _renderizar_resumo(leitura)
    _renderizar_grafico(leitura)
    _renderizar_cenario(leitura)
    _renderizar_detalhes(leitura)
    st.caption(
        "Leitura educacional de dados públicos. Taxas de títulos também "
        "refletem prêmio de prazo, liquidez e condições de mercado."
    )
