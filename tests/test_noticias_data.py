import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from noticias_data import (
    Noticia,
    canonicalizar_link,
    deduplicar_noticias,
    selecionar_destaques,
)


AGORA = datetime(2026, 8, 4, 12, tzinfo=UTC)


def _noticia(titulo, fonte, minutos=0, link=None):
    slug = titulo.casefold().replace(" ", "-")
    return Noticia(
        titulo=titulo,
        link=link or f"https://exemplo.com/{slug}/",
        fonte=fonte,
        publicada_em=AGORA - timedelta(minutes=minutos),
    )


def test_canonicalizar_link_remove_parametros_e_fragmento():
    assert canonicalizar_link(
        "https://EXEMPLO.com/materia/?utm_source=x#trecho"
    ) == "https://exemplo.com/materia"


def test_deduplicar_noticias_por_link_ou_titulo():
    original = _noticia(
        "Selic fica estável",
        "InfoMoney",
        link="https://exemplo.com/selic/?utm_source=a",
    )
    repetida = _noticia(
        "Outra chamada",
        "InfoMoney",
        minutos=5,
        link="https://exemplo.com/selic/",
    )
    mesmo_titulo = _noticia(
        "Selic fica estável",
        "Brazil Journal",
        minutos=10,
    )
    assert deduplicar_noticias([repetida, mesmo_titulo, original]) == [
        original
    ]


def test_selecionar_destaques_prioriza_macro_e_diversifica_fontes():
    noticias = [
        _noticia("WhatsApp muda visual", "InfoMoney"),
        _noticia("Copom discute juros e Selic", "InfoMoney", 5),
        _noticia("IPCA desacelera no mês", "InfoMoney", 10),
        _noticia("Dólar reage ao cenário fiscal", "Brazil Journal", 15),
    ]
    destaques = selecionar_destaques(noticias, limite=3)
    assert len(destaques) == 3
    assert {noticia.fonte for noticia in destaques} == {
        "InfoMoney",
        "Brazil Journal",
    }
    assert all("WhatsApp" not in noticia.titulo for noticia in destaques)
