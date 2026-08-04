"""Composição visual da página do Boletim Focus."""

from __future__ import annotations

import re
from datetime import UTC
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from financas_taxonomia import UNIDADE_INDICADOR
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
    comparar,
    leitura_anterior,
    leitura_mais_recente,
    serie_historica,
)
from focus_leitura import (
    ErroBuscaFocus,
    atualizar_e_obter_historico,
    carregar_cache,
)
from focus_regras import explicar_leigo, resumo_efeitos
from noticias_data import Noticia, selecionar_destaques
from noticias_feed import ResultadoNoticias, buscar_noticias
from ui_estilos import aplicar_estilos

_ROTULOS_EFEITO = {
    "positivo": ("Tende a favorecer", "trending_up", "blue"),
    "negativo": ("Tende a pressionar", "trending_down", "orange"),
    "neutro": ("Efeito misto", "swap_vert", "gray"),
}
_CARACTERES_MARKDOWN = re.compile(r"([\\`*_{}\[\]<>()#+\-.!|])")


@st.cache_data(ttl=15 * 60, show_spinner=False)
def _carregar_noticias() -> ResultadoNoticias:
    return buscar_noticias()


def _montar_comparativos(
    historico: list[LeituraIndicador],
) -> list[ComparativoIndicador]:
    indicadores = {leitura.indicador for leitura in historico}
    comparativos: list[ComparativoIndicador] = []
    for indicador in indicadores:
        leituras = [
            leitura
            for leitura in historico
            if leitura.indicador == indicador
        ]
        atual = leitura_mais_recente(leituras)
        if atual is None:
            continue
        comparativos.append(
            comparar(atual, leitura_anterior(historico, atual))
        )
    return ordenar_comparativos(comparativos)


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


def _formatar_publicacao(noticia: Noticia) -> str:
    if noticia.publicada_em is None:
        return "Horário não informado"
    momento = noticia.publicada_em
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=UTC)
    local = momento.astimezone(ZoneInfo("America/Sao_Paulo"))
    return local.strftime("%d/%m às %H:%M")


def _renderizar_cabecalho() -> bool:
    cabecalho, acoes = st.columns([4, 1], vertical_alignment="bottom")
    with cabecalho:
        st.caption("PANORAMA ECONÔMICO")
        st.title("Seu dinheiro em contexto")
        st.write(
            "Entenda o que mudou nas expectativas e explore os possíveis "
            "efeitos sem transformar cenário em certeza."
        )
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
    if not atualizar:
        return carregar_cache()
    with st.spinner(
        "Buscando expectativas mais recentes no BACEN...",
        show_time=True,
    ):
        try:
            historico = atualizar_e_obter_historico()
            st.toast(
                "Dados do Focus atualizados.",
                icon=":material/check_circle:",
            )
            return historico
        except ErroBuscaFocus as erro:
            st.error(str(erro))
            return carregar_cache()


def _renderizar_resumo(
    comparativos: list[ComparativoIndicador],
) -> ComparativoIndicador:
    data_mais_recente = max(
        comparativo.atual.data_coleta for comparativo in comparativos
    )
    st.caption(
        f"Última coleta disponível: "
        f"{data_mais_recente.strftime('%d/%m/%Y')} · "
        "Fonte oficial dos indicadores: Banco Central."
    )
    destaque = escolher_destaque(comparativos)
    with st.container(border=True, key="resumo_semana"):
        st.badge(
            "Expectativas de mercado",
            icon=":material/query_stats:",
            color="blue",
        )
        st.subheader(titulo_resumo(comparativos))
        st.write(explicar_leigo(destaque))
        if destaque.anterior is not None:
            st.caption(
                "Comparação real: "
                f"{destaque.anterior.data_coleta.strftime('%d/%m/%Y')} → "
                f"{destaque.atual.data_coleta.strftime('%d/%m/%Y')}. "
                "O destaque considera o limiar específico de cada indicador."
            )
    return destaque


def _renderizar_metricas(
    comparativos: list[ComparativoIndicador],
    historico: list[LeituraIndicador],
) -> None:
    st.subheader("Três números para começar")
    st.caption(
        "Selic, inflação e dólar ficam na primeira camada; os demais "
        "indicadores continuam disponíveis sem disputar atenção."
    )
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
    st.divider()
    st.subheader("O que isso pode afetar")
    st.caption(
        "Escolha um indicador. Os rótulos são condicionais e acompanhados "
        "da explicação — a cor nunca carrega o significado sozinha."
    )
    com_efeitos = [
        comparativo
        for comparativo in comparativos
        if resumo_efeitos(comparativo)
    ]
    if not com_efeitos:
        st.info("A leitura atual ainda não tem efeitos educacionais mapeados.")
        return

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


def _renderizar_historico(
    comparativos: list[ComparativoIndicador],
    historico: list[LeituraIndicador],
) -> None:
    st.subheader("Histórico sem poluição visual")
    opcoes = [comparativo.atual.indicador for comparativo in comparativos]
    indicador = st.pills(
        "Indicador do gráfico",
        opcoes,
        default=opcoes[0],
        required=True,
        label_visibility="collapsed",
        key="indicador_historico",
    )
    serie = serie_historica(historico, indicador)
    if len(serie) < 2:
        st.info(
            "Ainda é preciso salvar pelo menos duas coletas para desenhar "
            "a evolução deste indicador."
        )
        return

    dados = pd.DataFrame(
        {
            "Coleta": [leitura.data_coleta for leitura in serie],
            "Mediana": [leitura.mediana for leitura in serie],
        }
    )
    st.line_chart(
        dados,
        x="Coleta",
        y="Mediana",
        x_label="Data da coleta",
        y_label=UNIDADE_INDICADOR.get(indicador, "Mediana"),
        color="#1e40af",
        height=300,
    )
    if indicador == "Selic":
        st.caption(
            "A reunião observada muda após cada Copom; uma troca de "
            "referência pode gerar salto sem mudança equivalente na "
            "expectativa para a mesma reunião."
        )
    with st.expander(
        "Ver valores usados no gráfico",
        icon=":material/table_rows:",
    ):
        st.dataframe(dados, hide_index=True, width="stretch")


def _renderizar_noticias() -> None:
    st.subheader("Contexto em 3 manchetes")
    st.caption(
        "Leitura externa para contexto. Título e link permanecem na fonte; "
        "os indicadores oficiais continuam sendo os do BACEN."
    )
    try:
        with st.spinner("Atualizando manchetes..."):
            resultado = _carregar_noticias()
    except Exception:
        resultado = ResultadoNoticias(
            noticias=(),
            fontes_indisponiveis=("Feeds de notícias",),
        )
    destaques = selecionar_destaques(list(resultado.noticias), limite=3)
    if not destaques:
        st.info(
            "As manchetes estão temporariamente indisponíveis. O panorama "
            "do Focus continua funcionando normalmente."
        )
    for indice, noticia in enumerate(destaques):
        with st.container(border=True):
            st.badge(
                noticia.fonte,
                icon=":material/newspaper:",
                color="gray",
            )
            st.markdown(f"**{_escapar_markdown(noticia.titulo)}**")
            st.caption(_formatar_publicacao(noticia))
            st.link_button(
                "Ler na fonte",
                noticia.link,
                icon=":material/open_in_new:",
                type="tertiary",
                key=f"noticia_{indice}",
            )
    if resultado.fontes_indisponiveis:
        st.caption(
            "Fonte temporariamente indisponível: "
            + ", ".join(resultado.fontes_indisponiveis)
            + "."
        )


def _renderizar_detalhes(
    comparativos: list[ComparativoIndicador],
) -> None:
    st.divider()
    with st.expander(
        "Ver todos os indicadores, explicações e dispersão",
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


def render() -> None:
    st.set_page_config(
        page_title="Seu dinheiro em contexto",
        page_icon=":material/insights:",
        layout="wide",
    )
    aplicar_estilos()
    atualizar = _renderizar_cabecalho()
    historico = _obter_historico(atualizar)
    if not historico:
        st.warning(
            "Ainda não há uma leitura salva. Use **Atualizar dados** para "
            "criar a primeira fotografia das expectativas."
        )
        st.stop()

    comparativos = _montar_comparativos(historico)
    if not comparativos:
        st.warning("O histórico salvo não contém indicadores reconhecíveis.")
        st.stop()

    destaque = _renderizar_resumo(comparativos)
    _renderizar_metricas(comparativos, historico)
    _renderizar_impactos(comparativos, destaque)

    st.divider()
    coluna_historico, coluna_noticias = st.columns(
        [3, 2], gap="large", vertical_alignment="top"
    )
    with coluna_historico:
        _renderizar_historico(comparativos, historico)
    with coluna_noticias:
        _renderizar_noticias()

    _renderizar_detalhes(comparativos)
    st.caption(
        "Fonte dos indicadores: BACEN — Sistema de Expectativas de Mercado "
        "(Boletim Focus), via API pública Olinda. Conteúdo educacional; não "
        "é orientação de investimento personalizada."
    )
