"""Busca avançada de ações: filtros, presets, tabela e comparação."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from ativos.core.linguagem import validar_textos
from ativos.core.presets import PRESETS, SEM_PRESET, aplicar_preset
from ativos.paths import caminho_acoes, caminho_meta_acoes
from ativos.ui.pagina_ativos import AVISO
from focuslens.ui.ui_estilos import aplicar_estilos

METRICAS: dict[str, dict[str, str]] = {
    "preco": {
        "rotulo": "Preço",
        "grupo": "Liquidez e tamanho",
        "formato": "moeda",
        "descricao": "Último fechamento disponível do ticker.",
    },
    "valor_mercado": {
        "rotulo": "Valor de mercado (R$)",
        "grupo": "Liquidez e tamanho",
        "formato": "reais_abreviado",
        "descricao": "Soma do preço de cada classe pela quantidade de ações da classe.",
    },
    "liquidez_media_diaria": {
        "rotulo": "Liquidez/dia (R$)",
        "grupo": "Liquidez e tamanho",
        "formato": "reais_abreviado",
        "descricao": "Volume financeiro médio dos últimos 63 pregões.",
    },
    "lpa": {
        "rotulo": "LPA",
        "grupo": "Valuation",
        "formato": "moeda",
        "descricao": "Lucro dos controladores nos últimos 12 meses dividido pelas ações.",
    },
    "p_l": {
        "rotulo": "P/L",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Valor de mercado dividido pelo lucro dos últimos 12 meses.",
    },
    "vpa": {
        "rotulo": "VPA",
        "grupo": "Valuation",
        "formato": "moeda",
        "descricao": "Patrimônio líquido dos controladores dividido pelas ações.",
    },
    "p_vp": {
        "rotulo": "P/VP",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Valor de mercado dividido pelo patrimônio líquido dos controladores.",
    },
    "dy": {
        "rotulo": "DY",
        "grupo": "Valuation",
        "formato": "percentual",
        "descricao": "Dividendos e JCP pagos nos últimos 12 meses divididos pelo valor de mercado.",
    },
    "peg": {
        "rotulo": "PEG",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "P/L dividido pelo CAGR de lucros em pontos percentuais.",
    },
    "p_ativos": {
        "rotulo": "P/Ativos",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Valor de mercado dividido pelo ativo total.",
    },
    "p_cap_giro": {
        "rotulo": "P/Cap. giro",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Valor de mercado dividido por ativo circulante menos passivo circulante.",
    },
    "p_ativo_circ_liq": {
        "rotulo": "P/ACL",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Valor de mercado dividido por ativo circulante menos passivo exigível.",
    },
    "psr": {
        "rotulo": "PSR",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Valor de mercado dividido pela receita dos últimos 12 meses.",
    },
    "p_ebit": {
        "rotulo": "P/EBIT",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Valor de mercado dividido pelo EBIT dos últimos 12 meses.",
    },
    "ev_ebit": {
        "rotulo": "EV/EBIT",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Valor de mercado mais dívida líquida, dividido pelo EBIT.",
    },
    "margem_bruta": {
        "rotulo": "Margem bruta",
        "grupo": "Rentabilidade",
        "formato": "percentual",
        "descricao": "Resultado bruto dividido pela receita dos últimos 12 meses.",
    },
    "margem_ebit": {
        "rotulo": "Margem EBIT",
        "grupo": "Rentabilidade",
        "formato": "percentual",
        "descricao": "EBIT dividido pela receita dos últimos 12 meses.",
    },
    "margem_liquida": {
        "rotulo": "Margem líquida",
        "grupo": "Rentabilidade",
        "formato": "percentual",
        "descricao": "Lucro dos controladores dividido pela receita dos últimos 12 meses.",
    },
    "roe": {
        "rotulo": "ROE",
        "grupo": "Rentabilidade",
        "formato": "percentual",
        "descricao": "Lucro dos controladores dividido pelo patrimônio dos controladores.",
    },
    "roa": {
        "rotulo": "ROA",
        "grupo": "Rentabilidade",
        "formato": "percentual",
        "descricao": "Lucro dos controladores dividido pelo ativo total.",
    },
    "roic": {
        "rotulo": "ROIC",
        "grupo": "Rentabilidade",
        "formato": "percentual",
        "descricao": "EBIT após alíquota de 34% dividido pelo capital investido.",
    },
    "giro_ativos": {
        "rotulo": "Giro de ativos",
        "grupo": "Rentabilidade",
        "formato": "multiplo",
        "descricao": "Receita dos últimos 12 meses dividida pelo ativo total.",
    },
    "divida_bruta": {
        "rotulo": "Dívida bruta (R$)",
        "grupo": "Endividamento",
        "formato": "reais_abreviado",
        "descricao": "Empréstimos de curto e longo prazo.",
    },
    "divida_liquida": {
        "rotulo": "Dívida líquida (R$)",
        "grupo": "Endividamento",
        "formato": "reais_abreviado",
        "descricao": "Dívida bruta menos caixa e aplicações financeiras.",
    },
    "div_liq_ebit": {
        "rotulo": "Dív. líq./EBIT",
        "grupo": "Endividamento",
        "formato": "multiplo",
        "descricao": "Dívida líquida dividida pelo EBIT dos últimos 12 meses.",
    },
    "div_liq_patrimonio": {
        "rotulo": "Dív. líq./PL",
        "grupo": "Endividamento",
        "formato": "multiplo",
        "descricao": "Dívida líquida dividida pelo patrimônio dos controladores.",
    },
    "liquidez_corrente": {
        "rotulo": "Liquidez corrente",
        "grupo": "Endividamento",
        "formato": "multiplo",
        "descricao": "Ativo circulante dividido pelo passivo circulante.",
    },
    "patrimonio_ativos": {
        "rotulo": "Patrimônio/Ativos",
        "grupo": "Endividamento",
        "formato": "percentual",
        "descricao": "Patrimônio dos controladores dividido pelo ativo total.",
    },
    "passivos_ativos": {
        "rotulo": "Passivos/Ativos",
        "grupo": "Endividamento",
        "formato": "percentual",
        "descricao": "Ativo total menos PL consolidado, dividido pelo ativo total.",
    },
    "cagr_receitas_5a": {
        "rotulo": "CAGR receitas 5a",
        "grupo": "Crescimento",
        "formato": "percentual",
        "descricao": "Crescimento anual composto da receita entre os últimos cinco exercícios.",
    },
    "cagr_lucros_5a": {
        "rotulo": "CAGR lucros 5a",
        "grupo": "Crescimento",
        "formato": "percentual",
        "descricao": "Crescimento anual composto do lucro entre os últimos cinco exercícios.",
    },
}

GRUPOS = tuple(dict.fromkeys(metrica["grupo"] for metrica in METRICAS.values()))
TEXTOS_UI = validar_textos(
    [
        "Busca avançada",
        "Compare indicadores fundamentalistas com filtros transparentes.",
        "Filtros",
        "Setores",
        "Liquidez mínima diária (R$)",
        "Excluir financeiras",
        "Ocultar linhas com alertas de dados",
        "Preset",
        "Grupos de colunas",
        "Indicadores com faixa",
        "Comparador",
        "Selecione até 5 tickers",
        "Exportar CSV",
        "A base derivada ainda não existe.",
        AVISO,
        *PRESETS,
        *(
            item
            for metrica in METRICAS.values()
            for item in (metrica["rotulo"], metrica["descricao"])
        ),
    ]
)


@st.cache_data(show_spinner=False)
def carregar_acoes(caminho: str) -> pd.DataFrame:
    """Carrega a tabela derivada; o caminho participa da chave do cache."""
    return pd.read_parquet(caminho)


@st.cache_data(show_spinner=False)
def carregar_meta(caminho: str) -> dict[str, object]:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def aplicar_filtros(
    quadro: pd.DataFrame,
    *,
    setores: Sequence[str] = (),
    liquidez_minima: float = 0,
    excluir_financeiras: bool = False,
    ocultar_alertas: bool = False,
    faixas: Mapping[str, tuple[float | None, float | None]] | None = None,
    preset: str = SEM_PRESET,
) -> pd.DataFrame:
    """Aplica filtros inclusivos; NaN fica fora quando a faixa exige o indicador."""
    resultado = quadro.copy()
    if setores:
        resultado = resultado[resultado["setor"].isin(setores)]
    resultado = resultado[resultado["liquidez_media_diaria"].ge(liquidez_minima)]
    if excluir_financeiras:
        resultado = resultado[~resultado["financeira"].fillna(False)]
    if ocultar_alertas:
        resultado = resultado[
            resultado["alertas"].map(lambda valor: len(_alertas(valor)) == 0)
        ]
    for coluna, (minimo, maximo) in (faixas or {}).items():
        if minimo is not None:
            resultado = resultado[resultado[coluna].ge(minimo)]
        if maximo is not None:
            resultado = resultado[resultado[coluna].le(maximo)]
    return aplicar_preset(resultado, preset)


def _alertas(valor: object) -> list[str]:
    if isinstance(valor, np.ndarray):
        return [str(item) for item in valor.tolist()]
    if isinstance(valor, (list, tuple)):
        return [str(item) for item in valor]
    if valor is None or pd.isna(valor):
        return []
    return [str(valor)]


def colunas_dos_grupos(grupos: Sequence[str]) -> list[str]:
    return [coluna for coluna, metrica in METRICAS.items() if metrica["grupo"] in grupos]


def exportar_csv(quadro: pd.DataFrame) -> bytes:
    exportacao = quadro.copy()
    if "alertas" in exportacao:
        exportacao["alertas"] = exportacao["alertas"].map(
            lambda valor: ", ".join(_alertas(valor))
        )
    return exportacao.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")


def _configuracao_colunas(colunas: Sequence[str]) -> dict[str, object]:
    configuracao: dict[str, object] = {
        "ticker": st.column_config.TextColumn("Ticker", pinned=True, help="Código de negociação."),
        "empresa": st.column_config.TextColumn("Empresa", help="Denominação cadastral."),
        "setor": st.column_config.TextColumn("Setor", help="Setor informado no cadastro da CVM."),
        "financeira": st.column_config.CheckboxColumn(
            "Financeira", help="Setor financeiro ou balanço sem Ativo Circulante."
        ),
        "data_balanco": st.column_config.DateColumn(
            "Balanço", help="Data da posição contábil mais recente disponível."
        ),
        "alertas": st.column_config.ListColumn(
            "Alertas", help="Sinais de escala, preço ou casamento de cadastro."
        ),
    }
    formatos = {
        "moeda": "R$ %.2f",
        "reais_abreviado": "compact",
        "percentual": "percent",
        "multiplo": "%.2f",
    }
    for coluna in colunas:
        metrica = METRICAS[coluna]
        configuracao[coluna] = st.column_config.NumberColumn(
            metrica["rotulo"],
            help=metrica["descricao"],
            format=formatos[metrica["formato"]],
        )
    return configuracao


def _formatar_comparacao(valor: object, formato: str) -> str:
    if pd.isna(valor):
        return "—"
    numero = float(valor)
    if formato == "percentual":
        return f"{numero:.2%}".replace(".", ",")
    if formato == "moeda":
        return f"R$ {numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if formato == "reais_abreviado":
        for divisor, sufixo in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(numero) >= divisor:
                return f"R$ {numero / divisor:.2f} {sufixo}".replace(".", ",")
        return f"R$ {numero:.2f}".replace(".", ",")
    return f"{numero:.2f}".replace(".", ",")


def _renderizar_faixas(quadro: pd.DataFrame) -> dict[str, tuple[float, float]]:
    escolhidas = st.multiselect(
        "Indicadores com faixa",
        options=list(METRICAS),
        format_func=lambda coluna: METRICAS[coluna]["rotulo"],
        help="Valores ausentes não entram quando uma faixa está ativa.",
    )
    faixas = {}
    for coluna in escolhidas:
        serie = pd.to_numeric(quadro[coluna], errors="coerce").dropna()
        if serie.empty:
            st.caption(f"{METRICAS[coluna]['rotulo']}: sem dados para limitar.")
            continue
        minimo_real = float(serie.min())
        maximo_real = float(serie.max())
        col_min, col_max = st.columns(2)
        with col_min:
            minimo = st.number_input(
                f"{METRICAS[coluna]['rotulo']} · mínimo",
                value=minimo_real,
                key=f"faixa_min_{coluna}",
            )
        with col_max:
            maximo = st.number_input(
                f"{METRICAS[coluna]['rotulo']} · máximo",
                value=maximo_real,
                key=f"faixa_max_{coluna}",
            )
        faixas[coluna] = (float(minimo), float(maximo))
    return faixas


def render() -> None:
    st.set_page_config(
        page_title="Busca avançada · Lastro",
        page_icon=":material/table_view:",
        layout="wide",
    )
    aplicar_estilos()
    st.title("Busca avançada")
    st.write("Compare indicadores fundamentalistas com filtros transparentes.")
    st.caption(AVISO)

    parquet = caminho_acoes()
    meta_path = caminho_meta_acoes()
    if not parquet.exists():
        st.info(
            "A base derivada ainda não existe. Execute `python -m scripts.atualizar_ativos` "
            "para gerar `acoes.parquet`."
        )
        return
    quadro = carregar_acoes(str(parquet))
    meta = carregar_meta(str(meta_path)) if meta_path.exists() else {}
    total = len(quadro)

    with st.expander("Filtros", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            setores_disponiveis = sorted(quadro["setor"].dropna().astype(str).unique())
            setores = st.multiselect("Setores", setores_disponiveis)
            liquidez_minima = st.number_input(
                "Liquidez mínima diária (R$)", min_value=0.0, value=0.0, step=50_000.0
            )
        with col_b:
            excluir_financeiras = st.checkbox("Excluir financeiras")
            ocultar_alertas = st.checkbox("Ocultar linhas com alertas de dados")
            preset = st.selectbox("Preset", PRESETS)
        with col_c:
            grupos = st.multiselect("Grupos de colunas", GRUPOS, default=list(GRUPOS))
        faixas = _renderizar_faixas(quadro)

    filtrado = aplicar_filtros(
        quadro,
        setores=setores,
        liquidez_minima=liquidez_minima,
        excluir_financeiras=excluir_financeiras,
        ocultar_alertas=ocultar_alertas,
        faixas=faixas,
        preset=preset,
    )
    topo_a, topo_b, topo_c = st.columns(3)
    topo_a.metric("Data da cotação", meta.get("data_cotacao", "—"))
    topo_b.metric("Base gerada", str(meta.get("gerado_em", "—"))[:19].replace("T", " "))
    topo_c.metric("Exibidos", f"{len(filtrado)} de {total}")

    colunas_metricas = colunas_dos_grupos(grupos)
    # Ticker fixo à esquerda e indicadores logo depois; o cadastro vai para o fim.
    colunas_cadastro = ["empresa", "setor", "financeira", "data_balanco", "alertas"]
    colunas_visiveis = [
        coluna
        for coluna in ["ticker", *colunas_metricas, *colunas_cadastro]
        if coluna in filtrado
    ]
    st.dataframe(
        filtrado[colunas_visiveis],
        hide_index=True,
        width="stretch",
        height=620,
        column_config=_configuracao_colunas(colunas_metricas),
        placeholder="—",
    )
    st.download_button(
        "Exportar CSV",
        data=exportar_csv(filtrado[colunas_visiveis]),
        file_name="lastro_busca_acoes.csv",
        mime="text/csv",
    )

    st.subheader("Comparador")
    tickers = st.multiselect(
        "Selecione até 5 tickers",
        filtrado["ticker"].tolist(),
        max_selections=5,
        key="comparador_tickers",
    )
    if tickers:
        comparacao = filtrado[filtrado["ticker"].isin(tickers)].set_index("ticker")
        linhas = {}
        for coluna in colunas_metricas:
            linhas[METRICAS[coluna]["rotulo"]] = [
                _formatar_comparacao(comparacao.at[ticker, coluna], METRICAS[coluna]["formato"])
                for ticker in tickers
            ]
        st.dataframe(
            pd.DataFrame(linhas, index=tickers).T,
            width="stretch",
            column_config={ticker: st.column_config.TextColumn(ticker) for ticker in tickers},
        )
