import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

import pagina_curva
from curva_data import PontoCurva


HOJE = date.today()


def _datas_uteis(total: int) -> list[date]:
    datas = []
    cursor = HOJE
    while len(datas) < total:
        if cursor.weekday() < 5:
            datas.append(cursor)
        cursor -= timedelta(days=1)
    return sorted(datas)


def _historico() -> list[PontoCurva]:
    pontos = []
    for indice, data_ref in enumerate(_datas_uteis(22)):
        for ano, premio in ((2028, 0.0), (2030, 0.3), (2032, 0.6)):
            taxa = 13.0 + premio + indice * 0.01
            pontos.append(
                PontoCurva(
                    data_referencia=data_ref,
                    tipo_titulo="Tesouro Prefixado",
                    vencimento=date(ano, 1, 1),
                    taxa_compra=taxa,
                    taxa_venda=taxa + 0.12,
                    pu_compra=800.0,
                    pu_venda=799.0,
                    fonte="Teste",
                )
            )
    return pontos


def test_curva_renderiza_resumo_grafico_e_tabela_acessivel():
    pagina = Path(__file__).resolve().parent / "apps" / "curva_section.py"
    with patch.object(
        pagina_curva,
        "_obter_pontos",
        return_value=_historico(),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.header[0].value == "Como mudaram as taxas prefixadas"
    assert "Taxas prefixadas subiram frente a D-5" in [
        elemento.value for elemento in app.subheader
    ]
    assert [metrica.label for metrica in app.metric[:4]] == [
        "Mediana D-5",
        "Ponta curta",
        "Ponta longa",
        "Inclinação atual",
    ]
    assert len(app.get("vega_lite_chart")) == 1
    assert len(app.dataframe) == 1
    assert any(
        "Atualizada" in elemento.value for elemento in app.markdown
    )


def test_curva_indisponivel_nao_quebra_as_outras_secoes():
    pagina = Path(__file__).resolve().parent / "apps" / "curva_section.py"
    with patch.object(pagina_curva, "_obter_pontos", return_value=[]):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert "Curva prefixada indisponível no momento" in [
        elemento.value for elemento in app.subheader
    ]
    assert not app.metric
    assert not app.get("vega_lite_chart")
