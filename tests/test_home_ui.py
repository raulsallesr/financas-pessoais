import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

import pagina_home
from focus_data import LeituraIndicador


def _leitura(indicador: str) -> LeituraIndicador:
    return LeituraIndicador(
        indicador=indicador,
        referencia="2026",
        data_coleta=date(2026, 8, 4),
        mediana=5.0,
        media=5.0,
        minimo=4.8,
        maximo=5.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def test_home_mostra_status_e_entrada_compacta():
    pagina = Path(__file__).resolve().parent.parent / "app_financas.py"
    with (
        patch.object(
            pagina_home,
            "carregar_cache",
            return_value=[_leitura("Selic"), _leitura("IPCA")],
        ),
        patch.object(pagina_home.pagina_focus, "render_secao") as focus,
        patch.object(pagina_home.pagina_curva, "render_secao") as curva,
        patch.object(
            pagina_home.pagina_convergencia,
            "render_secao",
        ) as convergencia,
        patch.object(
            pagina_home.pagina_macro,
            "render_secao",
            return_value=(None, []),
        ) as macro,
        patch.object(pagina_home.pagina_carteira, "render") as carteira,
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Finanças pessoais"
    assert "Expectativas, curva, mercados e carteira em uma leitura só." in [
        item.value for item in app.markdown
    ]
    assert not app.header
    assert not app.subheader
    assert not app.get("page_link")
    assert "2 indicadores" in " ".join(
        elemento.value for elemento in app.caption
    )
    menu = " ".join(
        elemento.value for elemento in app.sidebar.markdown
    )
    assert "#boletim-focus" in menu
    assert "#curva-tesouro" in menu
    assert "#focus-curva" in menu
    assert "#radar-macro" in menu
    assert "#minha-carteira" in menu
    assert "#visao-geral" not in menu
    assert menu.count("<a href=") == 5
    assert "<svg" in menu
    assert "material-symbols-rounded" not in menu
    markdown = " ".join(elemento.value for elemento in app.markdown)
    assert 'class="fp-skip-link"' in markdown
    assert 'href="#boletim-focus"' in markdown
    assert "fp-step-index" not in markdown
    focus.assert_called_once_with()
    curva.assert_called_once_with()
    convergencia.assert_called_once_with()
    macro.assert_called_once_with()
    carteira.assert_called_once_with(None, [])
