"""Ficha unificada de ações e FIIs com faixa, modelos e comparações."""

from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from ativos.core.linguagem import validar_textos
from ativos.core.valuation import (
    calcular_valuation_acoes,
    calcular_valuation_fiis,
    sensibilidade_gordon,
    sensibilidade_taxa,
    tabela_modelos_acao,
    tabela_modelos_fii,
)
from ativos.paths import (
    caminho_acoes,
    caminho_fiis,
    caminho_meta_acoes,
    caminho_meta_fiis,
)
from ativos.ui.componentes_tabela import alertas, formatar_comparacao
from ativos.ui.pagina_ativos import AVISO
from ativos.ui.premissas_valuation import renderizar_premissas
from focuslens.ui.ui_estilos import aplicar_estilos

INDICADORES_ACOES = {
    "p_l": ("P/L", "multiplo"),
    "p_vp": ("P/VP", "multiplo"),
    "dy": ("DY", "percentual"),
    "roe": ("ROE", "percentual"),
    "margem_liquida": ("Margem líquida", "percentual"),
    "div_liq_ebit": ("Dívida líquida/EBIT", "multiplo"),
}
INDICADORES_FIIS = {
    "p_vp": ("P/VP", "multiplo"),
    "dy_12m": ("DY 12m", "percentual"),
    "vacancia": ("Vacância", "percentual"),
    "cotistas": ("Cotistas", "inteiro"),
}
TEXTOS_UI_FICHA = validar_textos(
    [
        "Ficha do ativo",
        "Selecione uma ação ou FII e abra os modelos que formam a faixa estimada.",
        "Ativo",
        "Faixa de valor",
        "Dados insuficientes: menos de dois modelos aplicáveis.",
        "Tabela dos modelos",
        "Sensibilidade",
        "Gordon: custo do capital próprio × crescimento",
        "Bazin: taxa mínima",
        "Renda capitalizada: taxa exigida",
        "Indicadores-chave versus o setor",
        "Alertas de dados",
        "Nenhum derivado de ações ou FIIs foi encontrado.",
        AVISO,
    ]
)


@st.cache_data(show_spinner=False)
def _carregar_parquet(caminho: str) -> pd.DataFrame:
    return pd.read_parquet(caminho)


@st.cache_data(show_spinner=False)
def _carregar_meta(caminho: str) -> dict[str, object]:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def _formatar_moeda(valor: object) -> str:
    return formatar_comparacao(valor, "moeda")


def _opcoes(acoes: pd.DataFrame, fiis: pd.DataFrame) -> tuple[list[str], dict[str, str]]:
    chaves = []
    rotulos = {}
    if not acoes.empty:
        for linha in acoes.sort_values("ticker", kind="stable").to_dict(orient="records"):
            chave = f"acao::{linha['ticker']}"
            chaves.append(chave)
            rotulos[chave] = f"[Ação] {linha['ticker']} · {linha.get('empresa', '—')}"
    if not fiis.empty:
        for linha in fiis.sort_values("ticker", kind="stable").to_dict(orient="records"):
            chave = f"fii::{linha['ticker']}"
            chaves.append(chave)
            rotulos[chave] = f"[FII] {linha['ticker']} · {linha.get('nome', '—')}"
    return chaves, rotulos


def _grafico_faixa(linha: pd.Series) -> None:
    faixa_baixa = linha.get("faixa_baixa")
    faixa_alta = linha.get("faixa_alta")
    if pd.isna(faixa_baixa) or pd.isna(faixa_alta):
        st.info("Dados insuficientes: menos de dois modelos aplicáveis.")
        return
    faixa = pd.DataFrame(
        [{"faixa_baixa": faixa_baixa, "faixa_alta": faixa_alta, "eixo": "Valor"}]
    )
    pontos = pd.DataFrame(
        [
            {"Valor": linha["valor_central"], "Referência": "Valor central"},
            {"Valor": linha["preco"], "Referência": "Preço atual"},
        ]
    )
    escala = alt.Scale(zero=False)
    intervalo = (
        alt.Chart(faixa)
        .mark_rule(color="#5ea99f", strokeWidth=14)
        .encode(
            x=alt.X("faixa_baixa:Q", title="R$ por ação ou cota", scale=escala),
            x2="faixa_alta:Q",
            tooltip=[
                alt.Tooltip("faixa_baixa:Q", title="Faixa baixa", format=".2f"),
                alt.Tooltip("faixa_alta:Q", title="Faixa alta", format=".2f"),
            ],
        )
    )
    marcas = (
        alt.Chart(pontos)
        .mark_point(filled=True, size=150)
        .encode(
            x=alt.X("Valor:Q", scale=escala),
            color=alt.Color(
                "Referência:N",
                scale=alt.Scale(
                    domain=["Valor central", "Preço atual"],
                    range=["#0f766e", "#a16207"],
                ),
            ),
            shape=alt.Shape("Referência:N"),
            tooltip=["Referência:N", alt.Tooltip("Valor:Q", format=".2f")],
        )
    )
    st.altair_chart((intervalo + marcas).properties(height=110), use_container_width=True)
    margem = formatar_comparacao(linha.get("margem_seguranca"), "percentual")
    st.write(
        f"Faixa: {_formatar_moeda(faixa_baixa)} a {_formatar_moeda(faixa_alta)} · "
        f"valor central {_formatar_moeda(linha.get('valor_central'))} · "
        f"margem calculada {margem} · {linha.get('situacao_faixa')}."
    )


def _percentil(serie: pd.Series, valor: object) -> float:
    numeros = pd.to_numeric(serie, errors="coerce").dropna()
    if numeros.empty or pd.isna(valor):
        return np.nan
    return float(numeros.le(float(valor)).mean())


def indicadores_setor(
    quadro: pd.DataFrame,
    linha: pd.Series,
    *,
    classe: str,
) -> pd.DataFrame:
    """Compara o ativo com empresas distintas ou fundos do mesmo segmento."""
    if classe == "acao":
        if bool(linha.get("financeira", False)):
            pares = quadro[quadro["financeira"].fillna(False)].copy()
        else:
            pares = quadro[
                ~quadro["financeira"].fillna(False) & quadro["setor"].eq(linha.get("setor"))
            ].copy()
        pares = pares.drop_duplicates("cnpj", keep="first")
        indicadores = INDICADORES_ACOES
    else:
        pares = quadro[quadro["segmento"].eq(linha.get("segmento"))].copy()
        indicadores = INDICADORES_FIIS
    linhas = []
    for coluna, (rotulo, formato) in indicadores.items():
        serie = pd.to_numeric(pares.get(coluna), errors="coerce")
        valor = pd.to_numeric(pd.Series([linha.get(coluna)]), errors="coerce").iloc[0]
        mediana = serie.median() if serie.notna().any() else np.nan
        linhas.append(
            {
                "Indicador": rotulo,
                "Ativo": formatar_comparacao(valor, formato),
                "Mediana do setor": formatar_comparacao(mediana, formato),
                "Percentil": formatar_comparacao(_percentil(serie, valor), "percentual"),
            }
        )
    return pd.DataFrame(linhas)


def _renderizar_modelos(linha: pd.Series, *, classe: str, premissas) -> None:
    st.subheader("Tabela dos modelos")
    modelos = (
        tabela_modelos_acao(linha, premissas)
        if classe == "acao"
        else tabela_modelos_fii(linha, premissas)
    )
    st.dataframe(
        modelos,
        hide_index=True,
        width="stretch",
        column_config={"Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")},
        placeholder="—",
    )


def _renderizar_sensibilidade(linha: pd.Series, *, classe: str, premissas) -> None:
    st.subheader("Sensibilidade")
    if classe == "acao":
        coluna_gordon, coluna_bazin = st.columns(2)
        with coluna_gordon:
            st.write("Gordon: custo do capital próprio × crescimento")
            st.dataframe(
                sensibilidade_gordon(linha.get("dpa"), premissas),
                width="stretch",
                column_config={
                    coluna: st.column_config.NumberColumn(coluna, format="R$ %.2f")
                    for coluna in sensibilidade_gordon(linha.get("dpa"), premissas).columns
                },
                placeholder="—",
            )
        with coluna_bazin:
            st.write("Bazin: taxa mínima")
            st.dataframe(
                sensibilidade_taxa(linha.get("dpa"), premissas.bazin_taxa),
                hide_index=True,
                width="stretch",
                column_config={
                    "Taxa": st.column_config.NumberColumn("Taxa", format="percent"),
                    "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                },
                placeholder="—",
            )
    else:
        st.write("Renda capitalizada: taxa exigida")
        st.dataframe(
            sensibilidade_taxa(
                linha.get("rendimento_12m_cota"), premissas.fii_taxa_exigida
            ),
            hide_index=True,
            width="stretch",
            column_config={
                "Taxa": st.column_config.NumberColumn("Taxa", format="percent"),
                "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            },
            placeholder="—",
        )


def render() -> None:
    st.set_page_config(
        page_title="Ficha do ativo · Lastro",
        page_icon=":material/finance_mode:",
        layout="wide",
    )
    aplicar_estilos()
    st.title("Ficha do ativo")
    st.write("Selecione uma ação ou FII e abra os modelos que formam a faixa estimada.")
    st.caption(AVISO)

    arquivo_acoes = caminho_acoes()
    arquivo_fiis = caminho_fiis()
    acoes = _carregar_parquet(str(arquivo_acoes)) if arquivo_acoes.exists() else pd.DataFrame()
    fiis = _carregar_parquet(str(arquivo_fiis)) if arquivo_fiis.exists() else pd.DataFrame()
    if acoes.empty and fiis.empty:
        st.info(
            "Nenhum derivado de ações ou FIIs foi encontrado. Execute "
            "`python -m scripts.atualizar_ativos --classe todos`."
        )
        return
    premissas = renderizar_premissas()
    opcoes, rotulos = _opcoes(acoes, fiis)
    selecionado = st.selectbox("Ativo", opcoes, format_func=rotulos.get)
    classe, ticker = selecionado.split("::", maxsplit=1)

    if classe == "acao":
        avaliado = calcular_valuation_acoes(acoes, premissas)
        linha = avaliado.loc[avaliado["ticker"].eq(ticker)].iloc[0]
        nome = linha.get("empresa", ticker)
        contexto = linha.get("setor", "Setor não informado")
        meta_path = caminho_meta_acoes()
    else:
        avaliado = calcular_valuation_fiis(fiis, premissas)
        linha = avaliado.loc[avaliado["ticker"].eq(ticker)].iloc[0]
        nome = linha.get("nome", ticker)
        contexto = f"{linha.get('tipo', 'Tipo não informado')} · {linha.get('segmento', '—')}"
        meta_path = caminho_meta_fiis()
    meta = _carregar_meta(str(meta_path)) if meta_path.exists() else {}

    st.header(f"{ticker} · {nome}")
    st.caption(f"{'Ação' if classe == 'acao' else 'FII'} · {contexto}")
    cabecalho_a, cabecalho_b, cabecalho_c = st.columns(3)
    cabecalho_a.metric("Preço atual", _formatar_moeda(linha.get("preco")))
    cabecalho_b.metric("Data da cotação", meta.get("data_cotacao", "—"))
    cabecalho_c.metric("Modelos aplicáveis", int(linha.get("n_modelos", 0)))
    sinais = alertas(linha.get("alertas"))
    if bool(linha.get("valuation_fragil", False)):
        sinais.append("valuation_fragil")
    if sinais:
        st.warning("Alertas de dados: " + ", ".join(sorted(set(sinais))))

    st.subheader("Faixa de valor")
    if classe == "acao":
        st.caption(
            "Graham, Bazin, Gordon e múltiplos do setor medem valor e renda atuais; "
            "não incorporam crescimento acelerado nem ativos intangíveis."
        )
        if bool(linha.get("modelos_valor_limitados", False)):
            st.info(
                "Múltiplos altos (P/L acima de 25 ou P/VP acima de 6): a faixa tende a "
                "ficar abaixo do preço mesmo quando o mercado precifica crescimento. "
                "Leia como referência de valor atual, não como veredito."
            )
    _grafico_faixa(linha)
    _renderizar_modelos(linha, classe=classe, premissas=premissas)
    _renderizar_sensibilidade(linha, classe=classe, premissas=premissas)
    st.subheader("Indicadores-chave versus o setor")
    st.dataframe(
        indicadores_setor(avaliado, linha, classe=classe),
        hide_index=True,
        width="stretch",
    )
