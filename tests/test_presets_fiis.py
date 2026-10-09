import pandas as pd
import pytest

from ativos.core.presets_fiis import (
    ALTA_LIQUIDEZ,
    PAPEL_DIVERSIFICADO,
    RENDA_DESCONTO,
    SEM_PRESET_FII,
    TIJOLO_BAIXA_VACANCIA,
    aplicar_preset_fii,
)


def _base():
    return pd.DataFrame(
        [
            {
                "ticker": "RENDA11",
                "tipo": "Tijolo",
                "p_vp": 0.90,
                "dy_12m": 0.09,
                "liquidez_media_diaria": 600_000,
                "vacancia": 0.08,
                "passivo_ativo": 0.10,
                "cotistas": 10_000,
            },
            {
                "ticker": "PAPEL11",
                "tipo": "Papel",
                "p_vp": 1.10,
                "dy_12m": 0.11,
                "liquidez_media_diaria": 400_000,
                "vacancia": None,
                "passivo_ativo": 0.15,
                "cotistas": 20_000,
            },
            {
                "ticker": "LIQDO11",
                "tipo": "Outros",
                "p_vp": None,
                "dy_12m": None,
                "liquidez_media_diaria": 3_000_000,
                "vacancia": None,
                "passivo_ativo": None,
                "cotistas": 50_000,
            },
        ]
    )


@pytest.mark.parametrize(
    ("preset", "tickers"),
    [
        (SEM_PRESET_FII, ["RENDA11", "PAPEL11", "LIQDO11"]),
        (RENDA_DESCONTO, ["RENDA11"]),
        (TIJOLO_BAIXA_VACANCIA, ["RENDA11"]),
        (PAPEL_DIVERSIFICADO, ["PAPEL11"]),
        (ALTA_LIQUIDEZ, ["LIQDO11"]),
    ],
)
def test_presets_fiis_incluem_limites_e_excluem_nan(preset, tickers):
    assert aplicar_preset_fii(_base(), preset)["ticker"].tolist() == tickers


def test_preset_fii_desconhecido_falha_fechado():
    with pytest.raises(ValueError, match="desconhecido"):
        aplicar_preset_fii(_base(), "inventado")
