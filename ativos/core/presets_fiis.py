"""Presets puros e auditáveis da busca de FIIs."""

from __future__ import annotations

import pandas as pd

SEM_PRESET_FII = "Sem preset"
RENDA_DESCONTO = "Renda com desconto"
TIJOLO_BAIXA_VACANCIA = "Tijolo com baixa vacância"
PAPEL_DIVERSIFICADO = "Papel diversificado"
ALTA_LIQUIDEZ = "Alta liquidez"
ABAIXO_DA_FAIXA = "Abaixo da faixa patrimonial e de renda"
PRESETS_FIIS = (
    SEM_PRESET_FII,
    RENDA_DESCONTO,
    TIJOLO_BAIXA_VACANCIA,
    PAPEL_DIVERSIFICADO,
    ALTA_LIQUIDEZ,
    ABAIXO_DA_FAIXA,
)


def aplicar_preset_fii(quadro: pd.DataFrame, preset: str) -> pd.DataFrame:
    """Aplica critérios inclusivos; valores ausentes não satisfazem os requisitos."""
    if preset == SEM_PRESET_FII:
        return quadro.copy()
    if preset == RENDA_DESCONTO:
        mascara = (
            quadro["p_vp"].between(0.70, 1.00, inclusive="both")
            & quadro["dy_12m"].ge(0.08)
            & quadro["liquidez_media_diaria"].ge(500_000)
        )
    elif preset == TIJOLO_BAIXA_VACANCIA:
        mascara = (
            quadro["tipo"].eq("Tijolo")
            & quadro["vacancia"].le(0.10)
            & quadro["p_vp"].between(0.80, 1.05, inclusive="both")
        )
    elif preset == PAPEL_DIVERSIFICADO:
        mascara = (
            quadro["tipo"].eq("Papel")
            & quadro["dy_12m"].ge(0.10)
            & quadro["passivo_ativo"].le(0.15)
        )
    elif preset == ALTA_LIQUIDEZ:
        mascara = quadro["liquidez_media_diaria"].ge(3_000_000) & quadro["cotistas"].ge(
            50_000
        )
    elif preset == ABAIXO_DA_FAIXA:
        mascara = quadro["situacao_faixa"].eq("abaixo da faixa")
    else:
        raise ValueError(f"Preset de FII desconhecido: {preset}")
    return quadro[mascara].copy()
