import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

import pagina_home
from pagina_macro import DadosRadar


def test_home_consolida_jornada_e_reutiliza_radar_na_carteira():
    pagina = Path(__file__).resolve().parent.parent / "app_financas.py"
    resumo_integrado = object()
    dados_radar = DadosRadar(
        cenario=None,
        series=(),
        noticias=(),
        fontes_indisponiveis=(),
    )
    with (
        patch.object(
            pagina_home.pagina_resumo,
            "carregar_resumo",
            return_value=resumo_integrado,
        ) as carregar_resumo,
        patch.object(
            pagina_home.pagina_resumo,
            "render_secao",
        ) as renderizar_resumo,
        patch.object(
            pagina_home.pagina_resumo,
            "renderizar_contexto_radar",
        ) as contexto_radar,
        patch.object(
            pagina_home.pagina_macro,
            "carregar_dados_radar",
            return_value=dados_radar,
        ) as carregar_radar,
        patch.object(pagina_home.pagina_focus, "render_secao") as focus,
        patch.object(pagina_home.pagina_curva, "render_secao") as curva,
        patch.object(pagina_home.pagina_carteira, "render") as carteira,
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "FocusLens BR"
    assert (
        "Expectativas, curva e carteira em uma sequência única, com prova, "
        "data e limite perto de cada leitura."
    ) in [
        item.value for item in app.markdown
    ]
    assert not app.header
    assert not app.subheader
    assert not app.get("page_link")
    menu = " ".join(
        elemento.value for elemento in app.sidebar.markdown
    )
    assert "#resumo" in menu
    assert "#expectativas" in menu
    assert "#curva" in menu
    assert "#carteira" in menu
    assert "#focus-curva" not in menu
    assert "#radar-macro" not in menu
    assert "#visao-geral" not in menu
    assert menu.count("<a href=") == 4
    assert "<svg" in menu
    assert "material-symbols-rounded" not in menu
    markdown = " ".join(elemento.value for elemento in app.markdown)
    assert 'class="fp-skip-link"' in markdown
    assert 'href="#resumo"' in markdown
    assert "fp-step-index" not in markdown
    carregar_resumo.assert_called_once_with()
    renderizar_resumo.assert_called_once_with(resumo_integrado)
    carregar_radar.assert_called_once_with()
    contexto_radar.assert_called_once_with(None)
    focus.assert_called_once_with()
    curva.assert_called_once_with()
    carteira.assert_called_once_with(None, [])
