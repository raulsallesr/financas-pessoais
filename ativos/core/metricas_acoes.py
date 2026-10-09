"""Fórmulas puras da busca avançada de ações."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

COLUNAS_METRICAS = (
    "preco",
    "valor_mercado",
    "liquidez_media_diaria",
    "lpa",
    "p_l",
    "vpa",
    "p_vp",
    "dy",
    "peg",
    "p_ativos",
    "p_cap_giro",
    "p_ativo_circ_liq",
    "psr",
    "p_ebit",
    "ev_ebit",
    "margem_bruta",
    "margem_ebit",
    "margem_liquida",
    "divida_bruta",
    "divida_liquida",
    "div_liq_ebit",
    "div_liq_patrimonio",
    "roe",
    "roa",
    "roic",
    "liquidez_corrente",
    "patrimonio_ativos",
    "passivos_ativos",
    "giro_ativos",
    "cagr_receitas_5a",
    "cagr_lucros_5a",
)

COLUNAS_FINANCEIRAS = {
    "preco",
    "valor_mercado",
    "liquidez_media_diaria",
    "p_l",
    "lpa",
    "p_vp",
    "vpa",
    "dy",
    "roe",
    "roa",
    "patrimonio_ativos",
    "passivos_ativos",
    "cagr_lucros_5a",
    "peg",
}


def _numero(registro: Mapping[str, object], chave: str) -> float:
    valor = registro.get(chave, np.nan)
    try:
        return float(valor) if not pd.isna(valor) else np.nan
    except (TypeError, ValueError):
        return np.nan


def divisao(numerador: float, denominador: float) -> float:
    """Divide apenas por denominador estritamente positivo."""
    if pd.isna(numerador) or pd.isna(denominador) or denominador <= 0:
        return np.nan
    return numerador / denominador


def calcular_cagr(valor_final: float, valor_inicial: float, anos: int = 5) -> float:
    if (
        pd.isna(valor_final)
        or pd.isna(valor_inicial)
        or valor_final <= 0
        or valor_inicial <= 0
        or anos <= 0
    ):
        return np.nan
    return (valor_final / valor_inicial) ** (1 / anos) - 1


def calcular_metricas(registro: Mapping[str, object]) -> dict[str, float]:
    """Calcula todas as métricas de uma empresa a partir de valores em reais."""
    preco = _numero(registro, "preco")
    valor_mercado = _numero(registro, "valor_mercado")
    liquidez = _numero(registro, "liquidez_media_diaria")
    acoes = _numero(registro, "acoes_total")
    lucro = _numero(registro, "lucro_ttm")
    pl = _numero(registro, "pl_controladores")
    pl_consolidado = _numero(registro, "pl_consolidado")
    proventos = _numero(registro, "proventos")
    ativo_total = _numero(registro, "ativo_total")
    ativo_circulante = _numero(registro, "ativo_circulante")
    passivo_circulante = _numero(registro, "passivo_circulante")
    passivo_nao_circulante = _numero(registro, "passivo_nao_circulante")
    receita = _numero(registro, "receita_ttm")
    resultado_bruto = _numero(registro, "resultado_bruto_ttm")
    ebit = _numero(registro, "ebit_ttm")
    emprestimos_cp = _numero(registro, "emprestimos_cp")
    emprestimos_lp = _numero(registro, "emprestimos_lp")
    caixa = _numero(registro, "caixa")
    aplicacoes = _numero(registro, "aplicacoes_financeiras")

    divida_bruta = (
        np.nan
        if pd.isna(emprestimos_cp) and pd.isna(emprestimos_lp)
        else np.nansum([emprestimos_cp, emprestimos_lp])
    )
    disponibilidades = (
        np.nan if pd.isna(caixa) and pd.isna(aplicacoes) else np.nansum([caixa, aplicacoes])
    )
    divida_liquida = (
        np.nan
        if pd.isna(divida_bruta) or pd.isna(disponibilidades)
        else divida_bruta - disponibilidades
    )
    p_l = divisao(valor_mercado, lucro)
    cagr_receitas = calcular_cagr(
        _numero(registro, "receita_dfp_atual"),
        _numero(registro, "receita_dfp_5a"),
    )
    cagr_lucros = calcular_cagr(
        _numero(registro, "lucro_dfp_atual"),
        _numero(registro, "lucro_dfp_5a"),
    )
    capital_investido = (
        divida_bruta + pl - caixa - aplicacoes
        if not any(pd.isna(valor) for valor in (divida_bruta, pl, caixa, aplicacoes))
        else np.nan
    )
    passivo_exigivel = (
        passivo_circulante + passivo_nao_circulante
        if not pd.isna(passivo_circulante) and not pd.isna(passivo_nao_circulante)
        else np.nan
    )

    metricas = {
        "preco": preco,
        "valor_mercado": valor_mercado,
        "liquidez_media_diaria": liquidez,
        "lpa": divisao(lucro, acoes),
        "p_l": p_l,
        "vpa": divisao(pl, acoes),
        "p_vp": divisao(valor_mercado, pl),
        "dy": divisao(proventos, valor_mercado),
        "peg": divisao(p_l, cagr_lucros * 100),
        "p_ativos": divisao(valor_mercado, ativo_total),
        "p_cap_giro": divisao(valor_mercado, ativo_circulante - passivo_circulante),
        "p_ativo_circ_liq": divisao(valor_mercado, ativo_circulante - passivo_exigivel),
        "psr": divisao(valor_mercado, receita),
        "p_ebit": divisao(valor_mercado, ebit),
        "ev_ebit": divisao(valor_mercado + divida_liquida, ebit),
        "margem_bruta": divisao(resultado_bruto, receita),
        "margem_ebit": divisao(ebit, receita),
        "margem_liquida": divisao(lucro, receita),
        "divida_bruta": divida_bruta,
        "divida_liquida": divida_liquida,
        "div_liq_ebit": divisao(divida_liquida, ebit),
        "div_liq_patrimonio": divisao(divida_liquida, pl),
        "roe": divisao(lucro, pl),
        "roa": divisao(lucro, ativo_total),
        "roic": divisao(ebit * (1 - 0.34), capital_investido),
        "liquidez_corrente": divisao(ativo_circulante, passivo_circulante),
        "patrimonio_ativos": divisao(pl, ativo_total),
        "passivos_ativos": divisao(ativo_total - pl_consolidado, ativo_total),
        "giro_ativos": divisao(receita, ativo_total),
        "cagr_receitas_5a": cagr_receitas,
        "cagr_lucros_5a": cagr_lucros,
    }
    if bool(registro.get("financeira", False)):
        for coluna in COLUNAS_METRICAS:
            if coluna not in COLUNAS_FINANCEIRAS:
                metricas[coluna] = np.nan
    return metricas


def calcular_metricas_tabela(base: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta as fórmulas a uma base de empresas/tickers."""
    if base.empty:
        return base.assign(**{coluna: pd.Series(dtype=float) for coluna in COLUNAS_METRICAS})
    calculadas = pd.DataFrame(
        [calcular_metricas(registro) for registro in base.to_dict(orient="records")],
        index=base.index,
    )
    resultado = base.copy()
    for coluna in COLUNAS_METRICAS:
        resultado[coluna] = calculadas[coluna]
    return resultado
