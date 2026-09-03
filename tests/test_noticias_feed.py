import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.adapters.noticias_feed import (
    FONTES_RSS,
    ErroFonteNoticias,
    FonteRSS,
    buscar_fonte,
    buscar_noticias,
)

RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Focus reduz proje\xc3\xa7\xc3\xa3o do IPCA</title>
      <link>https://www.infomoney.com.br/economia/focus-ipca/</link>
      <pubDate>Tue, 04 Aug 2026 14:00:00 +0000</pubDate>
      <category>Economia</category>
      <description>Corpo que o app n\xc3\xa3o deve armazenar.</description>
    </item>
    <item>
      <title>Link externo malicioso</title>
      <link>https://exemplo-malicioso.test/materia/</link>
      <pubDate>Tue, 04 Aug 2026 13:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>
"""


class RespostaFake:
    def __init__(self, conteudo=RSS, content_type="application/rss+xml"):
        self.content = conteudo
        self.headers = {"Content-Type": content_type}

    def raise_for_status(self):
        return None


FONTE = FonteRSS(
    nome="InfoMoney",
    url="https://www.infomoney.com.br/feed/",
    hosts_permitidos=frozenset(
        {"infomoney.com.br", "www.infomoney.com.br"}
    ),
)


def test_fontes_padrao_cobrem_seis_veiculos_validados():
    assert {fonte.nome for fonte in FONTES_RSS} == {
        "InfoMoney",
        "Brazil Journal",
        "Money Times",
        "Agência Brasil",
        "InvestNews",
        "NeoFeed",
    }


@patch("focuslens.adapters.noticias_feed.requests.get")
def test_buscar_fonte_le_apenas_metadados_e_filtra_host(mock_get):
    mock_get.return_value = RespostaFake()
    noticias = buscar_fonte(FONTE)
    assert len(noticias) == 1
    assert noticias[0].titulo == "Focus reduz projeção do IPCA"
    assert noticias[0].categorias == ("Economia",)
    assert not hasattr(noticias[0], "descricao")
    assert mock_get.call_args.kwargs["timeout"] == 8


@patch("focuslens.adapters.noticias_feed.requests.get")
def test_buscar_fonte_converte_falha_de_rede(mock_get):
    mock_get.side_effect = requests.Timeout("timeout")
    with pytest.raises(ErroFonteNoticias):
        buscar_fonte(FONTE)


@patch("focuslens.adapters.noticias_feed.buscar_fonte")
def test_buscar_noticias_isola_fonte_indisponivel(mock_buscar):
    outra = FonteRSS(
        nome="Brazil Journal",
        url="https://braziljournal.com/feed/",
        hosts_permitidos=frozenset({"braziljournal.com"}),
    )

    def resposta_controlada(fonte, limite):
        if fonte.nome == "Brazil Journal":
            raise ErroFonteNoticias("fora")
        from datetime import UTC, datetime

        from focuslens.core.noticias_data import Noticia

        return [
            Noticia(
                titulo="Selic no radar",
                link="https://www.infomoney.com.br/economia/selic/",
                fonte=fonte.nome,
                publicada_em=datetime(2026, 8, 4, tzinfo=UTC),
            )
        ]

    mock_buscar.side_effect = resposta_controlada
    resultado = buscar_noticias((FONTE, outra))
    assert len(resultado.noticias) == 1
    assert resultado.fontes_indisponiveis == ("Brazil Journal",)
