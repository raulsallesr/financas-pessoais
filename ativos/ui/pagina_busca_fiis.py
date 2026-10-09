"""Busca de FIIs: filtros, presets, tabela, comparação e exportação."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pandas as pd
import streamlit as st

from ativos.core.linguagem import validar_textos
from ativos.core.presets_fiis import PRESETS_FIIS, SEM_PRESET_FII, aplicar_preset_fii
from ativos.paths import caminho_fiis, caminho_meta_fiis
from ativos.ui.componentes_tabela import (
    alertas,
    configuracao_metricas,
    renderizar_comparador,
    renderizar_tabela_e_csv,
)
from ativos.ui.pagina_ativos import AVISO
from focuslens.ui.ui_estilos import aplicar_estilos

METRICAS_FII: dict[str, dict[str, str]] = {
    "preco": {
        "rotulo": "Preço",
        "grupo": "Liquidez e tamanho",
        "formato": "moeda",
        "descricao": "Último fechamento disponível da cota.",
    },
    "valor_mercado": {
        "rotulo": "Valor de mercado (R$)",
        "grupo": "Liquidez e tamanho",
        "formato": "reais_abreviado",
        "descricao": "Preço da cota multiplicado pelas cotas emitidas do último informe.",
    },
    "liquidez_media_diaria": {
        "rotulo": "Liquidez/dia (R$)",
        "grupo": "Liquidez e tamanho",
        "formato": "reais_abreviado",
        "descricao": "Volume financeiro médio dos últimos 63 pregões.",
    },
    "patrimonio_liquido": {
        "rotulo": "Patrimônio líquido (R$)",
        "grupo": "Liquidez e tamanho",
        "formato": "reais_abreviado",
        "descricao": "Patrimônio líquido do último informe mensal da classe.",
    },
    "cotas_emitidas": {
        "rotulo": "Cotas emitidas",
        "grupo": "Liquidez e tamanho",
        "formato": "inteiro",
        "descricao": "Quantidade de cotas emitidas no último informe mensal.",
    },
    "cotistas": {
        "rotulo": "Cotistas",
        "grupo": "Liquidez e tamanho",
        "formato": "inteiro",
        "descricao": "Total de cotistas informado no mês de referência.",
    },
    "vp_cota": {
        "rotulo": "VP/cota",
        "grupo": "Valuation",
        "formato": "moeda",
        "descricao": "Valor patrimonial por cota do último informe mensal.",
    },
    "p_vp": {
        "rotulo": "P/VP",
        "grupo": "Valuation",
        "formato": "multiplo",
        "descricao": "Preço da cota dividido pelo valor patrimonial por cota.",
    },
    "dy_12m": {
        "rotulo": "DY 12m",
        "grupo": "Renda",
        "formato": "percentual",
        "descricao": "Rendimentos por cota dos últimos 12 informes divididos pelo preço atual.",
    },
    "dy_ultimo_mes": {
        "rotulo": "DY último mês anualizado",
        "grupo": "Renda",
        "formato": "percentual",
        "descricao": "Rendimento por cota do último mês, anualizado, dividido pelo preço atual.",
    },
    "rendimento_ultimo_mes": {
        "rotulo": "Rendimento último mês",
        "grupo": "Renda",
        "formato": "moeda",
        "descricao": "Percentual de dividend yield do mês multiplicado pelo VP por cota.",
    },
    "rentab_12m": {
        "rotulo": "Rentabilidade efetiva 12m",
        "grupo": "Renda",
        "formato": "percentual",
        "descricao": "Produto das rentabilidades efetivas dos 12 últimos informes, menos um.",
    },
    "taxa_adm": {
        "rotulo": "Taxa de administração",
        "grupo": "Renda",
        "formato": "percentual",
        "descricao": "Despesa de administração do mês como fração do patrimônio líquido.",
    },
    "pct_imoveis": {
        "rotulo": "Imóveis",
        "grupo": "Qualidade da carteira",
        "formato": "percentual",
        "descricao": "Parcela do total investido ligada a imóveis e sociedades do FII.",
    },
    "pct_recebiveis": {
        "rotulo": "Recebíveis",
        "grupo": "Qualidade da carteira",
        "formato": "percentual",
        "descricao": "Parcela do total investido em recebíveis e instrumentos relacionados.",
    },
    "pct_cotas_fundos": {
        "rotulo": "Cotas de fundos",
        "grupo": "Qualidade da carteira",
        "formato": "percentual",
        "descricao": "Parcela do total investido em cotas de fundos.",
    },
    "vacancia": {
        "rotulo": "Vacância",
        "grupo": "Qualidade da carteira",
        "formato": "percentual",
        "descricao": "Vacância média dos imóveis, ponderada pela participação quando disponível.",
    },
    "inadimplencia": {
        "rotulo": "Inadimplência",
        "grupo": "Qualidade da carteira",
        "formato": "percentual",
        "descricao": "Inadimplência média dos imóveis na posição trimestral mais recente.",
    },
    "num_imoveis": {
        "rotulo": "Imóveis distintos",
        "grupo": "Qualidade da carteira",
        "formato": "inteiro",
        "descricao": "Quantidade de nomes de imóveis distintos no informe trimestral mais recente.",
    },
    "concentracao_top_imovel": {
        "rotulo": "Maior imóvel",
        "grupo": "Qualidade da carteira",
        "formato": "percentual",
        "descricao": "Maior participação individual de imóvel no total investido.",
    },
    "passivo_ativo": {
        "rotulo": "Passivo/Ativo",
        "grupo": "Qualidade da carteira",
        "formato": "percentual",
        "descricao": "Passivo total dividido pelo valor do ativo no último informe mensal.",
    },
}

GRUPOS_FII = tuple(dict.fromkeys(item["grupo"] for item in METRICAS_FII.values()))
TEXTOS_UI_FII = validar_textos(
    [
        "Busca de FIIs",
        "Explore fundos imobiliários com critérios transparentes e dados oficiais.",
        "Filtros",
        "Tipos",
        "Segmentos",
        "P/VP mínimo",
        "P/VP máximo",
        "DY 12m mínimo (%)",
        "Vacância máxima (%)",
        "Liquidez mínima diária (R$)",
        "Ocultar fundos com alertas de dados",
        "Preset",
        "Grupos de colunas",
        "Comparador",
        "Selecione até 5 tickers",
        "Exportar CSV",
        "A base derivada de FIIs ainda não existe.",
        AVISO,
        *PRESETS_FIIS,
        *(
            texto
            for metrica in METRICAS_FII.values()
            for texto in (metrica["rotulo"], metrica["descricao"])
        ),
    ]
)


@st.cache_data(show_spinner=False)
def carregar_fiis(caminho: str) -> pd.DataFrame:
    return pd.read_parquet(caminho)


@st.cache_data(show_spinner=False)
def carregar_meta_fiis(caminho: str) -> dict[str, object]:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def _faixa(
    quadro: pd.DataFrame,
    coluna: str,
    limites: tuple[float | None, float | None],
) -> pd.DataFrame:
    minimo, maximo = limites
    resultado = quadro
    if minimo is not None:
        resultado = resultado[resultado[coluna].ge(minimo)]
    if maximo is not None:
        resultado = resultado[resultado[coluna].le(maximo)]
    return resultado


def aplicar_filtros_fiis(
    quadro: pd.DataFrame,
    *,
    tipos: Sequence[str] = (),
    segmentos: Sequence[str] = (),
    p_vp: tuple[float | None, float | None] = (None, None),
    dy_12m: tuple[float | None, float | None] = (None, None),
    vacancia: tuple[float | None, float | None] = (None, None),
    liquidez_minima: float = 0,
    ocultar_alertas: bool = False,
    preset: str = SEM_PRESET_FII,
) -> pd.DataFrame:
    """Aplica filtros próprios de FII; NaN não satisfaz uma faixa ativa."""
    resultado = quadro.copy()
    if tipos:
        resultado = resultado[resultado["tipo"].isin(tipos)]
    if segmentos:
        resultado = resultado[resultado["segmento"].isin(segmentos)]
    resultado = resultado[resultado["liquidez_media_diaria"].ge(liquidez_minima)]
    resultado = _faixa(resultado, "p_vp", p_vp)
    resultado = _faixa(resultado, "dy_12m", dy_12m)
    resultado = _faixa(resultado, "vacancia", vacancia)
    if ocultar_alertas:
        resultado = resultado[resultado["alertas"].map(lambda valor: not alertas(valor))]
    return aplicar_preset_fii(resultado, preset)


def colunas_dos_grupos_fii(grupos: Sequence[str]) -> list[str]:
    return [
        coluna for coluna, metrica in METRICAS_FII.items() if metrica["grupo"] in grupos
    ]


def _configuracao_colunas(colunas: Sequence[str]) -> dict[str, object]:
    configuracao: dict[str, object] = {
        "ticker": st.column_config.TextColumn("Ticker", pinned=True, help="Código de negociação."),
        "nome": st.column_config.TextColumn("Fundo", help="Nome cadastral da classe na CVM."),
        "cnpj": st.column_config.TextColumn("CNPJ", help="CNPJ da classe do fundo."),
        "segmento": st.column_config.TextColumn(
            "Segmento", help="Segmento autodeclarado no informe mensal."
        ),
        "tipo": st.column_config.TextColumn(
            "Tipo", help="Classificação calculada a partir da composição do total investido."
        ),
        "gestao": st.column_config.TextColumn("Gestão", help="Tipo de gestão declarado."),
        "meses_informe": st.column_config.NumberColumn(
            "Meses de informe", help="Quantidade de meses disponíveis para o fundo.", format="%d"
        ),
        "data_informe": st.column_config.DateColumn(
            "Informe", help="Mês de referência mais recente usado nos indicadores."
        ),
        "alertas": st.column_config.ListColumn(
            "Alertas", help="Sinais de cobertura, defasagem ou dado extremo."
        ),
    }
    configuracao.update(configuracao_metricas(METRICAS_FII, colunas))
    return configuracao


def _percentual_ou_none(valor: float | None) -> float | None:
    return valor / 100 if valor is not None else None


def render() -> None:
    st.set_page_config(
        page_title="Busca de FIIs · Lastro",
        page_icon=":material/apartment:",
        layout="wide",
    )
    aplicar_estilos()
    st.title("Busca de FIIs")
    st.write("Explore fundos imobiliários com critérios transparentes e dados oficiais.")
    st.caption(AVISO)

    parquet = caminho_fiis()
    meta_path = caminho_meta_fiis()
    if not parquet.exists():
        st.info(
            "A base derivada de FIIs ainda não existe. Execute "
            "`python -m scripts.atualizar_ativos --classe fiis` para gerar `fiis.parquet`."
        )
        return
    quadro = carregar_fiis(str(parquet))
    meta = carregar_meta_fiis(str(meta_path)) if meta_path.exists() else {}
    total = len(quadro)

    with st.expander("Filtros", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            tipos = st.multiselect("Tipos", sorted(quadro["tipo"].dropna().unique()))
            segmentos = st.multiselect(
                "Segmentos", sorted(quadro["segmento"].dropna().astype(str).unique())
            )
            liquidez_minima = st.number_input(
                "Liquidez mínima diária (R$)", min_value=0.0, value=0.0, step=50_000.0
            )
        with col_b:
            p_vp_min = st.number_input("P/VP mínimo", value=None, placeholder="Sem limite")
            p_vp_max = st.number_input("P/VP máximo", value=None, placeholder="Sem limite")
            dy_min = st.number_input("DY 12m mínimo (%)", value=None, placeholder="Sem limite")
            vacancia_max = st.number_input(
                "Vacância máxima (%)", value=None, placeholder="Sem limite"
            )
        with col_c:
            ocultar_alertas = st.checkbox("Ocultar fundos com alertas de dados")
            preset = st.selectbox("Preset", PRESETS_FIIS)
            grupos = st.multiselect(
                "Grupos de colunas", GRUPOS_FII, default=list(GRUPOS_FII)
            )

    filtrado = aplicar_filtros_fiis(
        quadro,
        tipos=tipos,
        segmentos=segmentos,
        p_vp=(p_vp_min, p_vp_max),
        dy_12m=(_percentual_ou_none(dy_min), None),
        vacancia=(None, _percentual_ou_none(vacancia_max)),
        liquidez_minima=liquidez_minima,
        ocultar_alertas=ocultar_alertas,
        preset=preset,
    )
    topo_a, topo_b, topo_c = st.columns(3)
    topo_a.metric("Data da cotação", meta.get("data_cotacao", "—"))
    topo_b.metric("Base gerada", str(meta.get("gerado_em", "—"))[:19].replace("T", " "))
    topo_c.metric("Exibidos", f"{len(filtrado)} de {total}")

    colunas_metricas = colunas_dos_grupos_fii(grupos)
    cadastro = [
        "nome",
        "cnpj",
        "segmento",
        "tipo",
        "gestao",
        "meses_informe",
        "data_informe",
        "alertas",
    ]
    colunas_visiveis = [
        coluna
        for coluna in ["ticker", *colunas_metricas, *cadastro]
        if coluna in filtrado
    ]
    renderizar_tabela_e_csv(
        filtrado,
        colunas_visiveis,
        configuracao=_configuracao_colunas(colunas_metricas),
        arquivo="lastro_busca_fiis.csv",
    )
    renderizar_comparador(
        filtrado,
        colunas_metricas,
        METRICAS_FII,
        key="comparador_tickers_fiis",
    )
