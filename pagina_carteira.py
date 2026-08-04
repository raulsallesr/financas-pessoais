"""Composição visual da carteira pessoal, mantida apenas na sessão."""

from __future__ import annotations

from hashlib import sha256

import pandas as pd
import streamlit as st

from b3_importacao import ErroImportacaoB3, importar_posicao_b3
from carteira_modelo import (
    BENCHMARKS,
    CLASSES_CARTEIRA,
    comparar_com_benchmarks,
    cruzar_cenario,
    montar_posicoes,
    resumir_carteira,
)
from macro_modelo import CenarioMacro
from mercado_data import SerieMercado


_COLUNAS = (
    "Ativo",
    "Classe",
    "Valor atual (R$)",
    "Valor investido (R$)",
    "Comparar com",
)

_CORES_ESTADO = {
    "vento favorável": "green",
    "mais pressionado": "orange",
    "cenário misto": "gray",
    "proteção com ressalvas": "blue",
    "sem leitura específica": "gray",
}


def _tabela_inicial(
    registros: list[dict[str, object]] | None = None,
) -> pd.DataFrame:
    if registros:
        return pd.DataFrame(registros, columns=_COLUNAS)
    return pd.DataFrame(
        [
            {
                "Ativo": "",
                "Classe": CLASSES_CARTEIRA[0],
                "Valor atual (R$)": None,
                "Valor investido (R$)": None,
                "Comparar com": BENCHMARKS[0],
            }
        ],
        columns=_COLUNAS,
    )


def _moeda(valor: float) -> str:
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def _percentual(valor: float | None) -> str:
    return "—" if valor is None else f"{valor:+.2f}%".replace(".", ",")


def _preparar_editor_b3(arquivo) -> tuple[pd.DataFrame, str]:
    if arquivo is None:
        return _tabela_inicial(), "carteira_editor_manual"
    conteudo = arquivo.getvalue()
    try:
        resultado = importar_posicao_b3(conteudo)
    except ErroImportacaoB3 as erro:
        st.error(
            str(erro) + " Você ainda pode preencher a tabela manualmente.",
            icon=":material/error:",
        )
        return _tabela_inicial(), "carteira_editor_manual"

    st.success(
        f"{len(resultado.posicoes)} ativos consolidados · "
        f"{_moeda(resultado.valor_total)} nesta posição parcial.",
        icon=":material/check_circle:",
    )
    st.caption(
        f"{resultado.linhas_validas} linhas de posição lidas em "
        f"{len(resultado.abas_lidas)} abas; "
        f"{resultado.linhas_ignoradas} linhas de subtotal, vazias ou sem "
        "valor foram descartadas. Conta, instituição, CNPJ, ISIN e contratos "
        "não entram no editor."
    )
    registros = [posicao.para_editor() for posicao in resultado.posicoes]
    chave = sha256(conteudo).hexdigest()[:12]
    return _tabela_inicial(registros), f"carteira_editor_b3_{chave}"


def _renderizar_resumo(posicoes) -> None:
    resumo = resumir_carteira(posicoes)
    metricas = st.columns(4, gap="medium")
    metricas[0].metric(
        "Valor atual",
        _moeda(resumo.total_atual),
        border=True,
    )
    metricas[1].metric(
        "Posições",
        str(resumo.quantidade_posicoes),
        border=True,
    )
    metricas[2].metric(
        "Maior posição",
        f"{resumo.maior_concentracao_percentual:.1f}%".replace(".", ","),
        border=True,
    )
    metricas[3].metric(
        "Retorno informado",
        _percentual(resumo.retorno_conhecido_percentual),
        delta=(
            _moeda(resumo.resultado_conhecido)
            if resumo.resultado_conhecido is not None
            else "Preencha o valor investido"
        ),
        delta_color="off",
        border=True,
        help=(
            "Calculado apenas nas posições em que o valor investido foi "
            "preenchido."
        ),
    )

    alocacao = pd.DataFrame(
        [
            {
                "Classe": classe,
                "Valor atual (R$)": valor,
                "Peso (%)": (valor / resumo.total_atual) * 100,
            }
            for classe, valor in resumo.alocacao_por_classe
        ]
    )
    esquerda, direita = st.columns(
        [3, 2], gap="large", vertical_alignment="top"
    )
    with esquerda:
        st.subheader("Alocação por classe")
        st.bar_chart(
            alocacao,
            x="Classe",
            y="Valor atual (R$)",
            height=300,
            color="#1e40af",
        )
    with direita:
        st.subheader("Detalhe da alocação")
        st.dataframe(
            alocacao,
            hide_index=True,
            width="stretch",
            column_config={
                "Valor atual (R$)": st.column_config.NumberColumn(
                    format="R$ %.2f"
                ),
                "Peso (%)": st.column_config.NumberColumn(format="%.1f%%"),
            },
        )


def _renderizar_comparacoes(
    posicoes,
    series: list[SerieMercado],
) -> None:
    comparacoes = comparar_com_benchmarks(posicoes, series)
    if not comparacoes:
        return
    st.subheader("Como as posições estão se saindo")
    st.caption(
        "O retorno da posição usa os valores atual e investido que você "
        "informou. A referência mostra a variação desde o primeiro ponto "
        "útil disponível do ano. Como os períodos podem ser diferentes, o "
        "app não calcula uma diferença direta entre eles."
    )
    dados = pd.DataFrame(
        [
            {
                "Ativo": item.ativo,
                "Referência": item.benchmark,
                "Posição desde os aportes (%)": (
                    item.retorno_posicao_percentual
                ),
                "Referência no ano (%)": (
                    item.retorno_benchmark_percentual
                ),
            }
            for item in comparacoes
        ]
    )
    st.dataframe(
        dados,
        hide_index=True,
        width="stretch",
        column_config={
            "Posição desde os aportes (%)": (
                st.column_config.NumberColumn(format="%.2f%%")
            ),
            "Referência no ano (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
        },
    )


def _renderizar_impactos(posicoes, cenario: CenarioMacro | None) -> None:
    st.subheader("Como o cenário encosta na carteira")
    st.caption(
        "A leitura cruza apenas a classe de cada posição com o Radar Macro. "
        "Ela não avalia qualidade, preço de entrada, prazo ou adequação."
    )
    impactos = cruzar_cenario(posicoes, cenario)
    for inicio in range(0, len(impactos), 2):
        grupo = impactos[inicio : inicio + 2]
        colunas = st.columns(len(grupo), gap="medium")
        for coluna, impacto in zip(colunas, grupo):
            with coluna:
                with st.container(border=True):
                    st.badge(
                        impacto.estado,
                        color=_CORES_ESTADO[impacto.estado],
                    )
                    st.markdown(f"**{impacto.classe}**")
                    st.caption(
                        f"{_moeda(impacto.valor_atual)} · "
                        f"{impacto.peso_percentual:.1f}% da carteira"
                    )
                    st.write(impacto.explicacao)


def render(
    cenario: CenarioMacro | None,
    series: list[SerieMercado],
) -> None:
    st.caption("CARTEIRA PESSOAL")
    st.header("Minha carteira em contexto")
    st.write(
        "Adicione cada ativo, sua classe e quanto ele vale hoje. Se também "
        "informar quanto foi investido, o app calcula o resultado e permite "
        "comparar com uma referência desde o início do ano."
    )
    st.info(
        "Os valores ficam somente nesta sessão do navegador: não são "
        "gravados em arquivo nem enviados ao GitHub. A planilha importada "
        "também é processada apenas em memória.",
        icon=":material/lock:",
    )

    with st.container(border=True):
        st.markdown("**Importar posição da B3**")
        st.write(
            "Envie o arquivo XLSX da Área do Investidor para preencher a "
            "tabela automaticamente. A posição pode ser parcial: depois da "
            "importação, acrescente ou ajuste qualquer linha."
        )
        arquivo_b3 = st.file_uploader(
            "Planilha de posição da B3",
            type=("xlsx",),
            accept_multiple_files=False,
            help=(
                "São usados somente ativo, tipo, indexador e valor "
                "atualizado. Identificadores e dados da instituição são "
                "ignorados."
            ),
        )

    tabela_base, chave_editor = _preparar_editor_b3(arquivo_b3)
    tabela = st.data_editor(
        tabela_base,
        hide_index=True,
        num_rows="dynamic",
        width="stretch",
        key=chave_editor,
        column_config={
            "Ativo": st.column_config.TextColumn(
                "Ativo",
                help="Nome livre, por exemplo: Tesouro Selic ou ETF.",
                required=True,
            ),
            "Classe": st.column_config.SelectboxColumn(
                "Classe",
                options=CLASSES_CARTEIRA,
                required=True,
            ),
            "Valor atual (R$)": st.column_config.NumberColumn(
                "Valor atual (R$)",
                min_value=0.0,
                step=100.0,
                format="R$ %.2f",
                required=True,
            ),
            "Valor investido (R$)": st.column_config.NumberColumn(
                "Valor investido (R$)",
                help="Opcional; habilita o cálculo de resultado.",
                min_value=0.0,
                step=100.0,
                format="R$ %.2f",
            ),
            "Comparar com": st.column_config.SelectboxColumn(
                "Comparar com",
                options=BENCHMARKS,
                required=True,
            ),
        },
    )
    posicoes = montar_posicoes(tabela.to_dict("records"))
    if not posicoes:
        st.markdown(
            """
            **Quando você preencher a primeira posição, esta área mostrará:**

            - valor total, concentração e alocação por classe;
            - resultado da posição quando houver valor investido;
            - comparação com CDI, Selic, dólar, Brent ou Bitcoin no ano;
            - quais parcelas da carteira estão mais expostas ao cenário macro.
            """
        )
        return

    _renderizar_resumo(posicoes)
    _renderizar_comparacoes(posicoes, series)
    _renderizar_impactos(posicoes, cenario)
    st.caption(
        "Leitura descritiva e educacional. Não constitui recomendação de "
        "investimento nem substitui a análise de cada ativo."
    )
