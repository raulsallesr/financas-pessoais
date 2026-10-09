from datetime import date

import numpy as np
import pytest

from ativos.core import premissas
from ativos.core.premissas import PremissasValuation, premissas_padrao, taxa_livre_de_risco
from ativos.ui.premissas_valuation import restaurar_premissas
from focuslens.adapters.curva_fontes import ErroCacheCurva
from focuslens.core.curva_data import PontoCurva


def _ponto(data_base, vencimento, taxa):
    return PontoCurva(
        data_referencia=data_base,
        tipo_titulo="Tesouro Prefixado",
        vencimento=vencimento,
        taxa_compra=taxa,
        taxa_venda=None,
        pu_compra=None,
        pu_venda=None,
        fonte="Tesouro Transparente",
    )


def test_taxa_livre_de_risco_interpola_cinco_anos_na_data_mais_recente():
    data_base = date(2026, 1, 1)
    pontos = [
        _ponto(date(2025, 12, 31), date(2031, 12, 31), 99),
        _ponto(data_base, date(2029, 1, 1), 10),
        _ponto(data_base, date(2033, 1, 1), 14),
    ]
    prazos = np.array(
        [
            (date(2029, 1, 1) - data_base).days / 365.25,
            (date(2033, 1, 1) - data_base).days / 365.25,
        ]
    )
    esperado = np.interp(5, prazos, [10, 14]) / 100

    referencia = taxa_livre_de_risco(pontos)

    assert referencia.taxa == pytest.approx(esperado)
    assert referencia.data_referencia == data_base
    assert referencia.fonte == "Tesouro Transparente"
    assert not referencia.rf_padrao


def test_taxa_livre_de_risco_extrapola_pelo_vertice_mais_proximo():
    data_base = date(2026, 1, 1)
    pontos = [
        _ponto(data_base, date(2027, 1, 1), 11),
        _ponto(data_base, date(2028, 1, 1), 13),
    ]

    assert taxa_livre_de_risco(pontos, anos_alvo=0.5).taxa == pytest.approx(0.11)
    assert taxa_livre_de_risco(pontos, anos_alvo=10).taxa == pytest.approx(0.13)


def test_falha_do_cache_usa_fallback_marcado(monkeypatch):
    def falhar():
        raise ErroCacheCurva("cache inválido")

    monkeypatch.setattr(premissas, "carregar_cache", falhar)

    referencia = taxa_livre_de_risco()
    padrao = premissas_padrao()

    assert referencia.taxa == 0.12
    assert referencia.rf_padrao
    assert padrao.rf == 0.12
    assert padrao.k == pytest.approx(0.17)
    assert padrao.fii_taxa_exigida == pytest.approx(0.102)


def test_restaurar_premissas_recoloca_valores_visiveis_em_percentual():
    estado = {"valuation_rf": 99.0}
    padrao = PremissasValuation(rf=0.128, data_curva=date(2026, 10, 8))

    restaurar_premissas(padrao, estado)

    assert estado["valuation_rf"] == pytest.approx(12.8)
    assert estado["valuation_erp"] == pytest.approx(5.0)
    assert estado["valuation_data_curva"] == date(2026, 10, 8)


@pytest.mark.parametrize("anos", [0, -1, float("nan")])
def test_prazo_alvo_invalido_falha(anos):
    with pytest.raises(ValueError, match="positivo"):
        taxa_livre_de_risco([], anos_alvo=anos)
