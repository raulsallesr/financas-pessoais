import math

import numpy as np
import pandas as pd
import pytest

from ativos.core.metricas_acoes import (
    COLUNAS_FINANCEIRAS,
    COLUNAS_METRICAS,
    calcular_cagr,
    calcular_metricas,
    calcular_metricas_tabela,
)

BASE = {
    "preco": 10,
    "valor_mercado": 1_000,
    "liquidez_media_diaria": 200,
    "acoes_total": 100,
    "lucro_ttm": 100,
    "pl_controladores": 500,
    "pl_consolidado": 550,
    "proventos": 60,
    "ativo_total": 1_000,
    "ativo_circulante": 400,
    "passivo_circulante": 200,
    "passivo_nao_circulante": 100,
    "receita_ttm": 800,
    "resultado_bruto_ttm": 320,
    "ebit_ttm": 160,
    "emprestimos_cp": 100,
    "emprestimos_lp": 200,
    "caixa": 50,
    "aplicacoes_financeiras": 25,
    "receita_dfp_atual": 200,
    "receita_dfp_5a": 100,
    "lucro_dfp_atual": 243,
    "lucro_dfp_5a": 100,
    "financeira": False,
}

CAGR_RECEITAS = 2 ** (1 / 5) - 1
CAGR_LUCROS = 2.43 ** (1 / 5) - 1


@pytest.mark.parametrize(
    ("metrica", "esperado"),
    [
        ("preco", 10),
        ("valor_mercado", 1_000),
        ("liquidez_media_diaria", 200),
        ("lpa", 1),
        ("p_l", 10),
        ("vpa", 5),
        ("p_vp", 2),
        ("dy", 0.06),
        ("peg", 10 / (CAGR_LUCROS * 100)),
        ("p_ativos", 1),
        ("p_cap_giro", 5),
        ("p_ativo_circ_liq", 10),
        ("psr", 1.25),
        ("p_ebit", 6.25),
        ("ev_ebit", 1225 / 160),
        ("margem_bruta", 0.4),
        ("margem_ebit", 0.2),
        ("margem_liquida", 0.125),
        ("divida_bruta", 300),
        ("divida_liquida", 225),
        ("div_liq_ebit", 225 / 160),
        ("div_liq_patrimonio", 0.45),
        ("roe", 0.2),
        ("roa", 0.1),
        ("roic", 160 * 0.66 / 725),
        ("liquidez_corrente", 2),
        ("patrimonio_ativos", 0.5),
        ("passivos_ativos", 0.45),
        ("giro_ativos", 0.8),
        ("cagr_receitas_5a", CAGR_RECEITAS),
        ("cagr_lucros_5a", CAGR_LUCROS),
    ],
)
def test_golden_de_cada_formula_da_tabela(metrica, esperado):
    assert calcular_metricas(BASE)[metrica] == pytest.approx(esperado)


def test_denominador_nao_positivo_e_dado_ausente_viram_nan():
    registro = {**BASE, "lucro_ttm": 0, "ativo_circulante": np.nan}
    metricas = calcular_metricas(registro)

    assert math.isnan(metricas["p_l"])
    assert math.isnan(metricas["p_cap_giro"])
    assert math.isnan(calcular_cagr(-1, 10))


def test_p_ativo_circulante_liquido_usa_passivo_exigivel_e_passivos_ativos_usa_pl():
    metricas = calcular_metricas(
        {
            **BASE,
            "valor_mercado": 600,
            "ativo_total": 1_000,
            "ativo_circulante": 700,
            "passivo_circulante": 200,
            "passivo_nao_circulante": 100,
            "pl_consolidado": 550,
        }
    )

    assert metricas["p_ativo_circ_liq"] == 1.5
    assert metricas["passivos_ativos"] == 0.45


def test_financeira_mantem_somente_colunas_permitidas():
    metricas = calcular_metricas({**BASE, "financeira": True})

    assert metricas["p_l"] == 10
    assert metricas["roe"] == 0.2
    assert all(
        math.isnan(metricas[coluna])
        for coluna in COLUNAS_METRICAS
        if coluna not in COLUNAS_FINANCEIRAS
    )


def test_calculo_em_tabela_preserva_metadados():
    quadro = calcular_metricas_tabela(pd.DataFrame([{"ticker": "TEST3", **BASE}]))

    assert quadro.loc[0, "ticker"] == "TEST3"
    assert quadro.loc[0, "p_l"] == 10
