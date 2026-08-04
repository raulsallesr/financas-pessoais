"""Adaptador RSS para manchetes públicas de portais financeiros.

O adaptador lê apenas metadados do feed: título, URL, fonte, publicação e
categorias. O corpo das matérias não é armazenado nem republicado.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import requests

from noticias_data import Noticia, deduplicar_noticias

TIMEOUT_SEGUNDOS = 8
MAX_BYTES_FEED = 1_000_000
USER_AGENT = "financas-pessoais/1.0 (leitor RSS de uso pessoal)"


@dataclass(frozen=True)
class FonteRSS:
    nome: str
    url: str
    hosts_permitidos: frozenset[str]


@dataclass(frozen=True)
class ResultadoNoticias:
    noticias: tuple[Noticia, ...]
    fontes_indisponiveis: tuple[str, ...] = ()


FONTES_RSS = (
    FonteRSS(
        nome="InfoMoney",
        url="https://www.infomoney.com.br/feed/",
        hosts_permitidos=frozenset(
            {"infomoney.com.br", "www.infomoney.com.br"}
        ),
    ),
    FonteRSS(
        nome="Brazil Journal",
        url="https://braziljournal.com/feed/",
        hosts_permitidos=frozenset(
            {"braziljournal.com", "www.braziljournal.com"}
        ),
    ),
)


class ErroFonteNoticias(Exception):
    """Falha isolada ao carregar ou interpretar uma fonte RSS."""


def buscar_fonte(fonte: FonteRSS, limite: int = 10) -> list[Noticia]:
    try:
        resposta = requests.get(
            fonte.url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml"},
            timeout=TIMEOUT_SEGUNDOS,
        )
        resposta.raise_for_status()
    except requests.RequestException as erro:
        raise ErroFonteNoticias(
            f"Não foi possível consultar {fonte.nome}."
        ) from erro

    conteudo = resposta.content
    if len(conteudo) > MAX_BYTES_FEED:
        raise ErroFonteNoticias(f"O feed de {fonte.nome} excedeu o limite.")

    content_type = resposta.headers.get("Content-Type", "").casefold()
    if content_type and "xml" not in content_type and "rss" not in content_type:
        raise ErroFonteNoticias(
            f"{fonte.nome} respondeu em um formato inesperado."
        )

    try:
        raiz = ElementTree.fromstring(conteudo)
    except ElementTree.ParseError as erro:
        raise ErroFonteNoticias(
            f"O feed de {fonte.nome} retornou XML inválido."
        ) from erro

    noticias: list[Noticia] = []
    for item in raiz.findall(".//item"):
        titulo = _texto_filho(item, "title")
        link = _texto_filho(item, "link")
        if not titulo or not _link_permitido(link, fonte):
            continue
        categorias = tuple(
            texto
            for elemento in list(item)
            if _nome_local(elemento.tag) == "category"
            and (texto := (elemento.text or "").strip())
        )
        noticias.append(
            Noticia(
                titulo=titulo,
                link=link,
                fonte=fonte.nome,
                publicada_em=_parse_data(_texto_filho(item, "pubDate")),
                categorias=categorias,
            )
        )
        if len(noticias) == limite:
            break
    return noticias


def buscar_noticias(
    fontes: tuple[FonteRSS, ...] = FONTES_RSS,
    limite_por_fonte: int = 10,
) -> ResultadoNoticias:
    """Consulta fontes em paralelo; uma falha não derruba as demais."""
    noticias: list[Noticia] = []
    indisponiveis: list[str] = []

    with ThreadPoolExecutor(max_workers=max(1, len(fontes))) as executor:
        futuros = {
            executor.submit(buscar_fonte, fonte, limite_por_fonte): fonte
            for fonte in fontes
        }
        for futuro in as_completed(futuros):
            fonte = futuros[futuro]
            try:
                noticias.extend(futuro.result())
            except ErroFonteNoticias:
                indisponiveis.append(fonte.nome)

    return ResultadoNoticias(
        noticias=tuple(deduplicar_noticias(noticias)),
        fontes_indisponiveis=tuple(sorted(indisponiveis)),
    )


def _texto_filho(item: ElementTree.Element, nome: str) -> str:
    for elemento in list(item):
        if _nome_local(elemento.tag) == nome:
            return (elemento.text or "").strip()
    return ""


def _nome_local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _link_permitido(link: str, fonte: FonteRSS) -> bool:
    from urllib.parse import urlsplit

    partes = urlsplit(link.strip())
    return (
        partes.scheme.casefold() == "https"
        and (partes.hostname or "").casefold() in fonte.hosts_permitidos
    )


def _parse_data(valor: str) -> datetime | None:
    if not valor:
        return None
    try:
        return parsedate_to_datetime(valor)
    except (TypeError, ValueError, OverflowError):
        return None
