import math

import numpy as np
import pandas as pd
import pytest

from ativos.core.metricas_acoes import calcular_metricas_tabela
from ativos.core.normalizacao import normalizar_demonstracao
from ativos.core.pipeline_acoes import (
    _capital_e_mercado,
    _capital_empresas,
    _preparar_dfc,
    _proventos_dfc_empresas,
    _proventos_empresas,
    mapear_tickers,
)


def _fluxo(
    cnpj: str,
    codigo: str,
    descricao: str,
    valor: float,
    *,
    data: str = "2025-12-31",
    ordem: str = "ÚLTIMO",
    inicio: str = "2025-01-01",
) -> dict[str, object]:
    return {
        "CNPJ_CIA": cnpj,
        "DT_REFER": data,
        "VERSAO": "1",
        "DENOM_CIA": cnpj,
        "ESCALA_MOEDA": "MIL",
        "ORDEM_EXERC": ordem,
        "DT_INI_EXERC": inicio,
        "DT_FIM_EXERC": data,
        "CD_CONTA": codigo,
        "DS_CONTA": descricao,
        "VL_CONTA": str(valor),
        "DT_RECEB": "2026-03-31",
    }


def _normalizado(linhas: list[dict[str, object]]) -> pd.DataFrame:
    return normalizar_demonstracao(pd.DataFrame(linhas))


def test_golden_dfc_2025_soma_pagamentos_em_modulo_e_exclui_nao_controladores():
    vale = "VALE"
    itau = "ITAU"
    petrobras = "PETROBRAS"
    weg = "WEG"
    jcp_abreviado = "JCP_ABREVIADO"
    mi_con = pd.DataFrame(
        [
            _fluxo(vale, "6.03.04", "Dividendos/JCP Pagos a Acionistas", -19_971_000),
            _fluxo(
                itau,
                "6.03.08",
                "Dividendos / Juros sobre o Capital Próprio Pagos",
                -48_299_000,
            ),
            _fluxo(
                itau,
                "6.03.07",
                "Dividendos pagos a acionistas não controladores",
                -633_000,
            ),
            _fluxo(petrobras, "6.03.05", "Dividendos pagos a acionistas", -45_205_000),
            _fluxo(
                petrobras,
                "6.03.06",
                "Dividendos pagos a acionistas não controladores",
                -233_000,
            ),
            _fluxo(weg, "6.03.04", "Pgto de Dividendos/Juros s/ Capital Próprio", -5_384_769),
            _fluxo(weg, "6.03.09", "Dividendos recebidos", 999_000),
            _fluxo(jcp_abreviado, "6.03.02", "Pagamento de Juros s/ Capital Próprio", -10),
            _fluxo(jcp_abreviado, "6.03.03", "Juros capitalizados", -999),
        ]
    )
    vazio = mi_con.iloc[0:0].copy()
    dfc = _preparar_dfc((mi_con, vazio, vazio, vazio), pd.Timestamp("2026-10-08"))

    resultado = _proventos_dfc_empresas(dfc, normalizar_demonstracao(vazio)).set_index("cnpj")

    assert resultado.loc[vale, "proventos"] == 19_971_000_000
    assert resultado.loc[itau, "proventos"] == 48_299_000_000
    assert resultado.loc[petrobras, "proventos"] == 45_205_000_000
    assert resultado.loc[weg, "proventos"] == 5_384_769_000
    assert resultado.loc[jcp_abreviado, "proventos"] == 10_000


def test_dfc_respeita_prioridade_ttm_e_resultado_negativo_vira_nan():
    mi_con = pd.DataFrame([_fluxo("PRIORIDADE", "6.03.01", "Dividendos pagos", -100)])
    md_con = pd.DataFrame(
        [
            _fluxo("PRIORIDADE", "6.03.01", "Dividendos pagos", -999),
            _fluxo("FALLBACK_MD", "6.03.01", "Dividendos pagos", -200),
        ]
    )
    mi_ind = pd.DataFrame([_fluxo("FALLBACK_IND", "6.03.01", "Dividendos pagos", -300)])
    vazio = mi_con.iloc[0:0].copy()
    dfp = _preparar_dfc((mi_con, md_con, mi_ind, vazio), pd.Timestamp("2026-10-08"))
    itr = _normalizado(
        [
            _fluxo(
                "PRIORIDADE",
                "6.03.01",
                "Dividendos pagos",
                -40,
                data="2026-06-30",
                inicio="2026-01-01",
            ),
            _fluxo(
                "PRIORIDADE",
                "6.03.01",
                "Dividendos pagos",
                -25,
                data="2026-06-30",
                ordem="PENÚLTIMO",
                inicio="2025-01-01",
            ),
            _fluxo("NEGATIVO", "6.03.01", "Dividendos pagos", -1),
        ]
    )
    negativo_dfp = _normalizado(
        [_fluxo("NEGATIVO", "6.03.01", "Dividendos pagos", -10)]
    )
    negativo_itr = _normalizado(
        [
            _fluxo(
                "NEGATIVO",
                "6.03.01",
                "Dividendos pagos",
                -1,
                data="2026-06-30",
                inicio="2026-01-01",
            ),
            _fluxo(
                "NEGATIVO",
                "6.03.01",
                "Dividendos pagos",
                -20,
                data="2026-06-30",
                ordem="PENÚLTIMO",
                inicio="2025-01-01",
            ),
        ]
    )

    resultado = _proventos_dfc_empresas(dfp, itr).set_index("cnpj")
    resultado_negativo = _proventos_dfc_empresas(negativo_dfp, negativo_itr).set_index("cnpj")

    assert resultado.loc["PRIORIDADE", "proventos"] == 115_000
    assert resultado.loc["FALLBACK_MD", "proventos"] == 200_000
    assert resultado.loc["FALLBACK_IND", "proventos"] == 300_000
    assert math.isnan(resultado_negativo.loc["NEGATIVO", "proventos"])


def test_dva_e_usada_so_sem_linha_dfc_e_marca_alerta():
    dfc = _normalizado([_fluxo("COM_DFC", "6.03.01", "Dividendos pagos", -100)])
    dva = _normalizado(
        [
            _fluxo("COM_DFC", "7.08.04.02", "Dividendos", 999),
            _fluxo("SO_DVA", "7.08.04.01", "Juros sobre o Capital Próprio", 50),
            _fluxo("DVA_NEGATIVA", "7.08.04.02", "Dividendos", -1),
        ]
    )

    resultado = _proventos_empresas(dfc, dfc.iloc[0:0].copy(), dva).set_index("cnpj")

    assert resultado.loc["COM_DFC", "proventos"] == 100_000
    assert resultado.loc["COM_DFC", "alertas_contabeis"] == []
    assert resultado.loc["SO_DVA", "proventos"] == 50_000
    assert resultado.loc["SO_DVA", "alertas_contabeis"] == ["dy_dva"]
    assert math.isnan(resultado.loc["DVA_NEGATIVA", "proventos"])


@pytest.mark.parametrize(
    ("ticker", "cnpj", "preco_unit", "acoes_por_unit", "on", "pn", "esperado"),
    [
        ("ENGI11", "ENGI", 66.25, 5, 975_000_000, 1_540_000_000, 33_323_750_000),
        ("BRBI11", "BRBI", 18.53, 3, 200_000_000, 115_000_000, 1_945_650_000),
    ],
)
def test_valor_de_mercado_e_derivado_do_preco_da_unit(
    ticker, cnpj, preco_unit, acoes_por_unit, on, pn, esperado
):
    tickers = pd.DataFrame(
        [
            {
                "ticker": ticker,
                "cnpj": cnpj,
                "preco": preco_unit,
                "liquidez_media_diaria": 1_000_000,
            }
        ]
    )
    capital = pd.DataFrame(
        [
            {
                "cnpj": cnpj,
                "quantidade_on": on,
                "quantidade_pn": pn,
                "variacao_quantidade_suspeita": False,
            }
        ]
    )
    contabil = pd.DataFrame([{"cnpj": cnpj, "pl_controladores": esperado}])
    units = pd.DataFrame([{"cnpj": cnpj, "acoes_por_unit": acoes_por_unit}])

    mercado = _capital_e_mercado(tickers, capital, contabil, units).iloc[0]

    assert mercado["valor_mercado"] == pytest.approx(esperado)
    assert mercado["alertas_capital"] == ["mcap_por_unit"]


def test_aliases_de_nome_resolvem_tickers_e_ambiguidade_fica_pendente():
    universo = pd.DataFrame(
        [
            {"ticker": "AMAR3", "empresa_b3": "LOJAS MARISA", "alertas": []},
            {"ticker": "BPAC11", "empresa_b3": "BTGP BANCO", "alertas": []},
            {"ticker": "CSNA3", "empresa_b3": "SID NACIONAL", "alertas": []},
            {"ticker": "DUPL3", "empresa_b3": "EMPRESA DUPLICADA", "alertas": []},
        ]
    )
    cadastro = pd.DataFrame(
        [
            {
                "CNPJ_CIA": "MARISA-CORRETA",
                "DENOM_SOCIAL": "MARISA LOJAS SA",
                "DENOM_COMERC": "MARISA LOJAS SA",
            },
            {"CNPJ_CIA": "MARISA-OUTRA", "DENOM_SOCIAL": "MARISA SA", "DENOM_COMERC": "MARISA"},
            {
                "CNPJ_CIA": "BTG",
                "DENOM_SOCIAL": "BANCO BTG PACTUAL S/A",
                "DENOM_COMERC": "BANCO UBS PACTUAL S/A",
            },
            {
                "CNPJ_CIA": "CSN",
                "DENOM_SOCIAL": "CIA SIDERURGICA NACIONAL",
                "DENOM_COMERC": "CSN",
            },
            {
                "CNPJ_CIA": "AMB-1",
                "DENOM_SOCIAL": "EMPRESA DUPLICADA SA",
                "DENOM_COMERC": "EMPRESA DUPLICADA",
            },
            {
                "CNPJ_CIA": "AMB-2",
                "DENOM_SOCIAL": "EMPRESA DUPLICADA SA",
                "DENOM_COMERC": "EMPRESA DUPLICADA",
            },
        ]
    )

    resultado = mapear_tickers(universo, pd.DataFrame(), cadastro).set_index("ticker")

    assert resultado.loc["AMAR3", "cnpj"] == "MARISA-CORRETA"
    assert resultado.loc["BPAC11", "cnpj"] == "BTG"
    assert resultado.loc["CSNA3", "cnpj"] == "CSN"
    assert resultado.loc[["AMAR3", "BPAC11", "CSNA3"], "origem_cnpj"].tolist() == [
        "nome",
        "nome",
        "nome",
    ]
    assert pd.isna(resultado.loc["DUPL3", "cnpj"])
    assert "sem_cnpj" in resultado.loc["DUPL3", "alertas"]


@pytest.mark.parametrize(
    ("ticker", "cnpj", "preco", "pl", "quantidades"),
    [
        ("GFSA3", "GFSA", 0.45, 1_533_000_000, [("2026-03-31", 24_516, 0)]),
        (
            "MEAL3",
            "MEAL",
            0.97,
            752_000_000,
            [
                ("2026-03-31", 2_866_765_400, 2_866_765_400),
                ("2026-06-30", 28_667_654_000, 2_866_765_400),
            ],
        ),
    ],
)
def test_escala_suspeita_bloqueia_valor_de_mercado_e_multiplos(
    ticker, cnpj, preco, pl, quantidades
):
    linhas_capital = [
        {
            "CNPJ_CIA": cnpj,
            "DT_REFER": data,
            "VERSAO": "1",
            "DT_RECEB": "2026-08-13",
            "QT_ACAO_ORDIN_CAP_INTEGR": str(on),
            "QT_ACAO_PREF_CAP_INTEGR": str(pn),
            "QT_ACAO_ORDIN_TESOURO": "0",
            "QT_ACAO_PREF_TESOURO": "0",
        }
        for data, on, pn in quantidades
    ]
    capital = _capital_empresas(
        pd.DataFrame(), pd.DataFrame(linhas_capital), pd.Timestamp("2026-10-08")
    )
    mercado = _capital_e_mercado(
        pd.DataFrame(
            [
                {
                    "ticker": ticker,
                    "cnpj": cnpj,
                    "preco": preco,
                    "liquidez_media_diaria": 1_000_000,
                }
            ]
        ),
        capital,
        pd.DataFrame([{"cnpj": cnpj, "pl_controladores": pl}]),
        pd.DataFrame(),
    )
    base = mercado.assign(
        preco=preco,
        pl_controladores=pl,
        proventos=10,
        lucro_ttm=100,
        receita_ttm=1_000,
        ebit_ttm=100,
        ativo_total=2_000,
        ativo_circulante=1_000,
        passivo_circulante=200,
        passivo_nao_circulante=300,
        financeira=False,
    )
    resultado = calcular_metricas_tabela(base).iloc[0]

    assert "escala_suspeita" in mercado.iloc[0]["alertas_capital"]
    for coluna in ("valor_mercado", "p_l", "p_vp", "dy", "psr", "p_ebit", "ev_ebit", "p_ativos"):
        assert np.isnan(resultado[coluna])
