import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from financas_taxonomia import Direcao
from focus_data import (
    LeituraIndicador,
    calcular_delta,
    comparar,
    leitura_anterior,
    leitura_mais_recente,
    serie_historica,
)


def _leitura(mediana, dias_atras=0, indicador="Selic", referencia="R5/2026"):
    data = date(2026, 7, 31) - timedelta(days=dias_atras)
    return LeituraIndicador(
        indicador=indicador,
        referencia=referencia,
        data_coleta=data,
        mediana=mediana,
        media=mediana,
        minimo=mediana - 1,
        maximo=mediana + 1,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def test_calcular_delta_sem_anterior():
    atual = _leitura(14.0)
    assert calcular_delta(atual, None) == 0.0


def test_calcular_delta_com_anterior():
    atual = _leitura(14.0)
    anterior = _leitura(13.75, dias_atras=7)
    assert calcular_delta(atual, anterior) == 0.25


def test_comparar_classifica_direcao_subiu():
    atual = _leitura(14.0)
    anterior = _leitura(13.5, dias_atras=7)
    comparativo = comparar(atual, anterior)
    assert comparativo.direcao == Direcao.SUBIU


def test_comparar_classifica_direcao_caiu():
    atual = _leitura(13.5)
    anterior = _leitura(14.0, dias_atras=7)
    comparativo = comparar(atual, anterior)
    assert comparativo.direcao == Direcao.CAIU


def test_comparar_classifica_direcao_estavel():
    atual = _leitura(14.00)
    anterior = _leitura(13.98, dias_atras=7)
    comparativo = comparar(atual, anterior)
    assert comparativo.direcao == Direcao.ESTAVEL


def test_comparar_sem_anterior_e_estavel():
    atual = _leitura(14.0)
    comparativo = comparar(atual, None)
    assert comparativo.direcao == Direcao.ESTAVEL
    assert comparativo.delta == 0.0


def test_leitura_mais_recente():
    leituras = [_leitura(13.5, dias_atras=7), _leitura(14.0, dias_atras=0)]
    mais_recente = leitura_mais_recente(leituras)
    assert mais_recente.mediana == 14.0


def test_leitura_mais_recente_lista_vazia():
    assert leitura_mais_recente([]) is None


def test_leitura_anterior_mesmo_indicador_e_referencia():
    historico = [
        _leitura(13.5, dias_atras=7, indicador="Selic", referencia="R5/2026"),
        _leitura(14.0, dias_atras=0, indicador="Selic", referencia="R5/2026"),
        _leitura(5.0, dias_atras=0, indicador="IPCA", referencia="2026"),
    ]
    atual = historico[1]
    anterior = leitura_anterior(historico, atual)
    assert anterior is not None
    assert anterior.mediana == 13.5


def test_leitura_anterior_ignora_indicador_diferente():
    historico = [
        _leitura(5.0, dias_atras=7, indicador="IPCA", referencia="2026"),
        _leitura(14.0, dias_atras=0, indicador="Selic", referencia="R5/2026"),
    ]
    atual = historico[1]
    assert leitura_anterior(historico, atual) is None


def test_serie_historica_ordena_por_data_e_filtra_indicador():
    historico = [
        _leitura(14.0, dias_atras=0, indicador="Selic", referencia="R5/2026"),
        _leitura(5.0, dias_atras=0, indicador="IPCA", referencia="2026"),
        _leitura(13.5, dias_atras=14, indicador="Selic", referencia="R5/2026"),
        _leitura(13.75, dias_atras=7, indicador="Selic", referencia="R5/2026"),
    ]
    serie = serie_historica(historico, "Selic")
    assert [leitura.mediana for leitura in serie] == [13.5, 13.75, 14.0]


def test_serie_historica_indicador_sem_leituras_retorna_lista_vazia():
    historico = [_leitura(5.0, indicador="IPCA", referencia="2026")]
    assert serie_historica(historico, "Selic") == []
