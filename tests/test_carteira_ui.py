import sys
from io import BytesIO
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest


def _arquivo_b3_sintetico() -> bytes:
    workbook = Workbook()
    acoes = workbook.active
    acoes.title = "Acoes"
    acoes.append(
        ["Produto", "Código de Negociação", "Valor Atualizado"]
    )
    acoes.append(["Empresa", "TEST3 - EMPRESA", 1_500])
    acoes.append([None, None, 1_500])
    saida = BytesIO()
    workbook.save(saida)
    workbook.close()
    return saida.getvalue()


def test_carteira_abre_editor_e_explica_privacidade_da_sessao():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "carteira_section.py"
    )
    app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.header[0].value == "Minha carteira em contexto"
    assert len(app.get("file_uploader")) == 1
    assert len(app.get("dataframe")) == 1
    assert "somente nesta sessão" in " ".join(
        elemento.value for elemento in app.info
    )
    assert "Quando você preencher" in " ".join(
        elemento.value for elemento in app.markdown
    )


def test_upload_b3_preenche_editor_e_mostra_resumo():
    pagina = (
        Path(__file__).resolve().parent / "apps" / "carteira_section.py"
    )
    app = AppTest.from_file(pagina, default_timeout=15).run()
    app.get("file_uploader")[0].upload(
        "posicao.xlsx",
        _arquivo_b3_sintetico(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ).run()

    assert not app.exception
    assert "1 ativos consolidados" in " ".join(
        elemento.value for elemento in app.success
    )
    assert app.metric[0].value == "R$ 1.500,00"
    assert app.metric[1].value == "1"
