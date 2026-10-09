import pandas as pd
import pytest

from ativos.core.presets import (
    BAZIN,
    GRAHAM_DEFENSIVO,
    MAGIC_FORMULA,
    QUALIDADE_DIVIDA_BAIXA,
    SEM_PRESET,
    aplicar_preset,
)


def _base():
    return pd.DataFrame(
        [
            {
                "ticker": "AAA3",
                "p_l": 10,
                "p_vp": 1,
                "liquidez_corrente": 2,
                "dy": 0.07,
                "financeira": False,
                "div_liq_ebit": 1,
                "ev_ebit": 5,
                "roic": 0.20,
                "roe": 0.20,
                "margem_liquida": 0.15,
            },
            {
                "ticker": "BBB3",
                "p_l": 20,
                "p_vp": 2,
                "liquidez_corrente": 1,
                "dy": 0.02,
                "financeira": False,
                "div_liq_ebit": 4,
                "ev_ebit": 4,
                "roic": 0.10,
                "roe": 0.10,
                "margem_liquida": 0.05,
            },
            {
                "ticker": "CCC3",
                "p_l": None,
                "p_vp": 1,
                "liquidez_corrente": 2,
                "dy": None,
                "financeira": True,
                "div_liq_ebit": None,
                "ev_ebit": None,
                "roic": None,
                "roe": 0.30,
                "margem_liquida": 0.20,
            },
        ]
    )


@pytest.mark.parametrize(
    ("preset", "tickers"),
    [
        (SEM_PRESET, ["AAA3", "BBB3", "CCC3"]),
        (GRAHAM_DEFENSIVO, ["AAA3"]),
        (BAZIN, ["AAA3"]),
        (QUALIDADE_DIVIDA_BAIXA, ["AAA3"]),
        (MAGIC_FORMULA, ["AAA3", "BBB3"]),
    ],
)
def test_presets_e_nan_fora_de_criterios_obrigatorios(preset, tickers):
    assert aplicar_preset(_base(), preset)["ticker"].tolist() == tickers


def test_preset_desconhecido_falha_fechado():
    with pytest.raises(ValueError, match="desconhecido"):
        aplicar_preset(_base(), "inventado")
