import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.adapters.noticias_artigo import (
    PALAVRAS_TRECHO,
    ErroLeituraArtigo,
    buscar_artigo,
)
from focuslens.core.noticias_data import Noticia


class RespostaFake:
    def __init__(
        self,
        *,
        url,
        conteudo=b"",
        texto="",
        status_code=200,
        content_type="text/html; charset=utf-8",
        headers=None,
    ):
        self.url = url
        self.content = conteudo
        self.text = texto
        self.status_code = status_code
        self.encoding = "utf-8"
        self.headers = {
            "Content-Type": content_type,
            **(headers or {}),
        }

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(str(self.status_code))

    def iter_content(self, chunk_size):
        del chunk_size
        yield self.content


def _noticia(link="https://www.infomoney.com.br/economia/materia/"):
    return Noticia(
        titulo="Inflação e juros entram no radar",
        link=link,
        fonte="InfoMoney",
        publicada_em=datetime(2026, 8, 7, tzinfo=UTC),
    )


def _html_artigo():
    paragrafo_1 = " ".join(
        [
            "O Banco Central acompanha a inflação e os juros.",
            "Os preços dos alimentos sobem no mercado doméstico.",
        ]
        * 8
    )
    paragrafo_2 = " ".join(
        [
            "O relatório cita IPCA de 5,2% e dívida de R$ 1,4 bilhão.",
            "A próxima decisão do Copom segue no radar.",
        ]
        * 5
    )
    return f"""
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="description"
              content="Inflação e juros orientam o debate econômico desta semana.">
      </head>
      <body>
        <nav><p>Texto de navegação que deve ficar fora do artigo.</p></nav>
        <article>
          <p>{paragrafo_1}</p>
          <aside><p>Publicidade que nunca pode entrar na análise.</p></aside>
          <p>{paragrafo_2}</p>
        </article>
      </body>
    </html>
    """.encode()


@patch("focuslens.adapters.noticias_artigo.requests.get")
def test_buscar_artigo_respeita_robots_e_extrai_so_conteudo(mock_get):
    mock_get.side_effect = [
        RespostaFake(
            url="https://www.infomoney.com.br/robots.txt",
            texto="User-agent: *\nAllow: /",
            content_type="text/plain",
        ),
        RespostaFake(
            url=_noticia().link,
            conteudo=_html_artigo(),
        ),
    ]

    artigo = buscar_artigo(_noticia())

    assert artigo.origem == "Texto da matéria"
    assert artigo.palavras >= 80
    assert "navegação" not in artigo.texto
    assert "Publicidade" not in artigo.texto
    assert len(artigo.trecho_verificacao.rstrip("…").split()) <= PALAVRAS_TRECHO
    assert all(
        chamada.kwargs["allow_redirects"] is False
        for chamada in mock_get.call_args_list
    )


@patch("focuslens.adapters.noticias_artigo.requests.get")
def test_buscar_artigo_recusa_quando_robots_bloqueia(mock_get):
    mock_get.return_value = RespostaFake(
        url="https://www.infomoney.com.br/robots.txt",
        texto="User-agent: *\nDisallow: /economia/",
        content_type="text/plain",
    )

    with pytest.raises(ErroLeituraArtigo, match="não autoriza"):
        buscar_artigo(_noticia())


@patch("focuslens.adapters.noticias_artigo.requests.get")
def test_buscar_artigo_recusa_host_fora_da_fonte_sem_rede(mock_get):
    with pytest.raises(ErroLeituraArtigo, match="não pertence"):
        buscar_artigo(_noticia("https://exemplo-malicioso.test/materia"))
    mock_get.assert_not_called()


@patch("focuslens.adapters.noticias_artigo.requests.get")
def test_buscar_artigo_recusa_redirecionamento_para_host_externo(mock_get):
    mock_get.side_effect = [
        RespostaFake(
            url="https://www.infomoney.com.br/robots.txt",
            texto="User-agent: *\nAllow: /",
            content_type="text/plain",
        ),
        RespostaFake(
            url=_noticia().link,
            status_code=302,
            headers={"Location": "https://rede-interna.test/conteudo"},
        ),
    ]

    with pytest.raises(ErroLeituraArtigo, match="não pertence"):
        buscar_artigo(_noticia())
