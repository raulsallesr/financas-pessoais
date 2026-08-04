import sys
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

import pagina_macro
from focus_data import LeituraIndicador
from mercado_data import PontoMercado, SerieMercado
from mercado_fontes import ResultadoMercados
from noticias_data import Noticia
from noticias_feed import ResultadoNoticias


def _leitura(indicador, valor, data_coleta):
    return LeituraIndicador(
        indicador=indicador,
        referencia="2026",
        data_coleta=data_coleta,
        mediana=valor,
        media=valor,
        minimo=valor - 0.2,
        maximo=valor + 0.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def _historico_focus():
    return [
        _leitura("Selic", 13.75, date(2026, 7, 28)),
        _leitura("Selic", 14.0, date(2026, 8, 4)),
        _leitura("IPCA", 4.8, date(2026, 7, 28)),
        _leitura("IPCA", 5.0, date(2026, 8, 4)),
    ]


def _serie(codigo, nome, unidade, anterior, atual):
    return SerieMercado(
        codigo=codigo,
        nome=nome,
        unidade=unidade,
        fonte="Teste",
        fonte_url="https://example.com",
        pontos=(
            PontoMercado(date(2026, 7, 1), anterior),
            PontoMercado(date(2026, 8, 4), atual),
        ),
    )


def _mercados():
    return ResultadoMercados(
        series=(
            _serie("USDBRL", "Dólar PTAX", "R$", 5.0, 5.2),
            _serie(
                "BRENT",
                "Petróleo Brent",
                "US$/barril",
                80.0,
                88.0,
            ),
            _serie(
                "BTCBRL",
                "Bitcoin",
                "R$",
                400_000,
                420_000,
            ),
        )
    )


def _noticias():
    return ResultadoNoticias(
        noticias=(
            Noticia(
                titulo="Inflação e juros no radar do mercado",
                link="https://example.com/noticia",
                fonte="Teste",
                publicada_em=datetime(2026, 8, 4, tzinfo=UTC),
            ),
        )
    )


def test_radar_macro_renderiza_precos_cenario_e_linhas():
    pagina = (
        Path(__file__).resolve().parent.parent
        / "pages"
        / "2_Radar_Macro.py"
    )
    with (
        patch.object(
            pagina_macro,
            "_carregar_mercados",
            return_value=_mercados(),
        ),
        patch.object(
            pagina_macro,
            "_carregar_noticias_macro",
            return_value=_noticias(),
        ),
        patch.object(
            pagina_macro,
            "carregar_cache",
            return_value=_historico_focus(),
        ),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Sinais, cenário e preços"
    assert [metrica.label for metrica in app.metric[:3]] == [
        "Dólar PTAX",
        "Petróleo Brent",
        "Bitcoin",
    ]
    assert "As linhas do mercado" in [
        elemento.value for elemento in app.subheader
    ]
    assert len(app.get("vega_lite_chart")) == 2
