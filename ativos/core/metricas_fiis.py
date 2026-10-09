"""Fórmulas puras usadas pela busca de fundos imobiliários."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd

COLUNAS_IMOVEIS = (
    "Direitos_Bens_Imoveis",
    "Acoes_Sociedades_Atividades_FII",
    "Cotas_Sociedades_Atividades_FII",
)
COLUNAS_RECEBIVEIS = (
    "CRI",
    "CRI_CRA",
    "LCI",
    "LCI_LCA",
    "LIG",
    "Letras_Hipotecarias",
    "Cedulas_Debentures",
    "Debentures",
)
COLUNAS_COTAS_FUNDOS = (
    "FII",
    "Outras_Cotas_FI",
    "Fundo_Acoes",
    "FDIC",
)

COLUNAS_METRICAS_FII = (
    "preco",
    "valor_mercado",
    "liquidez_media_diaria",
    "patrimonio_liquido",
    "cotas_emitidas",
    "vp_cota",
    "p_vp",
    "dy_12m",
    "rendimento_12m_cota",
    "dy_ultimo_mes",
    "rendimento_ultimo_mes",
    "rentab_12m",
    "cotistas",
    "taxa_adm",
    "pct_imoveis",
    "pct_recebiveis",
    "pct_cotas_fundos",
    "vacancia",
    "inadimplencia",
    "num_imoveis",
    "concentracao_top_imovel",
    "passivo_ativo",
)


def _numero(valor: object) -> float:
    convertido = pd.to_numeric(pd.Series([valor]), errors="coerce").iloc[0]
    return float(convertido) if pd.notna(convertido) else np.nan


def divisao_segura(numerador: object, denominador: object) -> float:
    """Divide apenas quando ambos existem e o denominador é positivo."""
    num = _numero(numerador)
    den = _numero(denominador)
    if pd.isna(num) or pd.isna(den) or den <= 0:
        return np.nan
    return num / den


def _somar_disponiveis(linha: Mapping[str, object], colunas: Sequence[str]) -> float:
    valores = pd.to_numeric(pd.Series([linha.get(coluna) for coluna in colunas]), errors="coerce")
    if not valores.notna().any():
        return np.nan
    return float(valores.sum(skipna=True))


def calcular_composicao(linha: Mapping[str, object]) -> dict[str, object]:
    """Calcula os três blocos da carteira e classifica o tipo nos limites de 60%."""
    total = linha.get("Total_Investido")
    pct_imoveis = divisao_segura(_somar_disponiveis(linha, COLUNAS_IMOVEIS), total)
    pct_recebiveis = divisao_segura(_somar_disponiveis(linha, COLUNAS_RECEBIVEIS), total)
    pct_cotas = divisao_segura(_somar_disponiveis(linha, COLUNAS_COTAS_FUNDOS), total)
    tipo = classificar_tipo(pct_imoveis, pct_recebiveis, pct_cotas)
    return {
        "tipo": tipo,
        "pct_imoveis": pct_imoveis,
        "pct_recebiveis": pct_recebiveis,
        "pct_cotas_fundos": pct_cotas,
    }


def classificar_tipo(
    pct_imoveis: object,
    pct_recebiveis: object,
    pct_cotas_fundos: object,
) -> str:
    """Classifica a composição, considerando 60% como parte do respectivo limite."""
    imoveis = _numero(pct_imoveis)
    recebiveis = _numero(pct_recebiveis)
    cotas = _numero(pct_cotas_fundos)
    if pd.notna(imoveis) and imoveis >= 0.60:
        return "Tijolo"
    if pd.notna(recebiveis) and recebiveis >= 0.60:
        return "Papel"
    if pd.notna(cotas) and cotas >= 0.60:
        return "Fundo de fundos"
    if pd.notna(imoveis) and pd.notna(recebiveis) and imoveis + recebiveis >= 0.60:
        return "Híbrido"
    return "Outros"


def calcular_metricas_mensais(historico: pd.DataFrame, preco: object) -> dict[str, object]:
    """Calcula renda e rentabilidade a partir dos últimos 12 informes do fundo."""
    vazio = {
        "dy_12m": np.nan,
        "rendimento_12m_cota": np.nan,
        "dy_ultimo_mes": np.nan,
        "rendimento_ultimo_mes": np.nan,
        "rentab_12m": np.nan,
        "meses_informe": 0,
        "dy_parcial": True,
        "fundo_novo": True,
        "dy_dados_suspeitos": False,
    }
    if historico.empty:
        return vazio

    quadro = historico.copy()
    quadro["Data_Referencia"] = pd.to_datetime(quadro["Data_Referencia"], errors="coerce")
    quadro = quadro.dropna(subset=["Data_Referencia"]).sort_values("Data_Referencia")
    if quadro.empty:
        return vazio
    quadro = quadro.drop_duplicates("Data_Referencia", keep="last")
    meses_informe = len(quadro)
    janela = quadro.tail(12).copy()
    vp = pd.to_numeric(janela["Valor_Patrimonial_Cotas"], errors="coerce")
    dy_mes = pd.to_numeric(janela["Percentual_Dividend_Yield_Mes"], errors="coerce")
    dy_invalido = dy_mes.notna() & ~dy_mes.between(0, 0.05, inclusive="both")
    rendimentos = (vp * dy_mes).mask(dy_invalido)
    validos = rendimentos.dropna()
    quantidade_valida = len(validos)
    preco_numero = _numero(preco)
    if quantidade_valida >= 6 and pd.notna(preco_numero) and preco_numero > 0:
        fator = 12 / quantidade_valida if quantidade_valida < 12 else 1
        rendimento_12m_cota = float(validos.sum() * fator)
        dy_12m = rendimento_12m_cota / preco_numero
    else:
        rendimento_12m_cota = np.nan
        dy_12m = np.nan

    rendimento_ultimo = rendimentos.iloc[-1]
    if pd.isna(rendimento_ultimo):
        rendimento_ultimo = np.nan
    else:
        rendimento_ultimo = float(rendimento_ultimo)
    dy_ultimo = (
        rendimento_ultimo * 12 / preco_numero
        if pd.notna(rendimento_ultimo) and pd.notna(preco_numero) and preco_numero > 0
        else np.nan
    )

    retornos = pd.to_numeric(
        janela["Percentual_Rentabilidade_Efetiva_Mes"], errors="coerce"
    )
    # Faixa ±15% ao mês: o informe da CVM traz erros de preenchimento (VISC11 em
    # 2026-05 declara -28% com valor patrimonial estável).
    rentab_invalida = retornos.notna() & ~retornos.between(-0.15, 0.15, inclusive="both")
    rentab_12m = (
        float((1 + retornos).prod() - 1)
        if len(janela) == 12 and retornos.notna().all() and not rentab_invalida.any()
        else np.nan
    )
    return {
        "dy_12m": dy_12m,
        "rendimento_12m_cota": rendimento_12m_cota,
        "dy_ultimo_mes": dy_ultimo,
        "rendimento_ultimo_mes": rendimento_ultimo,
        "rentab_12m": rentab_12m,
        "meses_informe": meses_informe,
        "dy_parcial": quantidade_valida < 12,
        "fundo_novo": meses_informe < 12,
        "dy_dados_suspeitos": bool(dy_invalido.any() or rentab_invalida.any()),
    }


def _media_imovel(quadro: pd.DataFrame, coluna: str) -> float:
    valores = pd.to_numeric(quadro[coluna], errors="coerce")
    pesos = pd.to_numeric(quadro["Percentual_Imovel_Total_Investido"], errors="coerce")
    utilizaveis = valores.notna() & pesos.notna()
    if utilizaveis.any() and pesos[utilizaveis].sum() > 0:
        return float(np.average(valores[utilizaveis], weights=pesos[utilizaveis]))
    return float(valores.mean()) if valores.notna().any() else np.nan


def agregar_imoveis(quadro: pd.DataFrame) -> dict[str, object]:
    """Agrega a posição trimestral mais recente de imóveis de um fundo."""
    vazio = {
        "vacancia": np.nan,
        "inadimplencia": np.nan,
        "num_imoveis": np.nan,
        "concentracao_top_imovel": np.nan,
    }
    if quadro.empty:
        return vazio
    dados = quadro.copy()
    dados["Data_Referencia"] = pd.to_datetime(dados["Data_Referencia"], errors="coerce")
    dados = dados[dados["Data_Referencia"].eq(dados["Data_Referencia"].max())]
    if dados.empty:
        return vazio
    nomes = dados["Nome_Imovel"].dropna().astype(str).str.strip()
    nomes = nomes[nomes.ne("")]
    pesos = pd.to_numeric(dados["Percentual_Imovel_Total_Investido"], errors="coerce")
    return {
        "vacancia": _media_imovel(dados, "Percentual_Vacancia"),
        "inadimplencia": _media_imovel(dados, "Percentual_Inadimplencia"),
        "num_imoveis": int(nomes.nunique()) if len(nomes) else 0,
        "concentracao_top_imovel": float(pesos.max()) if pesos.notna().any() else np.nan,
    }


def calcular_metricas_snapshot(linha: Mapping[str, object]) -> dict[str, float]:
    """Calcula múltiplos e tamanho usando a última fotografia mensal."""
    preco = linha.get("preco")
    cotas = _numero(linha.get("Cotas_Emitidas"))
    preco_numero = _numero(preco)
    valor_mercado = (
        preco_numero * cotas
        if pd.notna(preco_numero) and pd.notna(cotas) and cotas >= 0
        else np.nan
    )
    return {
        "valor_mercado": valor_mercado,
        "p_vp": divisao_segura(preco, linha.get("Valor_Patrimonial_Cotas")),
        "passivo_ativo": divisao_segura(linha.get("Total_Passivo"), linha.get("Valor_Ativo")),
    }
