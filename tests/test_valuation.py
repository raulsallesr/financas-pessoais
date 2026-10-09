import math
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from ativos.core.premissas import PremissasValuation
from ativos.core.valuation import (
    calcular_valuation_acoes,
    calcular_valuation_fiis,
    consolidar_modelos,
    sensibilidade_gordon,
    sensibilidade_taxa,
    tabela_modelos_acao,
)

PREMISSAS = PremissasValuation(rf=0.128, erp=0.05, g=0.04)


def _acao(**mudancas):
    base = {
        "ticker": "BASE3",
        "cnpj": "base",
        "setor": "Indústria",
        "financeira": False,
        "preco": 10.0,
        "lpa": 2.0,
        "vpa": 10.0,
        "dpa": 0.60,
        "p_l": 5.0,
        "p_vp": 1.0,
        "liquidez_media_diaria": 1_000_000.0,
        "alertas": [],
    }
    return {**base, **mudancas}


def test_goldens_graham_bazin_e_gordon_e_recalculo_de_premissa():
    quadro = pd.DataFrame([_acao()])

    calculado = calcular_valuation_acoes(quadro, PREMISSAS).iloc[0]
    alterado = calcular_valuation_acoes(
        quadro, replace(PREMISSAS, bazin_taxa=0.08)
    ).iloc[0]
    restaurado = calcular_valuation_acoes(quadro, PREMISSAS).iloc[0]

    assert calculado["modelo_graham"] == pytest.approx(21.2132, rel=1e-5)
    assert calculado["modelo_bazin"] == pytest.approx(10.0)
    assert calculado["modelo_gordon"] == pytest.approx(4.5217391304)
    assert alterado["modelo_bazin"] == pytest.approx(7.5)
    assert restaurado["modelo_bazin"] == calculado["modelo_bazin"]
    assert calculado["n_modelos"] == 3


def test_golden_gordon_da_especificacao():
    calculado = calcular_valuation_acoes(
        pd.DataFrame([_acao(dpa=1.0)]), PREMISSAS
    ).iloc[0]

    assert calculado["modelo_gordon"] == pytest.approx(7.5362, rel=1e-5)


def test_multiplos_setoriais_excluem_proprio_ativo_e_deduplicam_cnpj():
    alvo = _acao(p_l=100, p_vp=100)
    duplicata = _acao(ticker="BASE4", p_l=100, p_vp=100)
    pares = [
        _acao(
            ticker=f"PAR{indice}3",
            cnpj=f"par-{indice}",
            lpa=1,
            vpa=1,
            p_l=pl,
            p_vp=pvp,
        )
        for indice, (pl, pvp) in enumerate(zip(range(5, 11), range(1, 7), strict=True))
    ]

    calculado = calcular_valuation_acoes(
        pd.DataFrame([alvo, duplicata, *pares]), PREMISSAS
    ).iloc[0]

    assert calculado["pares_p_l_setor"] == 6
    assert calculado["pares_p_vp_setor"] == 6
    assert calculado["mediana_p_l_setor"] == pytest.approx(7.5)
    assert calculado["mediana_p_vp_setor"] == pytest.approx(3.5)
    assert calculado["modelo_multiplos_setor"] == pytest.approx(25.0)


def test_multiplos_setoriais_falham_com_poucos_pares_e_financeiras_so_comparam_entre_si():
    quadro = pd.DataFrame(
        [
            _acao(financeira=True, setor="Bancos"),
            _acao(ticker="SEG3", cnpj="seg", financeira=True, setor="Seguradoras"),
            _acao(ticker="IND3", cnpj="ind", financeira=False),
        ]
    )
    calculado = calcular_valuation_acoes(quadro, PREMISSAS)

    assert calculado.loc[0, "pares_p_l_setor"] == 1
    assert math.isnan(calculado.loc[0, "modelo_multiplos_setor"])
    assert "menos de 6 pares" in calculado.loc[0, "status_multiplos_setor"]


@pytest.mark.parametrize(
    ("mudancas", "modelo", "motivo"),
    [
        ({"lpa": 0}, "modelo_graham", "LPA não positivo"),
        ({"vpa": -1}, "modelo_graham", "VPA não positivo"),
        ({"dpa": np.nan}, "modelo_bazin", "DPA ausente"),
        ({"dpa": 0}, "modelo_gordon", "DPA não positivo"),
    ],
)
def test_modelos_de_acao_explicam_quando_nao_se_aplicam(mudancas, modelo, motivo):
    calculado = calcular_valuation_acoes(pd.DataFrame([_acao(**mudancas)]), PREMISSAS).iloc[0]

    assert math.isnan(calculado[modelo])
    assert motivo in calculado[modelo.replace("modelo_", "status_")]


def test_gordon_exige_diferenca_de_quatro_pontos_percentuais():
    calculado = calcular_valuation_acoes(
        pd.DataFrame([_acao()]), replace(PREMISSAS, rf=0.04, erp=0.03, g=0.04)
    ).iloc[0]

    assert math.isnan(calculado["modelo_gordon"])
    assert "abaixo de 4 p.p." in calculado["status_gordon"]


@pytest.mark.parametrize(
    ("valores", "baixa", "central", "alta"),
    [
        ([10, 20], 12.5, 15, 17.5),
        ([10, 20, 30], 15, 20, 25),
        ([10, 20, 30, 40], 17.5, 25, 32.5),
    ],
)
def test_percentis_lineares_com_dois_tres_e_quatro_modelos(
    valores, baixa, central, alta
):
    modelos = pd.DataFrame([valores], columns=[f"m{i}" for i in range(len(valores))])
    consolidado = consolidar_modelos(modelos, pd.Series([15])).iloc[0]

    assert consolidado["faixa_baixa"] == pytest.approx(baixa)
    assert consolidado["valor_central"] == pytest.approx(central)
    assert consolidado["faixa_alta"] == pytest.approx(alta)


@pytest.mark.parametrize(
    ("preco", "situacao"),
    [(10, "abaixo da faixa"), (15, "dentro da faixa"), (20, "acima da faixa")],
)
def test_margem_e_posicao_nos_tres_casos(preco, situacao):
    consolidado = consolidar_modelos(pd.DataFrame([[12, 18]]), preco).iloc[0]

    assert consolidado["margem_seguranca"] == pytest.approx(15 / preco - 1)
    assert consolidado["situacao_faixa"] == situacao


def test_menos_de_dois_modelos_nao_forma_faixa_e_alertas_marcam_fragilidade():
    insuficiente = consolidar_modelos(pd.DataFrame([[10, np.nan]]), 8).iloc[0]
    fragil = consolidar_modelos(
        pd.DataFrame([[10, 40]]), 8, pd.Series([[]])
    ).iloc[0]
    alerta = consolidar_modelos(
        pd.DataFrame([[10, 12, 14]]), 8, pd.Series([["salto_preco"]])
    ).iloc[0]

    assert math.isnan(insuficiente["faixa_baixa"])
    assert pd.isna(insuficiente["situacao_faixa"])
    assert fragil["valuation_fragil"]
    assert alerta["valuation_fragil"]


def test_golden_renda_capitalizada_de_fii_e_casos_inaplicaveis():
    quadro = pd.DataFrame(
        [
            {
                "ticker": "OK11",
                "preco": 90,
                "vp_cota": 100,
                "rendimento_12m_cota": 12,
                "alertas": [],
            },
            {
                "ticker": "SEM11",
                "preco": 90,
                "vp_cota": 0,
                "rendimento_12m_cota": np.nan,
                "alertas": [],
            },
        ]
    )

    calculado = calcular_valuation_fiis(quadro, PremissasValuation(rf=0.12))

    assert calculado.loc[0, "modelo_patrimonial"] == 100
    assert calculado.loc[0, "modelo_renda_capitalizada"] == pytest.approx(12 / 0.102)
    assert calculado.loc[0, "n_modelos"] == 2
    assert calculado.loc[0, "situacao_faixa"] == "abaixo da faixa"
    assert calculado.loc[1, "n_modelos"] == 0
    assert math.isnan(calculado.loc[1, "faixa_baixa"])


def test_tabela_de_modelos_e_sensibilidades_expoem_calculos():
    linha = calcular_valuation_acoes(pd.DataFrame([_acao()]), PREMISSAS).iloc[0]
    tabela = tabela_modelos_acao(linha, PREMISSAS)
    gordon = sensibilidade_gordon(1.0, PREMISSAS)
    bazin = sensibilidade_taxa(0.60, 0.06)

    assert tabela["Modelo"].tolist() == [
        "Graham",
        "Bazin",
        "Gordon",
        "Múltiplos do setor",
    ]
    assert gordon.loc["g 4.00%", "k 17.80%"] == pytest.approx(7.5362, rel=1e-5)
    assert bazin.loc[1, "Valor"] == pytest.approx(10.0)


@pytest.mark.parametrize(
    ("mudancas", "limitado"),
    [
        ({"p_l": 25.0, "p_vp": 6.0}, False),
        ({"p_l": 25.1}, True),
        ({"p_vp": 6.1}, True),
        ({"p_l": np.nan, "p_vp": np.nan}, False),
    ],
)
def test_modelos_de_valor_limitados_para_multiplos_altos(mudancas, limitado):
    quadro = pd.DataFrame([_acao(**mudancas)])

    calculado = calcular_valuation_acoes(quadro, PREMISSAS).iloc[0]

    assert bool(calculado["modelos_valor_limitados"]) is limitado
