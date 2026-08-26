import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from convergencia_apresentacao import (
    detalhe_curva,
    detalhe_focus,
    detalhe_ponta,
    valor_curva,
    valor_focus,
    valor_ponta,
)
from convergencia_modelo import (
    DirecaoSinal,
    SinalCurva,
    SinalFocus,
    SinalPonta,
)


def test_formata_metricas_sem_depender_do_streamlit():
    focus = SinalFocus(
        referencia="R6/2026",
        data_anterior=date(2026, 8, 14),
        data_atual=date(2026, 8, 21),
        valor_anterior=13.50,
        valor_atual=13.75,
        delta_pp=0.25,
        direcao=DirecaoSinal.PRESSIONADA,
    )
    curva = SinalCurva(
        data_anterior=date(2026, 8, 19),
        data_atual=date(2026, 8, 26),
        delta_mediano_bps=-24.0,
        vencimentos_comparaveis=5,
        direcao=DirecaoSinal.BENIGNA,
    )
    ponta = SinalPonta(
        nome="Ponta curta",
        delta_mediano_bps=-6.5,
        vencimentos=(date(2027, 1, 1), date(2028, 1, 1)),
        direcao=DirecaoSinal.BENIGNA,
    )

    assert valor_focus(focus) == "+0,25 p.p."
    assert detalhe_focus(focus) == "Pressionada · R6/2026"
    assert valor_curva(curva) == "-24 bps"
    assert detalhe_curva(curva) == "Benigna · 5 venc."
    assert valor_ponta(ponta) == "-6,5 bps"
    assert detalhe_ponta(ponta) == "Benigna · 2027–2028"


def test_formata_ausencia_sem_inventar_zero():
    assert valor_focus(None) == "Sem comparação"
    assert valor_curva(None) == "Sem comparação"
    assert valor_ponta(None) == "Sem comparação"
    assert "mesma reunião" in detalhe_focus(None)
    assert "2 vencimentos" in detalhe_curva(None)
    assert "4+ vencimentos" in detalhe_ponta(None)
