import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

from focuslens.ui import pagina_convergencia
from focuslens.core.convergencia_modelo import (
    DirecaoSinal,
    EstadoConvergencia,
    LeituraConvergencia,
    SinalCurva,
    SinalFocus,
    SinalPonta,
)


def _leitura_publicavel() -> LeituraConvergencia:
    focus = SinalFocus(
        referencia="R6/2026",
        data_anterior=date(2026, 8, 14),
        data_atual=date(2026, 8, 21),
        valor_anterior=13.75,
        valor_atual=13.75,
        delta_pp=0.0,
        direcao=DirecaoSinal.ESTAVEL,
    )
    curva = SinalCurva(
        data_anterior=date(2026, 8, 19),
        data_atual=date(2026, 8, 26),
        delta_mediano_bps=-24.0,
        vencimentos_comparaveis=5,
        direcao=DirecaoSinal.BENIGNA,
    )
    curta = SinalPonta(
        nome="Ponta curta",
        delta_mediano_bps=-6.5,
        vencimentos=(date(2027, 1, 1), date(2028, 1, 1)),
        direcao=DirecaoSinal.BENIGNA,
    )
    longa = SinalPonta(
        nome="Ponta longa",
        delta_mediano_bps=-29.0,
        vencimentos=(date(2031, 1, 1), date(2032, 1, 1)),
        direcao=DirecaoSinal.BENIGNA,
    )
    return LeituraConvergencia(
        estado=EstadoConvergencia.CURVA_MAIS_BENIGNA,
        titulo="A curva ficou mais benigna que o Focus",
        resumo="Focus estável e curva em queda frente a D-5.",
        focus=focus,
        curva=curva,
        ponta_curta=curta,
        ponta_longa=longa,
        evidencias=(
            "Focus: 13,75% → 13,75%.",
            "Curva: mediana de -24 bps.",
        ),
        ressalvas=(
            "Taxa de título não é previsão pura da Selic.",
        ),
        condicoes_de_mudanca=(
            "A mediana da curva voltar ao intervalo estável.",
        ),
        datas_das_fontes=(
            date(2026, 8, 14),
            date(2026, 8, 21),
            date(2026, 8, 19),
            date(2026, 8, 26),
        ),
    )


def test_secao_mostra_veredito_evidencia_e_condicao_de_mudanca():
    pagina = Path(__file__).resolve().parent / "apps" / "convergencia_section.py"
    with patch.object(
        pagina_convergencia,
        "_carregar_leitura",
        return_value=_leitura_publicavel(),
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.header[0].value == "Focus e curva contam a mesma história?"
    assert "A curva ficou mais benigna que o Focus" in [
        item.value for item in app.subheader
    ]
    assert [metrica.label for metrica in app.metric] == [
        "Focus · Selic",
        "Curva geral",
        "Ponta curta",
        "Ponta longa",
    ]
    assert [metrica.value for metrica in app.metric] == [
        "0,00 p.p.",
        "-24 bps",
        "-6,5 bps",
        "-29 bps",
    ]
    subheaders = [item.value for item in app.subheader]
    assert "O que prova" in subheaders
    assert "O que faria mudar" in subheaders
    markdown = " ".join(item.value for item in app.markdown)
    assert "Curva: mediana de -24 bps." in markdown
    assert "voltar ao intervalo estável" in markdown


def test_secao_preserva_estado_insuficiente_sem_inventar_numero():
    leitura = LeituraConvergencia(
        estado=EstadoConvergencia.DADOS_INSUFICIENTES,
        titulo="Ainda não há evidência comparável suficiente",
        resumo="Falta a fotografia D-5 da curva.",
        focus=None,
        curva=None,
        ponta_curta=None,
        ponta_longa=None,
        evidencias=("Falta a fotografia D-5 da curva.",),
        ressalvas=("O motor não completa lacunas.",),
        condicoes_de_mudanca=("Carregar a fotografia D-5.",),
        datas_das_fontes=(),
    )
    pagina = Path(__file__).resolve().parent / "apps" / "convergencia_section.py"
    with patch.object(
        pagina_convergencia,
        "_carregar_leitura",
        return_value=leitura,
    ):
        app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert all(metrica.value == "Sem comparação" for metrica in app.metric)
    assert "Falta a fotografia D-5 da curva." in " ".join(
        item.value for item in app.markdown
    )
