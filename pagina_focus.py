"""Composição visual da página do Boletim Focus."""

from __future__ import annotations

import re
from datetime import date

import pandas as pd
import streamlit as st

from focus_atualizacao import (
    avaliar_atualidade,
    deve_verificar_automaticamente,
)
from focus_apresentacao import (
    INDICADORES_PRIORITARIOS,
    escolher_destaque,
    formatar_delta,
    formatar_valor,
    ordenar_comparativos,
    titulo_resumo,
)
from focus_data import (
    ComparativoIndicador,
    LeituraIndicador,
    montar_comparativos,
    serie_historica,
)
from focus_leitura import (
    ErroBuscaFocus,
    ErroCacheFocus,
    atualizar_e_obter_historico,
    carregar_cache,
    data_ultima_atualizacao_cache,
)
from focus_regras import explicar_leigo, resumo_efeitos
from noticias_feed import ResultadoNoticias, buscar_noticias
from noticias_focus import cruzar_noticias_com_focus

_ROTULOS_EFEITO = {
    "positivo": ("Tende a favorecer", "trending_up", "blue"),
    "negativo": ("Tende a pressionar", "trending_down", "orange"),
    "neutro": ("Efeito misto", "swap_vert", "gray"),
}
_CARACTERES_MARKDOWN = re.compile(r"([\\`*_{}\[\]<>()#+\-.!|])")
_CORES_RELACAO = {
    "Em linha": "green",
    "Em tensão": "orange",
    "Monitorar": "blue",
    "Sem direção clara": "gray",
}


@st.cache_data(ttl=15 * 60, show_spinner=False)
def _carregar_noticias() -> ResultadoNoticias:
    return buscar_noticias()


def _montar_comparativos(
    historico: list[LeituraIndicador],
) -> list[ComparativoIndicador]:
    return ordenar_comparativos(montar_comparativos(historico))


def _renderizar_metrica(
    comparativo: ComparativoIndicador,
    historico: list[LeituraIndicador],
    *,
    com_grafico: bool,
) -> None:
    serie = serie_historica(historico, comparativo.atual.indicador)
    grafico = [leitura.mediana for leitura in serie[-8:]]
    descricao_delta = (
        "Variação em relação à leitura anterior disponível."
        if comparativo.anterior is not None
        else "Ainda não existe uma leitura anterior comparável."
    )
    st.metric(
        label=comparativo.atual.indicador,
        value=formatar_valor(comparativo),
        delta=formatar_delta(comparativo),
        delta_color="off",
        delta_description=descricao_delta,
        border=True,
        chart_data=grafico if com_grafico and len(grafico) >= 2 else None,
        chart_type="line",
        help=(
            f"Referência {comparativo.atual.referencia}. "
            f"Coleta de {comparativo.atual.data_coleta.strftime('%d/%m/%Y')}."
        ),
    )


def _escapar_markdown(texto: str) -> str:
    return _CARACTERES_MARKDOWN.sub(r"\\\1", texto)


def _renderizar_cabecalho() -> bool:
    cabecalho, acoes = st.columns([4, 1], vertical_alignment="bottom")
    with cabecalho:
        st.caption("BOLETIM FOCUS")
        st.header("Expectativas do mercado")
        st.write("Selic, inflação e câmbio esperados para os próximos meses.")
    with acoes:
        atualizar = st.button(
            "Atualizar dados",
            type="primary",
            icon=":material/refresh:",
            width="stretch",
        )
        with st.popover(
            "Como ler",
            icon=":material/info:",
            width="stretch",
        ):
            st.markdown(
                """
                O **Boletim Focus mede expectativas**, não dados já
                realizados. Os efeitos mostrados são relações historicamente
                observadas e condicionais — não previsões nem orientação
                personalizada.
                """
            )
    return atualizar


def _obter_historico(atualizar: bool) -> list[LeituraIndicador]:
    try:
        historico = carregar_cache()
    except ErroCacheFocus:
        historico = []
        st.warning(
            "O histórico local precisa ser reconstruído. O app tentará "
            "buscar uma cópia íntegra no BACEN."
        )

    try:
        ultima_verificacao = data_ultima_atualizacao_cache()
    except ErroCacheFocus:
        ultima_verificacao = None

    hoje = date.today()
    atualizar_automaticamente = (
        not atualizar
        and deve_verificar_automaticamente(ultima_verificacao, hoje)
    )
    if atualizar_automaticamente:
        chave_tentativa = hoje.isoformat()
        if st.session_state.get("focus_auto_tentado_em") == chave_tentativa:
            return historico
        st.session_state["focus_auto_tentado_em"] = chave_tentativa

    if not atualizar and not atualizar_automaticamente:
        return historico

    mensagem = (
        "Verificando automaticamente os dados mais recentes no BACEN..."
        if atualizar_automaticamente
        else "Buscando expectativas mais recentes no BACEN..."
    )
    with st.spinner(
        mensagem,
        show_time=True,
    ):
        try:
            historico = atualizar_e_obter_historico()
            st.toast(
                (
                    "Dados do Focus verificados automaticamente."
                    if atualizar_automaticamente
                    else "Dados do Focus atualizados."
                ),
                icon=":material/check_circle:",
            )
            return historico
        except (ErroBuscaFocus, ErroCacheFocus) as erro:
            if historico:
                st.warning(
                    "Não foi possível verificar o BACEN agora. "
                    "Mantivemos a última coleta salva."
                )
            else:
                st.error(str(erro))
            return historico


def _renderizar_resumo(
    comparativos: list[ComparativoIndicador],
) -> ComparativoIndicador:
    data_mais_recente = max(
        comparativo.atual.data_coleta for comparativo in comparativos
    )
    atualidade = avaliar_atualidade(data_mais_recente, date.today())
    st.badge(
        atualidade.rotulo,
        icon=f":material/{atualidade.icone}:",
        color=atualidade.cor,
    )
    st.caption(
        f"{data_mais_recente.strftime('%d/%m/%Y')} · "
        f"{atualidade.descricao} · Banco Central"
    )
    destaque = escolher_destaque(comparativos)
    with st.container(border=True, key="resumo_semana"):
        st.subheader(titulo_resumo(comparativos))
        st.write(explicar_leigo(destaque))
    return destaque


def _renderizar_metricas(
    comparativos: list[ComparativoIndicador],
    historico: list[LeituraIndicador],
) -> None:
    mapa = {
        comparativo.atual.indicador: comparativo
        for comparativo in comparativos
    }
    principais = [
        mapa[indicador]
        for indicador in INDICADORES_PRIORITARIOS
        if indicador in mapa
    ]
    colunas = st.columns(max(1, len(principais)), gap="medium")
    for coluna, comparativo in zip(colunas, principais):
        with coluna:
            _renderizar_metrica(
                comparativo, historico, com_grafico=True
            )

    secundarios = [
        comparativo
        for comparativo in comparativos
        if comparativo.atual.indicador not in INDICADORES_PRIORITARIOS
    ]
    if not secundarios:
        return
    with st.expander(
        "Ver PIB, IGP-M e dívida pública",
        icon=":material/add_chart:",
    ):
        colunas = st.columns(min(3, len(secundarios)), gap="medium")
        for coluna, comparativo in zip(colunas, secundarios):
            with coluna:
                _renderizar_metrica(
                    comparativo, historico, com_grafico=False
                )


def _renderizar_impactos(
    comparativos: list[ComparativoIndicador],
    destaque: ComparativoIndicador,
) -> None:
    com_efeitos = [
        comparativo
        for comparativo in comparativos
        if resumo_efeitos(comparativo)
    ]
    if not com_efeitos:
        return

    with st.expander(
        "Possíveis impactos por classe de ativo",
        icon=":material/insights:",
    ):
        opcoes = [comparativo.atual.indicador for comparativo in com_efeitos]
        padrao = (
            destaque.atual.indicador
            if destaque.atual.indicador in opcoes
            else opcoes[0]
        )
        indicador = st.pills(
            "Indicador para explorar",
            opcoes,
            default=padrao,
            required=True,
            label_visibility="collapsed",
            key="indicador_impacto",
        )
        comparativo_selecionado = next(
            comparativo
            for comparativo in com_efeitos
            if comparativo.atual.indicador == indicador
        )
        st.write(explicar_leigo(comparativo_selecionado))
        efeitos = resumo_efeitos(comparativo_selecionado)
        for inicio in range(0, len(efeitos), 3):
            grupo = efeitos[inicio : inicio + 3]
            colunas = st.columns(len(grupo), gap="medium")
            for coluna, efeito in zip(colunas, grupo):
                rotulo, icone, cor = _ROTULOS_EFEITO[efeito.sentido]
                with coluna:
                    with st.container(border=True):
                        st.badge(
                            rotulo,
                            icon=f":material/{icone}:",
                            color=cor,
                        )
                        st.markdown(f"**{efeito.classe.value}**")
                        st.write(efeito.explicacao)


def _renderizar_noticias_focus(
    comparativos: list[ComparativoIndicador],
) -> None:
    st.subheader("Noticiário x Focus")
    try:
        with st.spinner("Lendo fontes públicas..."):
            resultado = _carregar_noticias()
    except Exception:
        resultado = ResultadoNoticias(
            noticias=(),
            fontes_indisponiveis=("Fontes de notícias",),
        )

    noticias = list(resultado.noticias)
    fontes_ativas = sorted({noticia.fonte for noticia in noticias})
    if noticias:
        st.caption(
            f"{len(noticias)} manchetes recentes · "
            f"{len(fontes_ativas)} fontes: {', '.join(fontes_ativas)}."
        )
    leituras = cruzar_noticias_com_focus(comparativos, noticias)
    if not leituras:
        st.info(
            "Ainda não há manchetes suficientes para cruzar com a última "
            "mudança do Focus."
        )
    else:
        colunas = st.columns(len(leituras), gap="medium")
        for coluna, leitura in zip(colunas, leituras):
            with coluna:
                with st.container(border=True):
                    st.badge(
                        leitura.relacao,
                        color=_CORES_RELACAO[leitura.relacao],
                    )
                    st.markdown(f"**{leitura.tema}**")
                    st.caption(
                        f"{leitura.mencoes} manchetes · "
                        f"{len(leitura.fontes)} fontes · "
                        f"Focus: {leitura.indicador_focus}"
                    )
                    st.write(leitura.resumo)
                    with st.popover(
                        "Ver manchetes",
                        icon=":material/newspaper:",
                        width="stretch",
                    ):
                        for noticia in leitura.destaques:
                            st.markdown(
                                f"[{_escapar_markdown(noticia.titulo)}]"
                                f"({noticia.link})"
                            )
                            st.caption(noticia.fonte)

    if resultado.fontes_indisponiveis:
        st.caption(
            "Indisponíveis agora: "
            + ", ".join(resultado.fontes_indisponiveis)
            + "."
        )
    st.caption(
        "A conexão usa somente títulos e categorias dos feeds; não lê o "
        "corpo das matérias e não transforma frequência em verdade."
    )


def _renderizar_detalhes(
    comparativos: list[ComparativoIndicador],
) -> None:
    with st.expander(
        "Todos os indicadores e metodologia",
        icon=":material/data_exploration:",
    ):
        st.caption(
            "Mínimo, máximo, desvio-padrão e número de respondentes mostram "
            "quanto consenso existe por trás da mediana."
        )
        linhas = [
            {
                "Indicador": comparativo.atual.indicador,
                "Referência": comparativo.atual.referencia,
                "Mediana atual": comparativo.atual.mediana,
                "Mediana anterior": (
                    comparativo.anterior.mediana
                    if comparativo.anterior
                    else None
                ),
                "Delta": comparativo.delta,
                "Mínimo": comparativo.atual.minimo,
                "Máximo": comparativo.atual.maximo,
                "Desvio-padrão": comparativo.atual.desvio_padrao,
                "Respondentes": comparativo.atual.num_respondentes,
            }
            for comparativo in comparativos
        ]
        st.dataframe(
            pd.DataFrame(linhas),
            hide_index=True,
            width="stretch",
        )
        st.markdown("### Explicações por indicador")
        for comparativo in comparativos:
            with st.container(border=True):
                st.markdown(
                    f"**{_escapar_markdown(comparativo.atual.indicador)}**"
                )
                st.write(explicar_leigo(comparativo))


def render_secao() -> None:
    atualizar = _renderizar_cabecalho()
    historico = _obter_historico(atualizar)
    if not historico:
        st.warning(
            "Ainda não há uma leitura salva. Use **Atualizar dados** para "
            "criar a primeira fotografia das expectativas."
        )
        return

    comparativos = _montar_comparativos(historico)
    if not comparativos:
        st.warning("O histórico salvo não contém indicadores reconhecíveis.")
        return

    destaque = _renderizar_resumo(comparativos)
    _renderizar_metricas(comparativos, historico)
    _renderizar_noticias_focus(comparativos)
    _renderizar_impactos(comparativos, destaque)
    _renderizar_detalhes(comparativos)
    st.caption(
        "Fonte dos indicadores: BACEN — Sistema de Expectativas de Mercado "
        "(Boletim Focus), via API pública Olinda. Conteúdo educacional; não "
        "é orientação de investimento personalizada."
    )
