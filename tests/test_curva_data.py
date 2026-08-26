import sys
from datetime import date
from pathlib import Path

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


def test_consolidacao_remove_duplicata_e_ordena_por_data_e_vencimento():
    antigo = _ponto(date(2026, 8, 25), date(2029, 1, 1), 13.0)
    atualizado = _ponto(date(2026, 8, 25), date(2029, 1, 1), 13.2)
    recente = _ponto(date(2026, 8, 26), date(2028, 1, 1), 12.9)

    resultado = consolidar_pontos_curva([recente, antigo, atualizado])

    assert resultado == (atualizado, recente)


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
    try:
        manter_datas_recentes([], max_datas=0)
        assert False, "deveria rejeitar max_datas inválido"
    except ValueError:
        pass
