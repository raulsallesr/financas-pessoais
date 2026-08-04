import sys
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

import pagina_focus
from focus_data import LeituraIndicador
from noticias_data import Noticia
from noticias_feed import ResultadoNoticias


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


def _noticias():
    return ResultadoNoticias(
        noticias=tuple(
            Noticia(
                titulo=f"Selic e inflação em destaque {indice}",
                link=f"https://www.infomoney.com.br/economia/item-{indice}/",
                fonte="InfoMoney" if indice < 2 else "Brazil Journal",
                publicada_em=datetime(
                    2026, 8, 4, 14 - indice, tzinfo=UTC
                ),
            )
            for indice in range(3)
        )
    )


def test_pagina_focus_renderiza_hierarquia_e_um_unico_grafico():
    pagina = (
        Path(__file__).resolve().parent.parent
        / "pages"
        / "1_Boletim_Focus.py"
    )
    with (
        patch.object(
            pagina_focus, "carregar_cache", return_value=_historico()
        ),
        patch.object(
            pagina_focus, "_carregar_noticias", return_value=_noticias()
        ),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Seu dinheiro em contexto"
    subtitulos = [elemento.value for elemento in app.subheader]
    assert "Três números para começar" in subtitulos
    assert "O que isso pode afetar" in subtitulos
    assert "Histórico sem poluição visual" in subtitulos
    assert "Contexto em 3 manchetes" in subtitulos
    assert [metrica.label for metrica in app.metric[:3]] == [
        "Selic",
        "IPCA",
        "Câmbio",
    ]
    assert len(app.get("vega_lite_chart")) == 1
    assert len(app.get("link_button")) == 3
