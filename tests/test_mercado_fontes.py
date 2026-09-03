import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.adapters import mercado_fontes
from focuslens.adapters.mercado_fontes import ErroFonteMercado


def _resposta(*, json_data=None, texto="", conteudo=b"ok"):
    class Resposta:
        content = conteudo
        text = texto

        @staticmethod
        def raise_for_status():
            return None

        @staticmethod
        def json():
            return json_data

    return Resposta()


@patch("focuslens.adapters.mercado_fontes.requests.get")
def test_buscar_dolar_ptax_converte_cotacao_oficial(mock_get):
    mock_get.return_value = _resposta(
        json_data={
            "value": [
                {
                    "cotacaoVenda": 5.1053,
                    "dataHoraCotacao": "2026-08-04 13:05:10.954816",
                }
            ]
        }
    )
    serie = mercado_fontes.buscar_dolar_ptax(
        inicio=date(2026, 1, 1),
        fim=date(2026, 8, 4),
    )
    assert serie.codigo == "USDBRL"
    assert serie.pontos[-1].valor == 5.1053
    assert serie.fonte == "Banco Central"
    assert mock_get.call_args.kwargs["params"]["@dataInicial"] == (
        "'01-01-2026'"
    )


@patch("focuslens.adapters.mercado_fontes.requests.get")
def test_buscar_brent_ignora_observacao_ausente(mock_get):
    texto = (
        "observation_date,DCOILBRENTEU\n"
        "2026-08-01,80.50\n"
        "2026-08-02,.\n"
        "2026-08-03,82.00\n"
    )
    mock_get.return_value = _resposta(
        texto=texto,
        conteudo=texto.encode(),
    )
    serie = mercado_fontes.buscar_brent()
    assert [ponto.valor for ponto in serie.pontos] == [80.5, 82.0]


@patch("focuslens.adapters.mercado_fontes.requests.get")
def test_buscar_bitcoin_usa_fechamento_diario_em_reais(mock_get):
    mock_get.return_value = _resposta(
        json_data=[
            [1785715200000, "320000", "330000", "318000", "325000"],
            [1785801600000, "325000", "335000", "323000", "330872"],
        ]
    )
    serie = mercado_fontes.buscar_bitcoin()
    assert serie.codigo == "BTCBRL"
    assert serie.pontos[-1].valor == 330872.0
    assert mock_get.call_args.kwargs["params"]["limit"] == 1000


@patch("focuslens.adapters.mercado_fontes.requests.get")
def test_buscar_cdi_compoe_taxas_diarias_em_indice(mock_get):
    mock_get.return_value = _resposta(
        json_data=[
            {"data": "02/01/2026", "valor": "0.05"},
            {"data": "05/01/2026", "valor": "0.10"},
        ]
    )
    serie = mercado_fontes.buscar_cdi(
        inicio=date(2026, 1, 1),
        fim=date(2026, 8, 4),
    )
    assert serie.codigo == "CDI"
    assert [ponto.valor for ponto in serie.pontos] == [100.0, 100.1]
    assert mock_get.call_args.kwargs["params"]["dataInicial"] == "01/01/2026"


@patch("focuslens.adapters.mercado_fontes.requests.get")
def test_buscar_selic_usa_serie_diaria_oficial(mock_get):
    mock_get.return_value = _resposta(
        json_data=[
            {"data": "02/01/2026", "valor": "0.05"},
            {"data": "05/01/2026", "valor": "0.06"},
        ]
    )
    serie = mercado_fontes.buscar_selic(
        inicio=date(2026, 1, 1),
        fim=date(2026, 8, 4),
    )
    assert serie.codigo == "SELIC"
    assert "bcdata.sgs.11" in mock_get.call_args.args[0]


@patch("focuslens.adapters.mercado_fontes.requests.get")
def test_erro_de_rede_vira_falha_controlada(mock_get):
    mock_get.side_effect = requests.Timeout("timeout")
    with pytest.raises(ErroFonteMercado):
        mercado_fontes.buscar_brent()


def test_busca_conjunta_preserva_fontes_que_responderam():
    serie = mercado_fontes.SerieMercado(
        codigo="USDBRL",
        nome="Dólar",
        unidade="R$",
        fonte="Teste",
        fonte_url="https://example.com",
        pontos=(),
    )
    with (
        patch.object(
            mercado_fontes,
            "buscar_dolar_ptax",
            return_value=serie,
        ),
        patch.object(
            mercado_fontes,
            "buscar_brent",
            side_effect=ErroFonteMercado("falhou"),
        ),
        patch.object(
            mercado_fontes,
            "buscar_bitcoin",
            side_effect=ErroFonteMercado("falhou"),
        ),
        patch.object(
            mercado_fontes,
            "buscar_cdi",
            side_effect=ErroFonteMercado("falhou"),
        ),
        patch.object(
            mercado_fontes,
            "buscar_selic",
            side_effect=ErroFonteMercado("falhou"),
        ),
    ):
        resultado = mercado_fontes.buscar_mercados()

    assert resultado.series == (serie,)
    assert resultado.fontes_indisponiveis == (
        "Bitcoin",
        "CDI",
        "Petróleo Brent",
        "Selic",
    )
