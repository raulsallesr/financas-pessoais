from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ativos.core.linguagem import textos_proibidos, validar_textos
from ativos.ui import pagina_ativos

RAIZ = Path(__file__).resolve().parent.parent
APP_ATIVOS = Path(__file__).parent / "fixtures" / "app_ativos.py"


def test_pagina_ativos_mostra_fases_e_aviso_de_uso_pessoal():
    app = AppTest.from_file(str(APP_ATIVOS), default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Ativos B3"
    assert pagina_ativos.AVISO in [item.value for item in app.caption]
    tabela = app.dataframe[0].value
    assert list(tabela["Fase"]) == [fase for fase, _, _ in pagina_ativos.ETAPAS]


def test_textos_do_modulo_ativos_respeitam_guardrail_de_linguagem():
    textos = [pagina_ativos.AVISO, *(entrega for _, entrega, _ in pagina_ativos.ETAPAS)]

    assert textos_proibidos(textos) == []


def test_guardrail_bloqueia_ordem_e_preco_alvo():
    assert textos_proibidos(["Compre agora", "preço-alvo de R$ 30", "faixa estimada"]) == [
        "Compre agora",
        "preço-alvo de R$ 30",
    ]
    with pytest.raises(ValueError, match="incompatível"):
        validar_textos(["Compre agora"])


def test_entrypoint_navega_entre_macro_e_ativos():
    codigo = (RAIZ / "app_financas.py").read_text(encoding="utf-8")

    assert "st.navigation" in codigo
    assert 'url_path="macro", default=True' in codigo
    assert 'url_path="ativos"' in codigo
    assert 'url_path="busca-acoes"' in codigo
    assert 'url_path="busca-fiis"' in codigo
