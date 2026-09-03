"""Leitura segura e efêmera do conteúdo de uma matéria selecionada.

O texto integral existe apenas em memória durante a análise. O adaptador
respeita robots.txt, restringe hosts/fontes, limita tamanho e não persiste
HTML nem conteúdo editorial.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import requests

from focuslens.adapters.noticias_feed import FONTES_RSS, TIMEOUT_SEGUNDOS, USER_AGENT, FonteRSS
from focuslens.core.noticias_data import Noticia, normalizar_texto

MAX_BYTES_ARTIGO = 2_000_000
MAX_PALAVRAS_ARTIGO = 6_000
MIN_PALAVRAS_ARTIGO = 80
PALAVRAS_TRECHO = 18
MAX_REDIRECIONAMENTOS = 4
ROBOTS_USER_AGENT = "financas-pessoais"

_TAGS_IGNORADAS = {
    "aside",
    "button",
    "figcaption",
    "footer",
    "form",
    "nav",
    "noscript",
    "script",
    "style",
    "svg",
}
_INICIOS_DESCARTADOS = (
    "assine ",
    "confira também",
    "conteúdo patrocinado",
    "leia mais",
    "leia também",
    "publicidade",
    "receba nossas",
    "siga ",
    "todos os direitos",
)


@dataclass(frozen=True)
class ArtigoExtraido:
    noticia: Noticia
    descricao: str
    paragrafos: tuple[str, ...]
    palavras: int
    origem: str
    trecho_verificacao: str
    texto: str = field(repr=False)


class ErroLeituraArtigo(Exception):
    """Falha segura ao autorizar, carregar ou extrair uma matéria."""


class _ExtratorParagrafos(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.article_depth = 0
        self.main_depth = 0
        self.ignored_depth = 0
        self.buffer: list[str] | None = None
        self.contexto_paragrafo = ""
        self.paragrafos_article: list[str] = []
        self.paragrafos_main: list[str] = []
        self.paragrafos_todos: list[str] = []
        self.descricoes: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        tag = tag.casefold()
        atributos = {
            nome.casefold(): (valor or "")
            for nome, valor in attrs
        }
        if tag == "meta":
            chave = (
                atributos.get("property")
                or atributos.get("name")
                or ""
            ).casefold()
            if chave in {
                "description",
                "og:description",
                "twitter:description",
            }:
                conteudo = atributos.get("content", "").strip()
                if conteudo:
                    self.descricoes.append(conteudo)
        if tag in _TAGS_IGNORADAS:
            self.ignored_depth += 1
        if tag == "article":
            self.article_depth += 1
        if tag == "main":
            self.main_depth += 1
        if tag == "p" and self.ignored_depth == 0:
            self.buffer = []
            self.contexto_paragrafo = (
                "article"
                if self.article_depth
                else "main"
                if self.main_depth
                else "all"
            )

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag == "p" and self.buffer is not None:
            texto = _limpar_espacos(" ".join(self.buffer))
            if texto:
                self.paragrafos_todos.append(texto)
                if self.contexto_paragrafo == "article":
                    self.paragrafos_article.append(texto)
                if self.contexto_paragrafo in {"article", "main"}:
                    self.paragrafos_main.append(texto)
            self.buffer = None
            self.contexto_paragrafo = ""
        if tag == "article" and self.article_depth:
            self.article_depth -= 1
        if tag == "main" and self.main_depth:
            self.main_depth -= 1
        if tag in _TAGS_IGNORADAS and self.ignored_depth:
            self.ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.buffer is not None and self.ignored_depth == 0:
            self.buffer.append(data)


def buscar_artigo(noticia: Noticia) -> ArtigoExtraido:
    """Lê uma matéria autorizada e devolve texto limpo apenas em memória."""
    fonte = _fonte_configurada(noticia)
    _validar_link(noticia.link, fonte)
    _validar_robots(noticia.link, fonte)

    try:
        resposta = _get_validado(
            noticia.link,
            fonte,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
            },
            timeout=TIMEOUT_SEGUNDOS,
            stream=True,
        )
        resposta.raise_for_status()
    except requests.RequestException as erro:
        raise ErroLeituraArtigo(
            f"Não foi possível abrir a matéria em {noticia.fonte}."
        ) from erro

    _validar_link(resposta.url, fonte)
    content_type = resposta.headers.get("Content-Type", "").casefold()
    if "html" not in content_type:
        raise ErroLeituraArtigo(
            f"{noticia.fonte} respondeu sem conteúdo HTML."
        )

    tamanho_declarado = resposta.headers.get("Content-Length")
    if tamanho_declarado:
        try:
            excedeu_limite = int(tamanho_declarado) > MAX_BYTES_ARTIGO
        except ValueError:
            excedeu_limite = False
        if excedeu_limite:
            raise ErroLeituraArtigo(
                f"A matéria em {noticia.fonte} excedeu o limite de leitura."
            )
    conteudo = _ler_com_limite(resposta)
    encoding = (
        requests.utils.get_encoding_from_headers(resposta.headers)
        or resposta.encoding
        or "utf-8"
    )
    html = conteudo.decode(encoding, errors="replace")
    return _extrair_artigo(noticia, html)


def _validar_robots(url: str, fonte: FonteRSS) -> None:
    partes = urlsplit(url)
    robots_url = urlunsplit(
        (partes.scheme, partes.netloc, "/robots.txt", "", "")
    )
    try:
        resposta = _get_validado(
            robots_url,
            fonte,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException as erro:
        raise ErroLeituraArtigo(
            "Não foi possível verificar a política de leitura da fonte."
        ) from erro

    if resposta.status_code in {401, 403}:
        raise ErroLeituraArtigo(
            "A fonte não autorizou a leitura automatizada desta matéria."
        )
    if resposta.status_code == 404:
        return
    try:
        resposta.raise_for_status()
    except requests.RequestException as erro:
        raise ErroLeituraArtigo(
            "Não foi possível validar a política de leitura da fonte."
        ) from erro

    regras = RobotFileParser()
    regras.set_url(robots_url)
    regras.parse(resposta.text.splitlines())
    if not regras.can_fetch(ROBOTS_USER_AGENT, url):
        raise ErroLeituraArtigo(
            "A fonte não autoriza a leitura automatizada desta matéria."
        )


def _get_validado(
    url: str,
    fonte: FonteRSS,
    **kwargs: object,
) -> requests.Response:
    """Segue somente redirecionamentos HTTPS dentro dos hosts da fonte."""
    atual = url
    for _ in range(MAX_REDIRECIONAMENTOS + 1):
        _validar_link(atual, fonte)
        resposta = requests.get(
            atual,
            allow_redirects=False,
            **kwargs,
        )
        if resposta.status_code not in {301, 302, 303, 307, 308}:
            return resposta
        destino = resposta.headers.get("Location")
        if not destino:
            raise ErroLeituraArtigo(
                "A fonte respondeu com um redirecionamento inválido."
            )
        atual = urljoin(atual, destino)
        fechar = getattr(resposta, "close", None)
        if callable(fechar):
            fechar()
    raise ErroLeituraArtigo(
        "A fonte excedeu o limite seguro de redirecionamentos."
    )


def _ler_com_limite(resposta: requests.Response) -> bytes:
    partes: list[bytes] = []
    tamanho = 0
    for parte in resposta.iter_content(chunk_size=64 * 1024):
        if not parte:
            continue
        tamanho += len(parte)
        if tamanho > MAX_BYTES_ARTIGO:
            raise ErroLeituraArtigo(
                "A matéria excedeu o limite seguro de leitura."
            )
        partes.append(parte)
    return b"".join(partes)


def _extrair_artigo(noticia: Noticia, html: str) -> ArtigoExtraido:
    parser = _ExtratorParagrafos()
    try:
        parser.feed(html)
        parser.close()
    except Exception as erro:
        raise ErroLeituraArtigo(
            f"Não foi possível interpretar a matéria em {noticia.fonte}."
        ) from erro

    descricao = _primeiro_texto_util(parser.descricoes)
    grupos = (
        parser.paragrafos_article,
        parser.paragrafos_main,
        parser.paragrafos_todos,
    )
    paragrafos: tuple[str, ...] = ()
    for grupo in grupos:
        candidatos = _filtrar_paragrafos(grupo)
        if _contar_palavras(candidatos) >= MIN_PALAVRAS_ARTIGO:
            paragrafos = _limitar_palavras(candidatos)
            break

    if not paragrafos and descricao:
        paragrafos = (descricao,)
    palavras = _contar_palavras(paragrafos)
    if palavras < 12:
        raise ErroLeituraArtigo(
            "A fonte abriu, mas não expôs texto suficiente para análise."
        )

    texto = "\n\n".join(paragrafos)
    base_trecho = descricao or paragrafos[0]
    return ArtigoExtraido(
        noticia=noticia,
        descricao=descricao,
        paragrafos=paragrafos,
        palavras=palavras,
        origem=(
            "Texto da matéria"
            if palavras >= MIN_PALAVRAS_ARTIGO
            else "Descrição editorial da página"
        ),
        trecho_verificacao=_trecho_curto(base_trecho),
        texto=texto,
    )


def _fonte_configurada(noticia: Noticia) -> FonteRSS:
    for fonte in FONTES_RSS:
        if fonte.nome == noticia.fonte:
            return fonte
    raise ErroLeituraArtigo("A notícia não pertence a uma fonte autorizada.")


def _validar_link(link: str, fonte: FonteRSS) -> None:
    partes = urlsplit(link.strip())
    if (
        partes.scheme.casefold() != "https"
        or (partes.hostname or "").casefold() not in fonte.hosts_permitidos
        or partes.username
        or partes.password
    ):
        raise ErroLeituraArtigo("O link da matéria não pertence à fonte.")


def _filtrar_paragrafos(paragrafos: list[str]) -> tuple[str, ...]:
    resultado: list[str] = []
    vistos: set[str] = set()
    for paragrafo in paragrafos:
        texto = _limpar_espacos(paragrafo)
        normalizado = normalizar_texto(texto)
        if len(texto) < 40:
            continue
        if any(normalizado.startswith(inicio) for inicio in _INICIOS_DESCARTADOS):
            continue
        if normalizado in vistos:
            continue
        vistos.add(normalizado)
        resultado.append(texto)
    return tuple(resultado)


def _limitar_palavras(paragrafos: tuple[str, ...]) -> tuple[str, ...]:
    resultado: list[str] = []
    total = 0
    for paragrafo in paragrafos:
        palavras = paragrafo.split()
        restante = MAX_PALAVRAS_ARTIGO - total
        if restante <= 0:
            break
        if len(palavras) > restante:
            resultado.append(" ".join(palavras[:restante]))
            break
        resultado.append(paragrafo)
        total += len(palavras)
    return tuple(resultado)


def _primeiro_texto_util(candidatos: list[str]) -> str:
    for candidato in candidatos:
        texto = _limpar_espacos(candidato)
        if len(texto) >= 30:
            return texto
    return ""


def _trecho_curto(texto: str) -> str:
    palavras = texto.split()
    trecho = " ".join(palavras[:PALAVRAS_TRECHO])
    return trecho + ("…" if len(palavras) > PALAVRAS_TRECHO else "")


def _contar_palavras(paragrafos: tuple[str, ...]) -> int:
    return sum(len(paragrafo.split()) for paragrafo in paragrafos)


def _limpar_espacos(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()
