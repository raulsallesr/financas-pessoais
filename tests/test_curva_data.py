import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from curva_data import PontoCurva, consolidar_pontos_curva, manter_datas_recentes


def _ponto(data_ref: date, vencimento: date, taxa: float) -> PontoCurva:
    return PontoCurva(
        data_referencia=data_ref,
        tipo_titulo="Tesouro Prefixado",
        vencimento=vencimento,
        taxa_compra=taxa,
        taxa_venda=taxa + 0.1,
        pu_compra=900.0,
        pu_venda=899.0,
        fonte="Teste",
    )


def test_consolidacao_remove_duplicata_identica_e_ordena():
    antigo = _ponto(date(2026, 8, 25), date(2029, 1, 1), 13.0)
    recente = _ponto(date(2026, 8, 26), date(2028, 1, 1), 12.9)

    resultado = consolidar_pontos_curva([recente, antigo, antigo])

    assert resultado == (antigo, recente)


def test_consolidacao_rejeita_duplicata_conflitante():
    original = _ponto(date(2026, 8, 25), date(2029, 1, 1), 13.0)
    conflitante = _ponto(date(2026, 8, 25), date(2029, 1, 1), 13.2)

    with pytest.raises(ValueError, match="pontos conflitantes"):
        consolidar_pontos_curva([original, conflitante])


@pytest.mark.parametrize("taxa", [float("nan"), float("inf")])
def test_ponto_rejeita_taxa_nao_finita(taxa: float):
    with pytest.raises(ValueError, match="taxa_compra"):
        _ponto(date(2026, 8, 25), date(2029, 1, 1), taxa)


def test_ponto_rejeita_vencimento_na_data_base():
    with pytest.raises(ValueError, match="posterior"):
        _ponto(date(2026, 8, 25), date(2026, 8, 25), 13.0)


def test_recorte_mantem_datas_observadas_sem_interpolar():
    pontos = [
        _ponto(date(2026, 8, dia), date(2030, 1, 1), 13 + dia / 100)
        for dia in (20, 21, 24, 25, 26)
    ]

    resultado = manter_datas_recentes(pontos, max_datas=3)

    assert {ponto.data_referencia for ponto in resultado} == {
        date(2026, 8, 24),
        date(2026, 8, 25),
        date(2026, 8, 26),
    }


def test_recorte_rejeita_limite_invalido():
    with pytest.raises(ValueError, match="positivo"):
        manter_datas_recentes([], max_datas=0)
