import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import motor_indicadores
from focus_data import LeituraIndicador, comparar
from focus_regras import explicar_leigo, resumo_efeitos

VERBOS_PROIBIDOS = re.compile(
    r"\b(invista|invisto|compre|comprar|venda|vender|recomendo|recomendamos|recomendação)\w*",
    re.IGNORECASE,
)


def _leitura(mediana, indicador="Selic", referencia="R5/2026", data_coleta=date(2026, 7, 31)):
    return LeituraIndicador(
        indicador=indicador,
        referencia=referencia,
        data_coleta=data_coleta,
        mediana=mediana,
        media=mediana,
        minimo=mediana - 1,
        maximo=mediana + 1,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def test_nenhum_texto_de_regra_usa_linguagem_imperativa():
    for efeitos in motor_indicadores._REGRAS.values():
        for efeito in efeitos:
            assert not VERBOS_PROIBIDOS.search(efeito.explicacao), efeito.explicacao


def test_explicar_leigo_sem_leitura_anterior():
    atual = _leitura(14.0)
    comparativo = comparar(atual, None)
    texto = explicar_leigo(comparativo)
    assert "primeira leitura" in texto
    assert not VERBOS_PROIBIDOS.search(texto)


def test_explicar_leigo_com_alta():
    atual = _leitura(14.0)
    anterior = _leitura(13.5, data_coleta=date(2026, 7, 24))
    comparativo = comparar(atual, anterior)
    texto = explicar_leigo(comparativo)
    assert "subiu" in texto
    assert not VERBOS_PROIBIDOS.search(texto)


def test_explicar_leigo_com_queda():
    atual = _leitura(13.0)
    anterior = _leitura(13.8, data_coleta=date(2026, 7, 24))
    comparativo = comparar(atual, anterior)
    texto = explicar_leigo(comparativo)
    assert "caiu" in texto


def test_resumo_efeitos_retorna_lista_para_indicador_conhecido():
    atual = _leitura(14.0)
    anterior = _leitura(13.5, data_coleta=date(2026, 7, 24))
    comparativo = comparar(atual, anterior)
    assert len(resumo_efeitos(comparativo)) > 0
