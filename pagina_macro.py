"""Composição visual do Radar Macro."""

from __future__ import annotations

from datetime import UTC, date

import pandas as pd
import streamlit as st

from focus_data import montar_comparativos
from focus_leitura import ErroCacheFocus, carregar_cache
from macro_modelo import CenarioMacro, construir_cenario
from mercado_data import (
    MovimentoMercado,
    SerieMercado,
    calcular_movimento,
    pontos_base_100,
)
from mercado_fontes import ResultadoMercados, buscar_mercados
from noticias_data import Noticia, selecionar_destaques
from noticias_feed import ResultadoNoticias, buscar_noticias

_CORES_ESTADO = {
    "vento favorável": "green",
    "mais pressionado": "orange",
    "cenário misto": "gray",
    "proteção com ressalvas": "blue",
}
_CODIGOS_PRECO = frozenset({"USDBRL", "BRENT", "BTCBRL"})


@st.cache_data(ttl=15 * 60, show_spinner=False)
def _carregar_mercados() -> ResultadoMercados:
    return buscar_mercados()


@st.cache_data(ttl=15 * 60, show_spinner=False)
def _carregar_noticias_macro() -> ResultadoNoticias:
    return buscar_noticias()


def _formatar_numero(valor: float, casas: int = 2) -> str:
    return (
        f"{valor:,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def _formatar_valor(movimento: MovimentoMercado) -> str:
    if movimento.codigo == "BRENT":
        return f"US$ {_formatar_numero(movimento.valor_atual)}"
    if movimento.codigo == "BTCBRL":
        return f"R$ {_formatar_numero(movimento.valor_atual, 0)}"
    return f"R$ {_formatar_numero(movimento.valor_atual, 4)}"


def _formatar_variacao(movimento: MovimentoMercado) -> str:
    if movimento.variacao_30d is None:
        return "Histórico insuficiente"
    return f"{movimento.variacao_30d:+.2f}% em 30 dias"


def _renderizar_cabecalho() -> None:
    titulo, acao = st.columns([4, 1], vertical_alignment="bottom")
    with titulo:
        st.caption("RADAR MACROECONÔMICO")
        st.header("Sinais, cenário e preços")
        st.write(
            "Uma leitura explicável do momento: dados públicos, temas das "
            "manchetes e condições que confirmam ou invalidam o cenário."
        )
    with acao:
        if st.button(
            "Atualizar radar",
            icon=":material/refresh:",
            type="primary",
            width="stretch",
        ):
            _carregar_mercados.clear()
            _carregar_noticias_macro.clear()
            st.rerun()
        with st.popover(
            "Limites da leitura",
            icon=":material/info:",
            width="stretch",
        ):
            st.write(
                "O radar não prevê preços nem substitui uma decisão "
                "financeira individual. Ele organiza relações condicionais "
                "com horizonte de semanas e confiança limitada."
            )


def _renderizar_precos(series: list[SerieMercado]) -> list[MovimentoMercado]:
    series = [
        serie for serie in series if serie.codigo in _CODIGOS_PRECO
    ]
    st.subheader("Três preços que mudam o cenário")
    st.caption(
        "A seta mostra apenas movimento de preço — alta não significa "
        "automaticamente melhora, e queda não significa piora."
    )
    movimentos = [calcular_movimento(serie) for serie in series]
    colunas = st.columns(max(1, len(movimentos)), gap="medium")
    for coluna, serie, movimento in zip(colunas, series, movimentos):
        with coluna:
            st.metric(
                label=movimento.nome,
                value=_formatar_valor(movimento),
                delta=_formatar_variacao(movimento),
                delta_color="off",
                border=True,
                help=(
                    f"Último ponto em "
                    f"{movimento.data_atual.strftime('%d/%m/%Y')}."
                ),
            )
            st.caption(
                f"{serie.fonte} · ponto de "
                f"{movimento.data_atual.strftime('%d/%m/%Y')}"
            )
            defasagem = (date.today() - movimento.data_atual).days
            if defasagem > 7:
                st.caption(
                    f"Atenção: esta fonte está {defasagem} dias sem "
                    "observação nova."
                )
    return movimentos


def _renderizar_cenario(cenario: CenarioMacro) -> None:
    with st.container(border=True, key="macro_cenario"):
        st.badge(
            f"Confiança {cenario.confianca}",
            icon=":material/model_training:",
            color="blue" if cenario.confianca == "moderada" else "gray",
        )
        st.caption(f"HORIZONTE · {cenario.horizonte}")
        st.subheader(cenario.titulo)
        st.write(cenario.resumo)
        st.markdown("**Cenário-base condicionado**")
        for projecao in cenario.projecoes:
            st.markdown(f"- {projecao}")


def _renderizar_eixos(cenario: CenarioMacro) -> None:
    st.subheader("Como o motor chegou nessa leitura")
    st.caption(
        "Cada eixo mostra direção e evidências. Ausência de sinal é tratada "
        "como incerteza, não como confirmação."
    )
    for inicio in range(0, len(cenario.eixos), 3):
        grupo = cenario.eixos[inicio : inicio + 3]
        colunas = st.columns(len(grupo), gap="medium")
        for coluna, eixo in zip(colunas, grupo):
            with coluna:
                with st.container(border=True):
                    st.markdown(f"**{eixo.nome}**")
                    st.badge(
                        eixo.leitura,
                        color=(
                            "orange"
                            if eixo.saldo > 0
                            else "blue"
                            if eixo.saldo < 0
                            else "gray"
                        ),
                    )
                    if eixo.evidencias:
                        for evidencia in eixo.evidencias:
                            st.caption(evidencia)
                    else:
                        st.caption("Sem sinal quantitativo forte.")


def _renderizar_perspectivas(cenario: CenarioMacro) -> None:
    st.subheader("Ambiente por classe de ativo")
    st.caption(
        "Isto descreve ventos macro relativos; não considera prazo, preço de "
        "entrada, objetivo, liquidez ou tolerância a risco."
    )
    colunas = st.columns(2, gap="medium")
    for indice, perspectiva in enumerate(cenario.perspectivas):
        with colunas[indice % 2]:
            with st.container(border=True):
                st.badge(
                    perspectiva.estado,
                    color=_CORES_ESTADO[perspectiva.estado],
                )
                st.markdown(f"**{perspectiva.classe}**")
                st.write(perspectiva.explicacao)


def _renderizar_linhas(series: list[SerieMercado]) -> None:
    st.subheader("Mercados e juros desde o início do ano")
    st.caption(
        f"Dólar, Brent, Bitcoin, CDI e Selic desde o primeiro ponto útil de "
        f"{date.today().year}. Todas as linhas começam em 100 para comparar "
        "desempenho acumulado, não valores absolutos com unidades diferentes."
    )
    linhas = [
        {
            "Data": ponto.data,
            "Ativo": serie.nome,
            "Índice (base 100)": ponto.valor,
        }
        for serie in series
        for ponto in pontos_base_100(serie)
    ]
    dados = pd.DataFrame(linhas)
    if dados.empty:
        st.info("Ainda não há pontos suficientes para o gráfico.")
        return
    st.line_chart(
        dados,
        x="Data",
        y="Índice (base 100)",
        color="Ativo",
        height=360,
    )

    with st.expander(
        "Ver valores reais e dados do gráfico",
        icon=":material/show_chart:",
    ):
        nomes = [serie.nome for serie in series]
        escolha = st.pills(
            "Série em preço real",
            nomes,
            default=nomes[0],
            required=True,
        )
        serie = next(item for item in series if item.nome == escolha)
        reais = pd.DataFrame(
            {
                "Data": [ponto.data for ponto in serie.pontos],
                "Valor": [ponto.valor for ponto in serie.pontos],
            }
        )
        st.line_chart(
            reais,
            x="Data",
            y="Valor",
            y_label=serie.unidade,
            height=280,
            color="#1e40af",
        )
        st.dataframe(reais, hide_index=True, width="stretch")


def _renderizar_noticias(
    cenario: CenarioMacro,
    noticias: list[Noticia],
) -> None:
    st.subheader("O que domina as manchetes")
    st.caption(
        "O motor conta temas no título e nas categorias do RSS. Ele não "
        "raspa nem presume ter lido o conteúdo integral das matérias."
    )
    if cenario.temas_editoriais:
        colunas = st.columns(len(cenario.temas_editoriais), gap="small")
        for coluna, tema in zip(colunas, cenario.temas_editoriais):
            with coluna:
                st.metric(
                    tema.tema,
                    tema.ocorrencias,
                    border=True,
                )
    else:
        st.info("Nenhum tema macro apareceu com força nas manchetes atuais.")

    destaques = selecionar_destaques(noticias, limite=3)
    with st.expander(
        "Ver manchetes usadas como contexto",
        icon=":material/newspaper:",
    ):
        if not destaques:
            st.caption("Manchetes temporariamente indisponíveis.")
        for indice, noticia in enumerate(destaques):
            publicada = noticia.publicada_em
            if publicada is not None:
                if publicada.tzinfo is None:
                    publicada = publicada.replace(tzinfo=UTC)
                momento = publicada.astimezone().strftime("%d/%m às %H:%M")
            else:
                momento = "horário não informado"
            st.markdown(f"**{noticia.titulo}**")
            st.caption(f"{noticia.fonte} · {momento}")
            st.link_button(
                "Ler na fonte",
                noticia.link,
                icon=":material/open_in_new:",
                type="tertiary",
                key=f"macro_noticia_{indice}",
            )


def _renderizar_invalidadores(cenario: CenarioMacro) -> None:
    with st.expander(
        "O que faria o cenário mudar",
        icon=":material/change_circle:",
    ):
        for item in cenario.invalidadores:
            st.markdown(f"- {item}")
        st.caption(
            "A leitura é recalculada com os dados disponíveis a cada "
            "atualização; não existe cenário permanente."
        )


def render_secao() -> tuple[CenarioMacro | None, list[SerieMercado]]:
    _renderizar_cabecalho()

    with st.spinner("Conectando sinais públicos...", show_time=True):
        try:
            resultado_mercados = _carregar_mercados()
        except Exception:
            resultado_mercados = ResultadoMercados(
                series=(),
                fontes_indisponiveis=("Mercados",),
            )
        try:
            resultado_noticias = _carregar_noticias_macro()
        except Exception:
            resultado_noticias = ResultadoNoticias(
                noticias=(),
                fontes_indisponiveis=("Feeds de notícias",),
            )

    try:
        historico_focus = carregar_cache()
    except ErroCacheFocus:
        historico_focus = []
    series = list(resultado_mercados.series)
    noticias = list(resultado_noticias.noticias)
    comparativos = montar_comparativos(historico_focus)

    if not series and not comparativos:
        st.error(
            "O radar está sem dados quantitativos agora. Tente atualizar "
            "novamente quando as fontes estiverem disponíveis."
        )
        return None, series

    series_precos = [
        serie for serie in series if serie.codigo in _CODIGOS_PRECO
    ]
    if series_precos:
        _renderizar_precos(series_precos)
    cenario = construir_cenario(comparativos, series_precos, noticias)
    _renderizar_cenario(cenario)
    st.divider()
    _renderizar_eixos(cenario)
    _renderizar_perspectivas(cenario)
    if series:
        st.divider()
        _renderizar_linhas(series)
    st.divider()
    _renderizar_noticias(cenario, noticias)
    _renderizar_invalidadores(cenario)

    indisponiveis = (
        *resultado_mercados.fontes_indisponiveis,
        *resultado_noticias.fontes_indisponiveis,
    )
    if indisponiveis:
        st.warning(
            "Fontes temporariamente indisponíveis: "
            + ", ".join(indisponiveis)
            + ". A confiança da leitura foi reduzida."
        )
    st.caption(
        "Fontes: PTAX/Banco Central, Brent/EIA via FRED, BTC/BRL/Binance, "
        "CDI e Selic/Banco Central (SGS), "
        "Boletim Focus/BACEN e metadados RSS de InfoMoney/Brazil Journal. "
        "Conteúdo educacional; cenário condicionado, não previsão garantida "
        "nem orientação personalizada."
    )
    return cenario, series
