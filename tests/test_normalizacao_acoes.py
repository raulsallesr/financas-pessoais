import math
from datetime import date

import pandas as pd

from ativos.core.normalizacao import (
    calcular_pl_controladores,
    calcular_ttm,
    calcular_valor_mercado,
    corrigir_quantidade_acoes,
    normalizar_demonstracao,
    parsear_acoes_por_unit,
    preferir_consolidado,
    selecionar_versoes,
)


def test_escala_mil_multiplica_valor_por_mil():
    quadro = normalizar_demonstracao(
        pd.DataFrame([{"VL_CONTA": "12.5", "ESCALA_MOEDA": "MIL"}])
    )

    assert quadro.loc[0, "valor"] == 12_500


def test_point_in_time_descarta_entrega_futura_e_escolhe_maior_versao():
    quadro = pd.DataFrame(
        [
            {"CNPJ_CIA": "1", "DT_REFER": "2025-12-31", "VERSAO": "1", "DT_RECEB": "2026-02-01"},
            {"CNPJ_CIA": "1", "DT_REFER": "2025-12-31", "VERSAO": "2", "DT_RECEB": "2026-03-01"},
            {"CNPJ_CIA": "1", "DT_REFER": "2025-12-31", "VERSAO": "3", "DT_RECEB": "2026-04-01"},
        ]
    )

    resultado = selecionar_versoes(quadro, date(2026, 3, 15))

    assert resultado["VERSAO"].tolist() == [2]


def test_consolidado_precede_individual_por_documento():
    comum = {
        "CNPJ_CIA": "1",
        "DT_REFER": "2025-12-31",
        "VERSAO": "1",
        "DT_RECEB": "2026-03-01",
    }
    consolidado = pd.DataFrame([{**comum, "origem": "con"}])
    individual = pd.DataFrame(
        [{**comum, "origem": "ind"}, {**comum, "CNPJ_CIA": "2", "origem": "ind"}]
    )

    resultado = preferir_consolidado(consolidado, individual, date(2026, 4, 1))

    assert set(zip(resultado["CNPJ_CIA"], resultado["origem"], strict=True)) == {
        ("1", "con"),
        ("2", "ind"),
    }


def test_pl_e_ttm_seguem_regras_explicitas():
    assert calcular_pl_controladores(1_000, 100) == 900
    assert calcular_pl_controladores(1_000, None) == 1_000
    assert calcular_ttm(1_000, 300, 200) == 1_100
    assert calcular_ttm(1_000, None, 200) == 1_000


def test_quantidade_em_milhar_e_escala_suspeita_geram_alertas():
    on, pn, alertas = corrigir_quantidade_acoes(10, 10, 1_000_000, 10)
    assert (on, pn) == (10_000, 10_000)
    assert alertas == ["qtd_em_milhar"]

    _, _, alertas_suspeitos = corrigir_quantidade_acoes(1_000_000, 1_000_000, 1_000, 100)
    assert alertas_suspeitos == ["escala_suspeita"]

    _, _, alertas_gfsa = corrigir_quantidade_acoes(24_514, 0, 1_533_000_000, 0.45)
    assert alertas_gfsa == ["qtd_em_milhar", "escala_suspeita"]


def test_parser_de_unit():
    assert parsear_acoes_por_unit("1 ação ordinária e 4 ações preferenciais") == 5
    assert parsear_acoes_por_unit("2 PN e 1 ON") == 3
    assert parsear_acoes_por_unit(None) is None


def test_valor_de_mercado_soma_classes_sem_units_e_reaproveita_preco_ausente():
    assert calcular_valor_mercado(100, 50, 10, 20) == 2_000
    assert calcular_valor_mercado(100, 50, 10, None) == 1_500
    assert math.isnan(calcular_valor_mercado(0, 0, 10, 20))
