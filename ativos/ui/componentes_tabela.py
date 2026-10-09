"""Componentes compartilhados pelas buscas tabulares do módulo Ativos."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd
import streamlit as st


def alertas(valor: object) -> list[str]:
    if isinstance(valor, np.ndarray):
        return [str(item) for item in valor.tolist()]
    if isinstance(valor, (list, tuple)):
        return [str(item) for item in valor]
    if valor is None or pd.isna(valor):
        return []
    return [str(valor)]


def exportar_csv(quadro: pd.DataFrame) -> bytes:
    """Serializa exatamente o recorte visível no contrato pt-BR da tela."""
    exportacao = quadro.copy()
    if "alertas" in exportacao:
        exportacao["alertas"] = exportacao["alertas"].map(
            lambda valor: ", ".join(alertas(valor))
        )
    return exportacao.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")


def formatar_comparacao(valor: object, formato: str) -> str:
    if pd.isna(valor):
        return "—"
    numero = float(valor)
    if formato == "percentual":
        return f"{numero:.2%}".replace(".", ",")
    if formato == "inteiro":
        return f"{numero:,.0f}".replace(",", ".")
    if formato == "moeda":
        return f"R$ {numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if formato == "reais_abreviado":
        for divisor, sufixo in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(numero) >= divisor:
                return f"R$ {numero / divisor:.2f} {sufixo}".replace(".", ",")
        return f"R$ {numero:.2f}".replace(".", ",")
    return f"{numero:.2f}".replace(".", ",")


def configuracao_metricas(
    metricas: Mapping[str, Mapping[str, str]],
    colunas: Sequence[str],
) -> dict[str, object]:
    formatos = {
        "moeda": "R$ %.2f",
        "reais_abreviado": "compact",
        "percentual": "percent",
        "multiplo": "%.2f",
        "inteiro": "localized",
    }
    return {
        coluna: st.column_config.NumberColumn(
            metricas[coluna]["rotulo"],
            help=metricas[coluna]["descricao"],
            format=formatos[metricas[coluna]["formato"]],
        )
        for coluna in colunas
    }


def renderizar_tabela_e_csv(
    quadro: pd.DataFrame,
    colunas: Sequence[str],
    *,
    configuracao: Mapping[str, object],
    arquivo: str,
) -> None:
    st.dataframe(
        quadro[list(colunas)],
        hide_index=True,
        width="stretch",
        height=620,
        column_config=dict(configuracao),
        placeholder="—",
    )
    st.download_button(
        "Exportar CSV",
        data=exportar_csv(quadro[list(colunas)]),
        file_name=arquivo,
        mime="text/csv",
    )


def renderizar_comparador(
    quadro: pd.DataFrame,
    colunas_metricas: Sequence[str],
    metricas: Mapping[str, Mapping[str, str]],
    *,
    key: str,
) -> None:
    st.subheader("Comparador")
    tickers = st.multiselect(
        "Selecione até 5 tickers",
        quadro["ticker"].tolist(),
        max_selections=5,
        key=key,
    )
    if not tickers:
        return
    comparacao = quadro[quadro["ticker"].isin(tickers)].set_index("ticker")
    linhas = {
        metricas[coluna]["rotulo"]: [
            formatar_comparacao(
                comparacao.at[ticker, coluna], metricas[coluna]["formato"]
            )
            for ticker in tickers
        ]
        for coluna in colunas_metricas
    }
    st.dataframe(
        pd.DataFrame(linhas, index=tickers).T,
        width="stretch",
        column_config={ticker: st.column_config.TextColumn(ticker) for ticker in tickers},
    )
