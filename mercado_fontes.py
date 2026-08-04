"""Adaptadores públicos para preços, CDI e Selic usados no Radar."""

from __future__ import annotations

import csv
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, date, datetime, time

import requests

from mercado_data import (
    PontoMercado,
    SerieMercado,
    acumular_taxas_diarias,
    consolidar_pontos,
)

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
SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
SGS_SELIC_FONTE_URL = (
    "https://dadosabertos.bcb.gov.br/dataset/11-taxa-de-juros---selic"
)
SGS_CDI_FONTE_URL = (
    "https://www3.bcb.gov.br/sgspub/consultarvalores/"
    "consultarValoresSeries.do?method=consultarSeries&series=12"
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


def _periodo_ano(
    inicio: date | None,
    fim: date | None,
) -> tuple[date, date]:
    data_final = fim or date.today()
    data_inicial = inicio or date(data_final.year, 1, 1)
    if data_inicial > data_final:
        raise ValueError("A data inicial não pode ser posterior à final.")
    return data_inicial, data_final


def buscar_dolar_ptax(
    *,
    inicio: date | None = None,
    fim: date | None = None,
) -> SerieMercado:
    inicio, fim = _periodo_ano(inicio, fim)
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


def buscar_brent(
    *,
    inicio: date | None = None,
    fim: date | None = None,
) -> SerieMercado:
    inicio, fim = _periodo_ano(inicio, fim)
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


def buscar_bitcoin(
    *,
    inicio: date | None = None,
    fim: date | None = None,
) -> SerieMercado:
    inicio, fim = _periodo_ano(inicio, fim)
    inicio_ms = int(
        datetime.combine(inicio, time.min, tzinfo=UTC).timestamp() * 1000
    )
    fim_ms = int(
        datetime.combine(fim, time.max, tzinfo=UTC).timestamp() * 1000
    )
    resposta = _get(
        BINANCE_URL,
        params={
            "symbol": "BTCBRL",
            "interval": "1d",
            "startTime": inicio_ms,
            "endTime": fim_ms,
            "limit": 1000,
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


def _buscar_indice_taxa_sgs(
    *,
    codigo_sgs: int,
    codigo: str,
    nome: str,
    fonte_url: str,
    inicio: date | None = None,
    fim: date | None = None,
) -> SerieMercado:
    inicio, fim = _periodo_ano(inicio, fim)
    resposta = _get(
        SGS_URL.format(codigo=codigo_sgs),
        params={
            "formato": "json",
            "dataInicial": inicio.strftime("%d/%m/%Y"),
            "dataFinal": fim.strftime("%d/%m/%Y"),
        },
    )
    try:
        pontos_taxa = [
            PontoMercado(
                data=datetime.strptime(linha["data"], "%d/%m/%Y").date(),
                valor=float(linha["valor"]),
            )
            for linha in resposta.json()
        ]
    except (KeyError, TypeError, ValueError) as erro:
        raise ErroFonteMercado(
            f"O Banco Central respondeu a série {nome} "
            "em um formato inesperado."
        ) from erro
    pontos = acumular_taxas_diarias(pontos_taxa)
    if not pontos:
        raise ErroFonteMercado(
            f"O Banco Central não retornou observações de {nome}."
        )
    return SerieMercado(
        codigo=codigo,
        nome=nome,
        unidade="Índice acumulado",
        fonte="Banco Central (SGS)",
        fonte_url=fonte_url,
        pontos=pontos,
    )


def buscar_cdi(
    *,
    inicio: date | None = None,
    fim: date | None = None,
) -> SerieMercado:
    return _buscar_indice_taxa_sgs(
        codigo_sgs=12,
        codigo="CDI",
        nome="CDI acumulado",
        fonte_url=SGS_CDI_FONTE_URL,
        inicio=inicio,
        fim=fim,
    )


def buscar_selic(
    *,
    inicio: date | None = None,
    fim: date | None = None,
) -> SerieMercado:
    return _buscar_indice_taxa_sgs(
        codigo_sgs=11,
        codigo="SELIC",
        nome="Selic acumulada",
        fonte_url=SGS_SELIC_FONTE_URL,
        inicio=inicio,
        fim=fim,
    )


def buscar_mercados() -> ResultadoMercados:
    fontes = {
        "Dólar PTAX": buscar_dolar_ptax,
        "Petróleo Brent": buscar_brent,
        "Bitcoin": buscar_bitcoin,
        "CDI": buscar_cdi,
        "Selic": buscar_selic,
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
    ordem = {
        "USDBRL": 0,
        "BRENT": 1,
        "BTCBRL": 2,
        "CDI": 3,
        "SELIC": 4,
    }
    return ResultadoMercados(
        series=tuple(
            sorted(series, key=lambda serie: ordem.get(serie.codigo, 99))
        ),
        fontes_indisponiveis=tuple(sorted(indisponiveis)),
    )
