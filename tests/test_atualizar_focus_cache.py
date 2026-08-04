import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import atualizar_focus_cache
from focus_data import LeituraIndicador


def _leitura() -> LeituraIndicador:
    return LeituraIndicador(
        indicador="IPCA",
        referencia="2026",
        data_coleta=date(2026, 8, 4),
        mediana=5.0,
        media=5.0,
        minimo=4.8,
        maximo=5.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def test_main_atualiza_cache_sem_iniciar_streamlit(capsys):
    with patch.object(
        atualizar_focus_cache,
        "atualizar_e_obter_historico",
        return_value=[_leitura()],
    ):
        assert atualizar_focus_cache.main() == 0

    saida = capsys.readouterr().out
    assert "1 registros" in saida
    assert "coleta mais recente em 2026-08-04" in saida
