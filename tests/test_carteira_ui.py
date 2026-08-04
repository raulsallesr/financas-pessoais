import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest


def test_carteira_abre_editor_e_explica_privacidade_da_sessao():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "carteira_section.py"
    )
    app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.header[0].value == "Minha carteira em contexto"
    assert len(app.get("dataframe")) == 1
    assert "somente nesta sessão" in " ".join(
        elemento.value for elemento in app.info
    )
    assert "Quando você preencher" in " ".join(
        elemento.value for elemento in app.markdown
    )
