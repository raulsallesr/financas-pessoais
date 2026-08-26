import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

import pagina_focus
from focus_data import LeituraIndicador
from noticias_analise import (
    AnaliseArtigo,
    ConexaoFocus,
    EvidenciaNumerica,
)
from noticias_data import Noticia
from noticias_feed import ResultadoNoticias


DATA_ATUAL = date.today()
DATA_ANTERIOR = DATA_ATUAL - timedelta(days=7)


def _leitura(indicador, mediana, data_coleta, referencia="2026"):
    return LeituraIndicador(
        indicador=indicador,
        referencia=referencia,
        data_coleta=data_coleta,
        mediana=mediana,
        media=mediana,
        minimo=mediana - 0.2,
        maximo=mediana + 0.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def _historico():
    valores = {
        "Selic": (14.0, 13.75, "R5/2026"),
        "IPCA": (5.03, 5.10, "2026"),
        "Câmbio": (5.20, 5.10, "2026"),
        "PIB Total": (1.99, 1.90, "2026"),
        "IGP-M": (4.54, 4.40, "2026"),
        "Dívida líquida do setor público": (69.9, 69.5, "2026"),
    }
    leituras = []
    for indicador, (atual, anterior, referencia) in valores.items():
        leituras.extend(
            [
                _leitura(
                    indicador,
                    anterior,
                    DATA_ANTERIOR,
                    referencia,
                ),
                _leitura(
                    indicador,
                    atual,
                    DATA_ATUAL,
                    referencia,
                ),
            ]
        )
    return leituras


def _noticias():
    titulos = (
        ("Inflação desacelera no mês", "Agência Brasil"),
        ("Mercado reduz expectativa de inflação", "InfoMoney"),
        ("Dólar sobe com pressão externa", "Money Times"),
        ("Dólar avança diante do real", "InvestNews"),
        ("Copom mantém Selic", "NeoFeed"),
    )
    return ResultadoNoticias(
        noticias=tuple(
            Noticia(
                titulo=titulo,
                link=f"https://exemplo.com/noticia-{indice}",
                fonte=fonte,
                publicada_em=datetime(
                    2026, 8, 4, 14 - indice, tzinfo=UTC
                ),
            )
            for indice, (titulo, fonte) in enumerate(titulos)
        )
    )


def _analise(noticia):
    return AnaliseArtigo(
        noticia=noticia,
        origem="Texto da matéria",
        palavras_lidas=420,
        temas=("Inflação",),
        sintese="A matéria concentra-se em inflação.",
        conexoes=(
            ConexaoFocus(
                tema="Inflação",
                indicador_focus="IPCA",
                relacao="Em tensão",
                explicacao=(
                    "A matéria sinaliza pressão de alta nos preços, "
                    "mas IPCA caiu no Focus."
                ),
            ),
        ),
        numeros=(
            EvidenciaNumerica(valor="5,2%", contexto="Inflação"),
        ),
        instituicoes=("Banco Central do Brasil",),
        onde_olhar=("Próxima leitura do IPCA",),
        trecho_verificacao="A inflação voltou ao radar nesta semana.",
        limitacao="Leitura automatizada; confira a matéria.",
    )


def test_pagina_focus_substitui_historico_por_leitura_multifuente():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "focus_section.py"
    )
    with (
        patch.object(
            pagina_focus, "carregar_cache", return_value=_historico()
        ),
        patch.object(
            pagina_focus,
            "data_ultima_atualizacao_cache",
            return_value=DATA_ATUAL,
        ),
        patch.object(
            pagina_focus,
            "_carregar_noticias",
            return_value=_noticias(),
        ),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.header[0].value == "O que mudou no Focus"
    subtitulos = [elemento.value for elemento in app.subheader]
    assert "Noticiário x Focus" in subtitulos
    assert "Histórico" not in subtitulos
    assert [metrica.label for metrica in app.metric[:3]] == [
        "Selic",
        "Câmbio",
        "PIB Total",
    ]
    assert "Selic liderou as revisões de alta" in subtitulos
    assert any(
        "Atualizado" in elemento.value
        for elemento in app.markdown
    )
    assert not app.get("vega_lite_chart")
    assert not app.get("link_button")
    assert "5 fontes" in " ".join(
        elemento.value for elemento in app.caption
    )
    assert any(
        elemento.label == "Analisar matéria"
        for elemento in app.button
    )


def test_pagina_focus_aprofunda_materia_so_depois_do_clique():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "focus_section.py"
    )
    with (
        patch.object(
            pagina_focus, "carregar_cache", return_value=_historico()
        ),
        patch.object(
            pagina_focus,
            "data_ultima_atualizacao_cache",
            return_value=DATA_ATUAL,
        ),
        patch.object(
            pagina_focus,
            "_carregar_noticias",
            return_value=_noticias(),
        ),
        patch.object(
            pagina_focus,
            "_carregar_analise_artigo",
        ) as carregar_analise,
    ):
        carregar_analise.side_effect = (
            lambda noticia, comparativos: _analise(noticia)
        )
        app = AppTest.from_file(pagina, default_timeout=15).run()
        carregar_analise.assert_not_called()

        botao = next(
            elemento
            for elemento in app.button
            if elemento.label == "Analisar matéria"
        )
        app = botao.click().run()

    assert not app.exception
    carregar_analise.assert_called_once()
    textos = " ".join(elemento.value for elemento in app.markdown)
    assert "O que encontramos" in textos
    assert "Como isso conversa com o Focus" in textos
    assert "5,2%" in textos
    assert "Banco Central do Brasil" in textos
    assert "Próxima leitura do IPCA" in textos


def test_pagina_focus_busca_primeiro_historico_automaticamente():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "focus_section.py"
    )
    with (
        patch.object(pagina_focus, "carregar_cache", return_value=[]),
        patch.object(
            pagina_focus,
            "data_ultima_atualizacao_cache",
            return_value=None,
        ),
        patch.object(
            pagina_focus,
            "atualizar_e_obter_historico",
            return_value=_historico(),
        ) as atualizar,
        patch.object(
            pagina_focus,
            "_carregar_noticias",
            return_value=_noticias(),
        ),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    atualizar.assert_called_once_with()
    assert [metrica.label for metrica in app.metric[:3]] == [
        "Selic",
        "Câmbio",
        "PIB Total",
    ]


def test_pagina_focus_explica_quando_nao_ha_mudanca_relevante():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "focus_section.py"
    )
    historico = []
    valores = {
        "Selic": (14.08, 14.0, "R6/2026"),
        "IPCA": (5.04, 5.0, "2026"),
        "Câmbio": (5.04, 5.0, "2026"),
        "PIB Total": (1.04, 1.0, "2026"),
    }
    for indicador, (atual, anterior, referencia) in valores.items():
        historico.extend(
            [
                _leitura(
                    indicador,
                    anterior,
                    DATA_ANTERIOR,
                    referencia,
                ),
                _leitura(
                    indicador,
                    atual,
                    DATA_ATUAL,
                    referencia,
                ),
            ]
        )

    with (
        patch.object(
            pagina_focus,
            "carregar_cache",
            return_value=historico,
        ),
        patch.object(
            pagina_focus,
            "data_ultima_atualizacao_cache",
            return_value=DATA_ATUAL,
        ),
        patch.object(
            pagina_focus,
            "_carregar_noticias",
            return_value=ResultadoNoticias(noticias=()),
        ),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert any(
        "Sem mudança relevante" in elemento.value
        for elemento in app.markdown
    )
    assert "Expectativas seguem praticamente estáveis" in [
        elemento.value for elemento in app.subheader
    ]


def test_pagina_focus_mostra_estado_indisponivel_sem_historico():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "focus_section.py"
    )
    with (
        patch.object(pagina_focus, "carregar_cache", return_value=[]),
        patch.object(
            pagina_focus,
            "data_ultima_atualizacao_cache",
            return_value=None,
        ),
        patch.object(
            pagina_focus,
            "atualizar_e_obter_historico",
            return_value=[],
        ),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert any(
        "Indisponível" in elemento.value
        for elemento in app.markdown
    )
    assert "Focus indisponível no momento" in [
        elemento.value for elemento in app.subheader
    ]
