"""Composição visual da página do Boletim Focus."""

from __future__ import annotations

import re
from datetime import date

import pandas as pd
import streamlit as st

from focuslens.core.financas_taxonomia import Direcao
from focuslens.core.focus_atualizacao import (
    deve_verificar_automaticamente,
)
from focuslens.ui.focus_apresentacao import (
    descricao_resumo_semanal,
    escolher_destaque,
    formatar_delta,
    formatar_valor,
    ordenar_comparativos,
    titulo_resumo_semanal,
)
from focuslens.core.focus_data import (
    ComparativoIndicador,
    LeituraIndicador,
    montar_comparativos,
    serie_historica,
)
from focuslens.core.focus_semanal import (
    EstadoFocusSemanal,
    ResumoFocusSemanal,
    montar_resumo_semanal,
)
from focuslens.adapters.focus_leitura import (
    ErroBuscaFocus,
    ErroCacheFocus,
    atualizar_e_obter_historico,
    carregar_cache,
    data_ultima_atualizacao_cache,
)
from focuslens.core.focus_regras import explicar_leigo, resumo_efeitos
from focuslens.core.noticias_analise import AnaliseArtigo, analisar_artigo
from focuslens.adapters.noticias_artigo import ErroLeituraArtigo, buscar_artigo
from focuslens.core.noticias_data import Noticia
from focuslens.adapters.noticias_feed import ResultadoNoticias, buscar_noticias
from focuslens.core.noticias_focus import cruzar_noticias_com_focus

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
_ESTILO_ESTADO_SEMANAL = {
    EstadoFocusSemanal.ATUALIZADO: ("check_circle", "green"),
    EstadoFocusSemanal.DEFASADO: ("history", "orange"),
    EstadoFocusSemanal.INDISPONIVEL: ("cloud_off", "gray"),
    EstadoFocusSemanal.SEM_MUDANCA_RELEVANTE: (
        "horizontal_rule",
        "blue",
    ),
}


@st.cache_data(ttl=15 * 60, show_spinner=False)
def _carregar_noticias() -> ResultadoNoticias:
    return buscar_noticias()


@st.cache_data(ttl=30 * 60, show_spinner=False)
def _carregar_analise_artigo(
    noticia: Noticia,
    comparativos: tuple[ComparativoIndicador, ...],
) -> AnaliseArtigo:
    artigo = buscar_artigo(noticia)
    return analisar_artigo(artigo, list(comparativos))


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
        st.caption("FOCUSLENS BR · FOCUS SEMANAL")
        st.header("O que mudou no Focus")
        st.write(
            "As maiores revisões de Selic, IPCA, câmbio e PIB, com datas "
            "e fonte."
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
    historico: list[LeituraIndicador],
) -> ResumoFocusSemanal:
    resumo = montar_resumo_semanal(comparativos, date.today())
    icone, cor = _ESTILO_ESTADO_SEMANAL[resumo.estado]
    with st.container(border=True, key="resumo_semana"):
        estado, origem = st.columns(
            [1, 3],
            gap="medium",
            vertical_alignment="center",
        )
        with estado:
            st.badge(
                resumo.estado.value,
                icon=f":material/{icone}:",
                color=cor,
            )
        with origem:
            if resumo.data_mais_recente is None:
                st.caption("Banco Central · API pública Olinda")
            else:
                st.caption(
                    f"Coleta de "
                    f"{resumo.data_mais_recente.strftime('%d/%m/%Y')} · "
                    f"{resumo.total_acompanhados} indicadores acompanhados"
                )

        st.caption("O QUE MUDOU")
        st.subheader(titulo_resumo_semanal(resumo))
        st.write(descricao_resumo_semanal(resumo))

        if resumo.destaques:
            colunas = st.columns(len(resumo.destaques), gap="medium")
            for posicao, (coluna, comparativo) in enumerate(
                zip(colunas, resumo.destaques),
                start=1,
            ):
                with coluna:
                    if comparativo.anterior is None:
                        st.caption("PRIMEIRA LEITURA")
                    elif comparativo.direcao == Direcao.ESTAVEL:
                        st.caption("DENTRO DO LIMIAR")
                    else:
                        st.caption(f"{posicao}ª MAIOR REVISÃO")
                    _renderizar_metrica(
                        comparativo,
                        historico,
                        com_grafico=True,
                    )
    return resumo


def _renderizar_metricas(
    comparativos: list[ComparativoIndicador],
    historico: list[LeituraIndicador],
    exibidos: set[str],
) -> None:
    restantes = [
        comparativo
        for comparativo in comparativos
        if comparativo.atual.indicador not in exibidos
    ]
    if not restantes:
        return
    with st.expander(
        "Ver os demais indicadores",
        icon=":material/add_chart:",
    ):
        colunas = st.columns(min(3, len(restantes)), gap="medium")
        for coluna, comparativo in zip(colunas, restantes):
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

        candidatas = _noticias_unicas(
            [
                noticia
                for leitura in leituras
                for noticia in leitura.destaques
            ]
        )
        _renderizar_leitura_aprofundada(candidatas, comparativos)

    if resultado.fontes_indisponiveis:
        st.caption(
            "Indisponíveis agora: "
            + ", ".join(resultado.fontes_indisponiveis)
            + "."
        )
    st.caption(
        "Os cartões usam títulos e categorias. O corpo só é lido ao pedir "
        "uma análise e não é salvo; frequência editorial não vira verdade."
    )


def _noticias_unicas(noticias: list[Noticia]) -> list[Noticia]:
    unicas: list[Noticia] = []
    links: set[str] = set()
    for noticia in noticias:
        if noticia.link in links:
            continue
        links.add(noticia.link)
        unicas.append(noticia)
    return unicas


def _renderizar_leitura_aprofundada(
    noticias: list[Noticia],
    comparativos: list[ComparativoIndicador],
) -> None:
    if not noticias:
        return
    with st.expander(
        "Destrinchar uma matéria",
        icon=":material/manage_search:",
    ):
        st.caption(
            "Escolha uma matéria para verificar o conteúdo, os números "
            "citados e a conexão com o Focus."
        )
        noticia = st.selectbox(
            "Matéria",
            noticias,
            format_func=lambda item: f"{item.fonte} · {item.titulo}",
            key="materia_para_analise",
        )
        chave = _chave_analise(noticia, comparativos)
        analisar = st.button(
            "Analisar matéria",
            icon=":material/article:",
            width="stretch",
            key="analisar_materia_focus",
        )
        if analisar:
            try:
                with st.spinner(
                    f"Lendo e conferindo {noticia.fonte}...",
                    show_time=True,
                ):
                    analise = _carregar_analise_artigo(
                        noticia,
                        tuple(comparativos),
                    )
                st.session_state["analise_materia_focus"] = (
                    chave,
                    analise,
                )
            except ErroLeituraArtigo as erro:
                st.session_state.pop("analise_materia_focus", None)
                st.warning(str(erro))
                st.markdown(
                    f"[Abrir a matéria na fonte]"
                    f"({noticia.link})"
                )
            except Exception:
                st.session_state.pop("analise_materia_focus", None)
                st.warning(
                    "A matéria não pôde ser analisada agora. "
                    "O link original continua disponível."
                )
                st.markdown(
                    f"[Abrir a matéria na fonte]"
                    f"({noticia.link})"
                )

        resultado_salvo = st.session_state.get("analise_materia_focus")
        if (
            resultado_salvo
            and resultado_salvo[0] == chave
        ):
            _renderizar_analise_artigo(resultado_salvo[1])


def _chave_analise(
    noticia: Noticia,
    comparativos: list[ComparativoIndicador],
) -> tuple[object, ...]:
    fotografia_focus = tuple(
        (
            item.atual.indicador,
            item.atual.data_coleta.isoformat(),
            item.atual.mediana,
            item.direcao.value,
        )
        for item in comparativos
    )
    return noticia.link, fotografia_focus


def _renderizar_analise_artigo(analise: AnaliseArtigo) -> None:
    st.divider()
    st.markdown(
        f"#### [{_escapar_markdown(analise.noticia.titulo)}]"
        f"({analise.noticia.link})"
    )
    st.caption(
        f"{analise.noticia.fonte} · {analise.origem} · "
        f"{analise.palavras_lidas} palavras examinadas"
    )
    st.markdown("**O que encontramos**")
    st.write(analise.sintese)

    if analise.conexoes:
        st.markdown("**Como isso conversa com o Focus**")
        for conexao in analise.conexoes:
            with st.container(border=True):
                st.badge(
                    conexao.relacao,
                    color=_CORES_RELACAO[conexao.relacao],
                )
                st.markdown(
                    f"**{conexao.tema} · Focus: "
                    f"{conexao.indicador_focus}**"
                )
                st.write(conexao.explicacao)

    numeros, instituicoes = st.columns(2, gap="medium")
    with numeros:
        st.markdown("**Números citados**")
        if analise.numeros:
            for evidencia in analise.numeros:
                st.markdown(
                    f"- **{_escapar_markdown(evidencia.valor)}** "
                    f"· {evidencia.contexto}"
                )
        else:
            st.caption("Nenhum número econômico detectado com segurança.")
    with instituicoes:
        st.markdown("**Quem aparece no texto**")
        if analise.instituicoes:
            for instituicao in analise.instituicoes:
                st.markdown(f"- {instituicao}")
        else:
            st.caption("Nenhuma instituição-chave detectada com segurança.")

    if analise.onde_olhar:
        st.markdown("**Onde olhar a partir daqui**")
        for item in analise.onde_olhar:
            st.markdown(f"- {item}")

    if analise.trecho_verificacao:
        st.caption(
            "Trecho curto para conferência: "
            f"“{_escapar_markdown(analise.trecho_verificacao)}”"
        )
    st.caption(analise.limitacao)


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
        _renderizar_resumo([], [])
        return

    comparativos = _montar_comparativos(historico)
    if not comparativos:
        _renderizar_resumo([], historico)
        return

    resumo = _renderizar_resumo(comparativos, historico)
    exibidos = {
        comparativo.atual.indicador
        for comparativo in resumo.destaques
    }
    _renderizar_metricas(comparativos, historico, exibidos)
    _renderizar_noticias_focus(comparativos)
    destaque = (
        resumo.destaques[0]
        if resumo.destaques
        else escolher_destaque(comparativos)
    )
    _renderizar_impactos(comparativos, destaque)
    _renderizar_detalhes(comparativos)
    st.caption(
        "Fonte dos indicadores: BACEN — Sistema de Expectativas de Mercado "
        "(Boletim Focus), via API pública Olinda. Conteúdo educacional; não "
        "é orientação de investimento personalizada."
    )
