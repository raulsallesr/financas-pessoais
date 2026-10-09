"""Presets puros e auditáveis da busca avançada."""

from __future__ import annotations

import pandas as pd

SEM_PRESET = "Sem preset"
GRAHAM_DEFENSIVO = "Graham defensivo"
BAZIN = "Bazin"
MAGIC_FORMULA = "Magic Formula"
QUALIDADE_DIVIDA_BAIXA = "Qualidade com dívida baixa"
MARGEM_CALCULADA = "Margem calculada ≥ 30% com 3+ modelos"
PRESETS = (
    SEM_PRESET,
    GRAHAM_DEFENSIVO,
    BAZIN,
    MAGIC_FORMULA,
    QUALIDADE_DIVIDA_BAIXA,
    MARGEM_CALCULADA,
)


def aplicar_preset(quadro: pd.DataFrame, preset: str) -> pd.DataFrame:
    """Filtra/ordena o quadro; NaN nunca satisfaz um critério obrigatório."""
    if preset == SEM_PRESET:
        return quadro.copy()
    if preset == GRAHAM_DEFENSIVO:
        mascara = (
            quadro["p_l"].le(15)
            & quadro["p_vp"].le(1.5)
            & quadro["p_l"].mul(quadro["p_vp"]).le(22.5)
            & quadro["liquidez_corrente"].ge(1.5)
            & quadro["dy"].gt(0)
            & ~quadro["financeira"].fillna(False)
        )
        return quadro[mascara].copy()
    if preset == BAZIN:
        return quadro[quadro["dy"].ge(0.06) & quadro["div_liq_ebit"].le(3)].copy()
    if preset == MAGIC_FORMULA:
        elegiveis = quadro[
            ~quadro["financeira"].fillna(False)
            & quadro["ev_ebit"].gt(0)
            & quadro["roic"].gt(0)
        ].copy()
        elegiveis["_posto_yield"] = (1 / elegiveis["ev_ebit"]).rank(
            ascending=False,
            method="min",
        )
        elegiveis["_posto_roic"] = elegiveis["roic"].rank(ascending=False, method="min")
        elegiveis["_posto_total"] = elegiveis["_posto_yield"] + elegiveis["_posto_roic"]
        return (
            elegiveis.sort_values(["_posto_total", "ticker"], kind="stable")
            .drop(columns=["_posto_yield", "_posto_roic", "_posto_total"])
            .copy()
        )
    if preset == QUALIDADE_DIVIDA_BAIXA:
        return quadro[
            quadro["roe"].ge(0.15)
            & quadro["margem_liquida"].ge(0.10)
            & quadro["div_liq_ebit"].le(2)
        ].copy()
    if preset == MARGEM_CALCULADA:
        return quadro[
            quadro["margem_seguranca"].ge(0.30) & quadro["n_modelos"].ge(3)
        ].copy()
    raise ValueError(f"Preset desconhecido: {preset}")
