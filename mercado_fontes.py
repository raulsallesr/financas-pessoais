"""Adaptadores públicos para dólar PTAX, Brent e Bitcoin."""

from __future__ import annotations

import csv
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import requests

from mercado_data import PontoMercado, SerieMercado, consolidar_pontos

TIMEOUT_SEGUNDOS = 15
MAX_BYTES = 2_000_000
USER_AGENT = "financas-pessoais/1.0 (radar macro de uso pessoal)"

PTAX_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarPeriodo(dataInicial=@dataInicial,"
    "dataFinalCotacao=@dataFinalCotacao)"
)
PTAX_FONTE_URL = (
    "https://dadosabertos.bcb.gov.br/dataset/"
    "dolar-americano-usd-todos-os-boletins-diarios"
)
FRED_BRENT_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FRED_BRENT_FONTE_URL = (
    "https://fred.stlouisfed.org/series/DCOILBRENTEU"
)
BINANCE_URL = "https://data-api.binance.vision/api/v3/klines"
BINANCE_FONTE_URL = (
    "https://developers.binance.com/en/docs/products/spot/rest-api"
)


@dataclass(frozen=True)
class ResultadoMercados:
    series: tuple[SerieMercado, ...]
    fontes_indisponiveis: tuple[str, ...] = ()


class ErroFonteMercado(Exception):
    """Falha isolada ao consultar ou interpretar uma série pública."""


def _get(url: str, *, params: dict) -> requests.Response:
    try:
        resposta = requests.get(
            url,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SEGUNDOS,
        )
        resposta.raise_for_status()
    except requests.RequestException as erro:
        raise ErroFonteMercado(
            "A fonte de mercado não respondeu agora."
        ) from erro
    if len(resposta.content) > MAX_BYTES:
        raise ErroFonteMercado("A resposta da fonte excedeu o limite.")
    return resposta


def buscar_dolar_ptax(*, dias: int = 100) -> SerieMercado:
    fim = date.today()
    inicio = fim - timedelta(days=dias)
    resposta = _get(
        PTAX_URL,
        params={
            "@dataInicial": f"'{inicio:%m-%d-%Y}'",
            "@dataFinalCotacao": f"'{fim:%m-%d-%Y}'",
            "$format": "json",
            "$select": "cotacaoVenda,dataHoraCotacao",
        },
    )
    try:
        linhas = resposta.json()["value"]
        pontos = [
            PontoMercado(
                data=datetime.fromisoformat(
                    linha["dataHoraCotacao"]
                ).date(),
                valor=float(linha["cotacaoVenda"]),
            )
            for linha in linhas
        ]
    except (KeyError, TypeError, ValueError) as erro:
        raise ErroFonteMercado(
            "A PTAX respondeu em um formato inesperado."
        ) from erro
    pontos_consolidados = consolidar_pontos(pontos)
    if not pontos_consolidados:
        raise ErroFonteMercado("A PTAX não retornou cotações.")
    return SerieMercado(
        codigo="USDBRL",
        nome="Dólar PTAX",
        unidade="R$",
        fonte="Banco Central",
        fonte_url=PTAX_FONTE_URL,
        pontos=pontos_consolidados,
    )


def buscar_brent(*, dias: int = 120) -> SerieMercado:
    fim = date.today()
    inicio = fim - timedelta(days=dias)
    resposta = _get(
        FRED_BRENT_URL,
        params={
            "id": "DCOILBRENTEU",
            "cosd": inicio.isoformat(),
            "coed": fim.isoformat(),
        },
    )
    try:
        linhas = csv.DictReader(io.StringIO(resposta.text))
        pontos = [
            PontoMercado(
                data=date.fromisoformat(linha["observation_date"]),
                valor=float(linha["DCOILBRENTEU"]),
            )
            for linha in linhas
            if linha.get("DCOILBRENTEU") not in (None, "", ".")
        ]
    except (KeyError, TypeError, ValueError) as erro:
        raise ErroFonteMercado(
            "O FRED respondeu em um formato inesperado."
        ) from erro
    pontos_consolidados = consolidar_pontos(pontos)
    if not pontos_consolidados:
        raise ErroFonteMercado("O FRED não retornou cotações do Brent.")
    return SerieMercado(
        codigo="BRENT",
        nome="Petróleo Brent",
        unidade="US$/barril",
        fonte="EIA via FRED",
        fonte_url=FRED_BRENT_FONTE_URL,
        pontos=pontos_consolidados,
    )


def buscar_bitcoin(*, dias: int = 100) -> SerieMercado:
    limite = min(max(dias, 30), 1000)
    resposta = _get(
        BINANCE_URL,
        params={
            "symbol": "BTCBRL",
            "interval": "1d",
            "limit": limite,
        },
    )
    try:
        linhas = resposta.json()
        pontos = [
            PontoMercado(
                data=datetime.fromtimestamp(
                    int(linha[0]) / 1000,
                    tz=UTC,
                ).date(),
                valor=float(linha[4]),
            )
            for linha in linhas
        ]
    except (IndexError, TypeError, ValueError) as erro:
        raise ErroFonteMercado(
            "A Binance respondeu em um formato inesperado."
        ) from erro
    pontos_consolidados = consolidar_pontos(pontos)
    if not pontos_consolidados:
        raise ErroFonteMercado("A Binance não retornou cotações do Bitcoin.")
    return SerieMercado(
        codigo="BTCBRL",
        nome="Bitcoin",
        unidade="R$",
        fonte="Binance",
        fonte_url=BINANCE_FONTE_URL,
        pontos=pontos_consolidados,
    )


def buscar_mercados() -> ResultadoMercados:
    fontes = {
        "Dólar PTAX": buscar_dolar_ptax,
        "Petróleo Brent": buscar_brent,
        "Bitcoin": buscar_bitcoin,
    }
    series: list[SerieMercado] = []
    indisponiveis: list[str] = []
    with ThreadPoolExecutor(max_workers=len(fontes)) as executor:
        futuros = {
            executor.submit(funcao): nome
            for nome, funcao in fontes.items()
        }
        for futuro in as_completed(futuros):
            nome = futuros[futuro]
            try:
                series.append(futuro.result())
            except ErroFonteMercado:
                indisponiveis.append(nome)
    ordem = {"USDBRL": 0, "BRENT": 1, "BTCBRL": 2}
    return ResultadoMercados(
        series=tuple(
            sorted(series, key=lambda serie: ordem.get(serie.codigo, 99))
        ),
        fontes_indisponiveis=tuple(sorted(indisponiveis)),
    )
