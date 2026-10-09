import math

import pandas as pd
import pytest

from ativos.core.metricas_fiis import (
    agregar_imoveis,
    calcular_composicao,
    calcular_metricas_mensais,
    calcular_metricas_snapshot,
    classificar_tipo,
)


@pytest.mark.parametrize(
    ("imoveis", "recebiveis", "cotas", "esperado"),
    [
        (0.60, 0.10, 0.10, "Tijolo"),
        (0.10, 0.60, 0.10, "Papel"),
        (0.10, 0.10, 0.60, "Fundo de fundos"),
        (0.30, 0.30, 0.10, "Híbrido"),
        (0.20, 0.20, 0.20, "Outros"),
    ],
)
def test_tipo_por_composicao_inclui_limite_de_sessenta_por_cento(
    imoveis, recebiveis, cotas, esperado
):
    assert classificar_tipo(imoveis, recebiveis, cotas) == esperado


def test_golden_composicao_soma_blocos_sobre_total_investido():
    resultado = calcular_composicao(
        {
            "Total_Investido": 1_000,
            "Direitos_Bens_Imoveis": 500,
            "Acoes_Sociedades_Atividades_FII": 50,
            "Cotas_Sociedades_Atividades_FII": 50,
            "CRI": 200,
            "LCI": 100,
            "FII": 50,
            "Outras_Cotas_FI": 50,
        }
    )

    assert resultado == {
        "tipo": "Tijolo",
        "pct_imoveis": pytest.approx(0.60),
        "pct_recebiveis": pytest.approx(0.30),
        "pct_cotas_fundos": pytest.approx(0.10),
    }


def _historico(meses: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Data_Referencia": pd.date_range("2025-01-01", periods=meses, freq="MS"),
            "Valor_Patrimonial_Cotas": [100.0] * meses,
            "Percentual_Dividend_Yield_Mes": [0.01] * meses,
            "Percentual_Rentabilidade_Efetiva_Mes": [0.01] * meses,
        }
    )


def test_golden_dy_12m_dy_mensal_e_rentabilidade_composta():
    resultado = calcular_metricas_mensais(_historico(12), 100)

    assert resultado["dy_12m"] == pytest.approx(0.12)
    assert resultado["rendimento_ultimo_mes"] == pytest.approx(1.0)
    assert resultado["dy_ultimo_mes"] == pytest.approx(0.12)
    assert resultado["rentab_12m"] == pytest.approx(1.01**12 - 1)
    assert resultado["meses_informe"] == 12
    assert not resultado["dy_parcial"]
    assert not resultado["fundo_novo"]


def test_dy_com_seis_meses_anualiza_e_com_cinco_fica_vazio():
    parcial = calcular_metricas_mensais(_historico(6), 100)
    insuficiente = calcular_metricas_mensais(_historico(5), 100)

    assert parcial["dy_12m"] == pytest.approx(0.12)
    assert parcial["dy_parcial"] and parcial["fundo_novo"]
    assert math.isnan(parcial["rentab_12m"])
    assert math.isnan(insuficiente["dy_12m"])


def test_golden_xpml11_descarta_dy_negativo_anualiza_e_alerta():
    historico = _historico(12)
    mes_invalido = historico["Data_Referencia"].eq("2025-06-01")
    historico.loc[mes_invalido, "Percentual_Dividend_Yield_Mes"] = -0.058778

    resultado = calcular_metricas_mensais(historico, 100)

    assert resultado["dy_12m"] == pytest.approx(0.12)
    assert resultado["dy_parcial"]
    assert resultado["dy_dados_suspeitos"]


def test_golden_dy_zero_e_mes_valido_sem_alerta():
    historico = _historico(12)
    historico.loc[5, "Percentual_Dividend_Yield_Mes"] = 0

    resultado = calcular_metricas_mensais(historico, 100)

    assert resultado["dy_12m"] == pytest.approx(0.11)
    assert not resultado["dy_parcial"]
    assert not resultado["dy_dados_suspeitos"]


def test_golden_dy_com_cinco_meses_validos_fica_vazio_e_alerta():
    historico = _historico(12)
    historico.loc[:6, "Percentual_Dividend_Yield_Mes"] = 0.051

    resultado = calcular_metricas_mensais(historico, 100)

    assert math.isnan(resultado["dy_12m"])
    assert resultado["dy_parcial"]
    assert resultado["dy_dados_suspeitos"]


def test_rentabilidade_fora_do_intervalo_invalida_calculo_e_alerta():
    historico = _historico(12)
    historico.loc[0, "Percentual_Rentabilidade_Efetiva_Mes"] = 0.150001

    resultado = calcular_metricas_mensais(historico, 100)

    assert math.isnan(resultado["rentab_12m"])
    assert resultado["dy_dados_suspeitos"]


@pytest.mark.parametrize("limite", [-0.15, 0.15])
def test_limites_da_rentabilidade_mensal_sao_validos(limite):
    historico = _historico(12)
    historico.loc[0, "Percentual_Rentabilidade_Efetiva_Mes"] = limite

    resultado = calcular_metricas_mensais(historico, 100)

    assert not math.isnan(resultado["rentab_12m"])
    assert not resultado["dy_dados_suspeitos"]


def test_golden_vacancia_e_inadimplencia_ponderadas_e_concentracao():
    quadro = pd.DataFrame(
        {
            "Data_Referencia": ["2026-03-31", "2026-06-30", "2026-06-30"],
            "Nome_Imovel": ["Antigo", "A", "B"],
            "Percentual_Vacancia": [0.50, 0.10, 0.20],
            "Percentual_Inadimplencia": [0.50, 0.02, 0.04],
            "Percentual_Imovel_Total_Investido": [1.0, 0.60, 0.40],
        }
    )

    resultado = agregar_imoveis(quadro)

    assert resultado["vacancia"] == pytest.approx(0.14)
    assert resultado["inadimplencia"] == pytest.approx(0.028)
    assert resultado["num_imoveis"] == 2
    assert resultado["concentracao_top_imovel"] == pytest.approx(0.60)


def test_vacancia_sem_pesos_usa_media_simples():
    quadro = pd.DataFrame(
        {
            "Data_Referencia": ["2026-06-30", "2026-06-30"],
            "Nome_Imovel": ["A", "B"],
            "Percentual_Vacancia": [0.10, 0.30],
            "Percentual_Inadimplencia": [0.02, 0.06],
            "Percentual_Imovel_Total_Investido": [None, None],
        }
    )

    resultado = agregar_imoveis(quadro)

    assert resultado["vacancia"] == pytest.approx(0.20)
    assert resultado["inadimplencia"] == pytest.approx(0.04)
    assert math.isnan(resultado["concentracao_top_imovel"])


def test_golden_alavancagem_valor_de_mercado_e_p_vp():
    resultado = calcular_metricas_snapshot(
        {
            "preco": 90,
            "Cotas_Emitidas": 2_000,
            "Valor_Patrimonial_Cotas": 100,
            "Total_Passivo": 150,
            "Valor_Ativo": 1_000,
        }
    )

    assert resultado == {
        "valor_mercado": pytest.approx(180_000),
        "p_vp": pytest.approx(0.90),
        "passivo_ativo": pytest.approx(0.15),
    }


def test_rentabilidade_visc11_maio_2026_menos_28_por_cento_e_erro_de_cadastro():
    historico = _historico(12)
    historico.loc[0, "Percentual_Rentabilidade_Efetiva_Mes"] = -0.279847

    resultado = calcular_metricas_mensais(historico, 100)

    assert math.isnan(resultado["rentab_12m"])
    assert resultado["dy_dados_suspeitos"]
