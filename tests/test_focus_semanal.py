import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.core.focus_data import LeituraIndicador, comparar
from focuslens.core.focus_semanal import (
    EstadoFocusSemanal,
    calcular_relevancia,
    montar_resumo_semanal,
    ordenar_por_relevancia,
)


HOJE = date(2026, 8, 26)


def _leitura(
    indicador: str,
    mediana: float,
    data_coleta: date,
    referencia: str = "2026",
) -> LeituraIndicador:
    return LeituraIndicador(
        indicador=indicador,
        referencia=referencia,
        data_coleta=data_coleta,
        mediana=mediana,
        media=mediana,
        minimo=mediana - 0.2,
        maximo=mediana + 0.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def _comparativo(
    indicador: str,
    atual: float,
    anterior: float | None,
    *,
    dias_atras: int = 0,
):
    referencia = "R6/2026" if indicador == "Selic" else "2026"
    leitura_atual = _leitura(
        indicador,
        atual,
        HOJE - timedelta(days=dias_atras),
        referencia,
    )
    leitura_anterior = (
        _leitura(
            indicador,
            anterior,
            HOJE - timedelta(days=dias_atras + 7),
            referencia,
        )
        if anterior is not None
        else None
    )
    return comparar(leitura_atual, leitura_anterior)


def test_relevancia_normaliza_delta_pelo_limiar_do_indicador():
    selic = _comparativo("Selic", 14.2, 14.0)
    ipca = _comparativo("IPCA", 5.15, 5.0)

    assert calcular_relevancia(selic) == 2.0
    assert calcular_relevancia(ipca) == 3.0


def test_ranking_prioriza_revisoes_e_ignora_indicadores_fora_do_marco():
    comparativos = [
        _comparativo("PIB Total", 1.06, 1.0),
        _comparativo("IGP-M", 5.0, 4.0),
        _comparativo("Câmbio", 5.10, 5.0),
        _comparativo("Selic", 14.2, 14.0),
        _comparativo("IPCA", 5.15, 5.0),
    ]

    ranking = ordenar_por_relevancia(comparativos)

    assert [item.atual.indicador for item in ranking] == [
        "IPCA",
        "Selic",
        "Câmbio",
        "PIB Total",
    ]


def test_resumo_atualizado_expoe_as_tres_maiores_revisoes():
    comparativos = [
        _comparativo("Selic", 14.2, 14.0),
        _comparativo("IPCA", 5.15, 5.0),
        _comparativo("Câmbio", 5.10, 5.0),
        _comparativo("PIB Total", 1.06, 1.0),
    ]

    resumo = montar_resumo_semanal(comparativos, HOJE)

    assert resumo.estado == EstadoFocusSemanal.ATUALIZADO
    assert resumo.total_acompanhados == 4
    assert resumo.total_comparaveis == 4
    assert resumo.total_relevantes == 4
    assert [item.atual.indicador for item in resumo.destaques] == [
        "IPCA",
        "Selic",
        "Câmbio",
    ]


def test_resumo_distingue_estabilidade_de_dado_defasado():
    estaveis = [
        _comparativo("Selic", 14.08, 14.0),
        _comparativo("IPCA", 5.04, 5.0),
        _comparativo("Câmbio", 5.04, 5.0),
        _comparativo("PIB Total", 1.04, 1.0),
    ]
    resumo_estavel = montar_resumo_semanal(estaveis, HOJE)

    defasados = [
        _comparativo("Selic", 14.2, 14.0, dias_atras=10),
        _comparativo("IPCA", 5.15, 5.0, dias_atras=10),
    ]
    resumo_defasado = montar_resumo_semanal(defasados, HOJE)

    assert (
        resumo_estavel.estado
        == EstadoFocusSemanal.SEM_MUDANCA_RELEVANTE
    )
    assert resumo_estavel.total_relevantes == 0
    assert resumo_defasado.estado == EstadoFocusSemanal.DEFASADO
    assert resumo_defasado.dias_uteis is not None
    assert resumo_defasado.dias_uteis > 5


def test_resumo_sem_dados_fica_indisponivel():
    resumo = montar_resumo_semanal([], HOJE)

    assert resumo.estado == EstadoFocusSemanal.INDISPONIVEL
    assert resumo.data_mais_recente is None
    assert resumo.destaques == ()


def test_primeira_fotografia_e_atualizada_sem_inventar_variacao():
    comparativos = [
        _comparativo("Câmbio", 5.2, None),
        _comparativo("Selic", 14.0, None),
        _comparativo("IPCA", 5.0, None),
    ]

    resumo = montar_resumo_semanal(comparativos, HOJE)

    assert resumo.estado == EstadoFocusSemanal.ATUALIZADO
    assert resumo.total_comparaveis == 0
    assert resumo.total_relevantes == 0
    assert [item.atual.indicador for item in resumo.destaques] == [
        "Selic",
        "IPCA",
        "Câmbio",
    ]
