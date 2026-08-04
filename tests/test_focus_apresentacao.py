import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focus_apresentacao import (
    escolher_destaque,
    formatar_delta,
    formatar_valor,
    ordenar_comparativos,
    titulo_resumo,
)
from focus_data import LeituraIndicador, comparar


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


def _comparativo(indicador: str, atual: float, anterior: float):
    return comparar(
        _leitura(indicador, atual, date(2026, 8, 4)),
        _leitura(indicador, anterior, date(2026, 7, 28)),
    )


def test_ordenar_comparativos_coloca_tres_principais_primeiro():
    comparativos = [
        _comparativo("IGP-M", 4.5, 4.2),
        _comparativo("Câmbio", 5.2, 5.1),
        _comparativo("Selic", 14.0, 13.5),
        _comparativo("IPCA", 5.0, 4.9),
    ]
    ordenados = ordenar_comparativos(comparativos)
    assert [
        comparativo.atual.indicador for comparativo in ordenados[:3]
    ] == ["Selic", "IPCA", "Câmbio"]


def test_escolher_destaque_normaliza_delta_pelo_limiar():
    selic = _comparativo("Selic", 14.2, 14.0)
    ipca = _comparativo("IPCA", 5.15, 5.0)
    destaque = escolher_destaque([selic, ipca])
    assert destaque.atual.indicador == "IPCA"


def test_titulo_resumo_distingue_estabilidade_de_movimento():
    estavel = _comparativo("Selic", 14.05, 14.0)
    assert titulo_resumo([estavel]) == (
        "Pouca mudança nas expectativas acompanhadas"
    )

    alta = _comparativo("IPCA", 5.2, 5.0)
    assert "IPCA" in titulo_resumo([alta])
    assert "alta" in titulo_resumo([alta])


def test_formatacao_financeira_em_portugues():
    cambio = _comparativo("Câmbio", 5.25, 5.10)
    selic = _comparativo("Selic", 14.0, 13.5)
    assert formatar_valor(cambio) == "R$ 5,25"
    assert formatar_delta(cambio) == "+R$ 0,15 desde 28/07"
    assert formatar_valor(selic) == "14,00%"
    assert formatar_delta(selic) == "+0,50 p.p. desde 28/07"
