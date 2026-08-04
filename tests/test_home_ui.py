import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

import pagina_home
from focus_data import LeituraIndicador


def _leitura(indicador: str) -> LeituraIndicador:
    return LeituraIndicador(
        indicador=indicador,
        referencia="2026",
        data_coleta=date(2026, 8, 4),
        mediana=5.0,
        media=5.0,
        minimo=4.8,
        maximo=5.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def test_home_mostra_status_e_entrada_clara_para_o_focus():
    pagina = Path(__file__).resolve().parent.parent / "app_financas.py"
    with patch.object(
        pagina_home,
        "carregar_cache",
        return_value=[_leitura("Selic"), _leitura("IPCA")],
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Finanças Pessoais, sem ruído"
    assert app.subheader[0].value == "Panorama do Boletim Focus"
    assert app.get("page_link")[0].label == "Abrir panorama"
    assert "2 indicadores" in " ".join(
        elemento.value for elemento in app.caption
    )
