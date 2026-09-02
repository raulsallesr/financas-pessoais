"""Motor puro para organizar manchetes sem depender de rede ou Streamlit."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True)
class Noticia:
    titulo: str
    link: str
    fonte: str
    publicada_em: datetime | None
    categorias: tuple[str, ...] = ()


_TERMOS_PRIORITARIOS = {
    "selic": 5,
    "copom": 5,
    "ipca": 5,
    "inflacao": 5,
    "juros": 5,
    "cambio": 5,
    "dolar": 5,
    "boletim focus": 5,
    "pib": 4,
    "divida publica": 4,
    "fiscal": 4,
    "tesouro direto": 4,
    "renda fixa": 4,
    "economia": 3,
    "credito": 3,
    "mercado": 2,
    "bolsa": 2,
    "investimentos": 2,
    "petroleo": 1,
}


def normalizar_texto(texto: str) -> str:
    """Remove acentos e ruído para comparação, sem alterar o texto exibido."""
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )
    return re.sub(r"\s+", " ", sem_acentos.casefold()).strip()


def canonicalizar_link(link: str) -> str:
    """Remove query e fragmento para deduplicar a mesma matéria."""
    partes = urlsplit(link.strip())
    caminho = partes.path.rstrip("/") or "/"
    return urlunsplit(
        (partes.scheme.casefold(), partes.netloc.casefold(), caminho, "", "")
    )


def pontuar_relevancia(noticia: Noticia) -> int:
    texto = normalizar_texto(
        " ".join((noticia.titulo, *noticia.categorias))
    )
    return sum(
        peso for termo, peso in _TERMOS_PRIORITARIOS.items() if termo in texto
    )


def deduplicar_noticias(noticias: list[Noticia]) -> list[Noticia]:
    """Mantém a versão mais recente de links/títulos repetidos."""
    ordenadas = sorted(noticias, key=_momento_ordenacao, reverse=True)
    vistas: set[str] = set()
    resultado: list[Noticia] = []

    for noticia in ordenadas:
        chaves = {
            f"url:{canonicalizar_link(noticia.link)}",
            f"titulo:{normalizar_texto(noticia.titulo)}",
        }
        if vistas.intersection(chaves):
            continue
        vistas.update(chaves)
        resultado.append(noticia)
    return resultado


def selecionar_destaques(
    noticias: list[Noticia], limite: int = 3
) -> list[Noticia]:
    """Prioriza contexto macro recente e preserva diversidade de fontes."""
    if limite <= 0:
        return []

    unicas = deduplicar_noticias(noticias)
    ordenadas = sorted(
        unicas,
        key=lambda noticia: (
            pontuar_relevancia(noticia),
            _momento_ordenacao(noticia),
        ),
        reverse=True,
    )
    relevantes = [
        noticia for noticia in ordenadas if pontuar_relevancia(noticia) > 0
    ]
    candidatas = relevantes or ordenadas
    maximo_por_fonte = max(1, (limite + 1) // 2)
    contagem_fontes: dict[str, int] = {}
    escolhidas: list[Noticia] = []

    for noticia in candidatas:
        if contagem_fontes.get(noticia.fonte, 0) >= maximo_por_fonte:
            continue
        escolhidas.append(noticia)
        contagem_fontes[noticia.fonte] = (
            contagem_fontes.get(noticia.fonte, 0) + 1
        )
        if len(escolhidas) == limite:
            return escolhidas

    for noticia in candidatas:
        if noticia not in escolhidas:
            escolhidas.append(noticia)
        if len(escolhidas) == limite:
            break
    return escolhidas


def _momento_ordenacao(noticia: Noticia) -> datetime:
    if noticia.publicada_em is None:
        return datetime.min.replace(tzinfo=UTC)
    if noticia.publicada_em.tzinfo is None:
        return noticia.publicada_em.replace(tzinfo=UTC)
    return noticia.publicada_em.astimezone(UTC)
