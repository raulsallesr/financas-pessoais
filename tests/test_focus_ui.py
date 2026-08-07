import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

import pagina_focus
from focus_data import LeituraIndicador


def _leitura(indicador, mediana, data_coleta, referencia="2026"):
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


def _historico():
    valores = {
        "Selic": (14.0, 13.75, "R5/2026"),
        "IPCA": (5.03, 5.10, "2026"),
        "Câmbio": (5.20, 5.10, "2026"),
        "PIB Total": (1.99, 1.90, "2026"),
        "IGP-M": (4.54, 4.40, "2026"),
        "Dívida líquida do setor público": (69.9, 69.5, "2026"),
    }
    leituras = []
    for indicador, (atual, anterior, referencia) in valores.items():
        leituras.extend(
            [
                _leitura(
                    indicador,
                    anterior,
                    date(2026, 7, 28),
                    referencia,
                ),
                _leitura(
                    indicador,
                    atual,
                    date(2026, 8, 4),
                    referencia,
                ),
            ]
        )
    return leituras


def test_pagina_focus_renderiza_hierarquia_e_um_unico_grafico():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "focus_section.py"
    )
    with (
        patch.object(
            pagina_focus, "carregar_cache", return_value=_historico()
        ),
        patch.object(
            pagina_focus,
            "data_ultima_atualizacao_cache",
            return_value=date(2026, 8, 4),
        ),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.header[0].value == "Expectativas do mercado"
    subtitulos = [elemento.value for elemento in app.subheader]
    assert "Histórico" in subtitulos
    assert "Contexto em 3 manchetes" not in subtitulos
    assert [metrica.label for metrica in app.metric[:3]] == [
        "Selic",
        "IPCA",
        "Câmbio",
    ]
    assert len(app.get("vega_lite_chart")) == 1
    assert not app.get("link_button")


def test_pagina_focus_busca_primeiro_historico_automaticamente():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "focus_section.py"
    )
    with (
        patch.object(pagina_focus, "carregar_cache", return_value=[]),
        patch.object(
            pagina_focus,
            "data_ultima_atualizacao_cache",
            return_value=None,
        ),
        patch.object(
            pagina_focus,
            "atualizar_e_obter_historico",
            return_value=_historico(),
        ) as atualizar,
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    atualizar.assert_called_once_with()
    assert [metrica.label for metrica in app.metric[:3]] == [
        "Selic",
        "IPCA",
        "Câmbio",
    ]
