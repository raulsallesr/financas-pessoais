import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.core.focus_data import LeituraIndicador, comparar
from focuslens.core.focus_semanal import montar_resumo_semanal
from focuslens.ui.focus_apresentacao import (
    descricao_resumo_semanal,
    escolher_destaque,
    formatar_delta,
    formatar_valor,
    ordenar_comparativos,
    titulo_resumo,
    titulo_resumo_semanal,
)


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


def test_texto_semanal_resume_estado_e_quantifica_evidencia():
    comparativos = [
        _comparativo("Selic", 14.2, 14.0),
        _comparativo("IPCA", 5.15, 5.0),
        _comparativo("Câmbio", 5.04, 5.0),
        _comparativo("PIB Total", 1.04, 1.0),
    ]
    resumo = montar_resumo_semanal(
        comparativos,
        date(2026, 8, 4),
    )

    assert titulo_resumo_semanal(resumo) == (
        "IPCA liderou as revisões de alta"
    )
    descricao = descricao_resumo_semanal(resumo)
    assert "2 de 4 indicadores comparáveis" in descricao
    assert "limiar" in descricao


def test_texto_semanal_nao_inventa_movimento_na_primeira_fotografia():
    comparativos = [
        comparar(
            _leitura("Selic", 14.0, date(2026, 8, 4)),
            None,
        )
    ]
    resumo = montar_resumo_semanal(
        comparativos,
        date(2026, 8, 4),
    )

    assert titulo_resumo_semanal(resumo) == (
        "Primeira fotografia das expectativas disponível"
    )
    assert "não calculamos variação" in descricao_resumo_semanal(resumo)
