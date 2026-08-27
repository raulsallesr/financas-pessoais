import sys
from datetime import date
from math import inf, nan
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from curva_cenarios import simular_choque_paralelo
from curva_data import PontoCurva
from curva_modelo import FotografiaCurva


DATA_BASE = date(2026, 8, 26)


def _ponto(ano: int, taxa: float, data_base: date = DATA_BASE) -> PontoCurva:
    return PontoCurva(
        data_referencia=data_base,
        tipo_titulo="Tesouro Prefixado",
        vencimento=date(ano, 1, 1),
        taxa_compra=taxa,
        taxa_venda=None,
        pu_compra=None,
        pu_venda=None,
        fonte="Teste",
    )


def _fotografia() -> FotografiaCurva:
    return FotografiaCurva(
        data_referencia=DATA_BASE,
        pontos=(
            _ponto(2032, 13.60),
            _ponto(2028, 13.00),
            _ponto(2030, 13.30),
        ),
    )


def test_choque_paralelo_desloca_todos_os_pontos_sem_alterar_a_base():
    fotografia = _fotografia()
    cenario = simular_choque_paralelo(fotografia, 50)

    assert [ponto.vencimento.year for ponto in cenario.pontos] == [
        2028,
        2030,
        2032,
    ]
    assert [ponto.taxa_observada for ponto in cenario.pontos] == [
        13.00,
        13.30,
        13.60,
    ]
    assert [ponto.taxa_cenario for ponto in cenario.pontos] == [
        13.50,
        13.80,
        14.10,
    ]
    assert fotografia.pontos[0].taxa_compra == 13.60
    assert cenario.inclinacao_observada_bps == 60.0
    assert cenario.inclinacao_cenario_bps == 60.0
    assert cenario.titulo == "Choque paralelo de +50 bps"
    assert "permanece em +60 bps" in cenario.resumo


def test_choque_negativo_e_zero_produzem_narrativas_explicitas():
    queda = simular_choque_paralelo(_fotografia(), -25)
    neutro = simular_choque_paralelo(_fotografia(), 0)

    assert queda.pontos[0].taxa_cenario == 12.75
    assert "caem 0,25 p.p." in queda.resumo
    assert neutro.pontos[0].taxa_cenario == 13.00
    assert "permanecem no nível observado" in neutro.resumo
    assert neutro.titulo == "Choque paralelo de 0 bps"


def test_um_ponto_nao_inventa_inclinacao():
    fotografia = FotografiaCurva(DATA_BASE, (_ponto(2028, 13.0),))

    cenario = simular_choque_paralelo(fotografia, 25)

    assert cenario.inclinacao_observada_bps is None
    assert cenario.inclinacao_cenario_bps is None
    assert "não existe inclinação" in cenario.resumo


@pytest.mark.parametrize("choque", [True, nan, inf, -inf, -201, 201])
def test_choque_invalido_falha_fechado(choque):
    with pytest.raises(ValueError):
        simular_choque_paralelo(_fotografia(), choque)


def test_fotografia_vazia_ou_com_data_incoerente_falha_fechado():
    vazia = FotografiaCurva(DATA_BASE, ())
    incoerente = FotografiaCurva(
        DATA_BASE,
        (_ponto(2028, 13.0, date(2026, 8, 25)),),
    )

    with pytest.raises(ValueError, match="ao menos um ponto"):
        simular_choque_paralelo(vazia, 25)
    with pytest.raises(ValueError, match="data-base"):
        simular_choque_paralelo(incoerente, 25)


def test_limites_excluem_previsao_preco_e_mudanca_de_inclinacao():
    limites = " ".join(simular_choque_paralelo(_fotografia(), 25).limites)

    assert "não uma previsão" in limites
    assert "Não calcula preço, retorno" in limites
    assert "mudanças de inclinação" in limites
