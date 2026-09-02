import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import atualizar_curva_cache
from focuslens.core.curva_data import PontoCurva


def _ponto(ano: int) -> PontoCurva:
    return PontoCurva(
        data_referencia=date(2026, 8, 26),
        tipo_titulo="Tesouro Prefixado",
        vencimento=date(ano, 1, 1),
        taxa_compra=14.0,
        taxa_venda=14.12,
        pu_compra=800.0,
        pu_venda=799.0,
        fonte="Teste",
    )


def test_main_atualiza_cache_sem_iniciar_streamlit(capsys):
    with patch.object(
        atualizar_curva_cache,
        "atualizar_e_obter_curva",
        return_value=(_ponto(2029), _ponto(2031)),
    ):
        assert atualizar_curva_cache.main() == 0

    saida = capsys.readouterr().out
    assert "2 pontos em 1 datas" in saida
    assert "2 vencimentos" in saida
    assert "2026-08-26" in saida
