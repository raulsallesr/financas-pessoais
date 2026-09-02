"""Entrypoint mínimo usado pelo AppTest do Resumo integrado."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from focuslens.core.resumo_integrado import (
    DatasFonteResumo,
    PrioridadeResumo,
    ProvaResumo,
    ResumoIntegrado,
)
from focuslens.core.macro_modelo import CenarioMacro, SinalMacro
from focuslens.ui.pagina_resumo import render_secao, renderizar_contexto_radar


render_secao(
    ResumoIntegrado(
        prioridade=PrioridadeResumo.FOCUS_CURVA,
        veredito="A curva ficou mais benigna que o Focus",
        provas=(
            ProvaResumo("Focus × Curva", "Focus: 13,75% → 13,75%."),
            ProvaResumo("Focus × Curva", "Curva: mediana de -24 bps."),
        ),
        datas_fontes=(
            DatasFonteResumo(
                "BACEN · Focus",
                (date(2026, 8, 14), date(2026, 8, 21)),
            ),
            DatasFonteResumo(
                "Tesouro Transparente",
                (date(2026, 8, 19), date(2026, 8, 26)),
            ),
        ),
        limites=("Taxa de título não é previsão pura da Selic.",),
        condicoes_de_mudanca=(
            "A mediana da curva voltar ao intervalo estável.",
        ),
    )
)
renderizar_contexto_radar(
    CenarioMacro(
        titulo="Cenário misto",
        horizonte="próximas 4–12 semanas",
        confianca="moderada",
        resumo="Sinais condicionais.",
        projecoes=(),
        eixos=(),
        perspectivas=(),
        invalidadores=(),
        temas_editoriais=(),
        sinais=(
            SinalMacro(
                eixo="externo",
                impacto=-2,
                titulo="Dólar ganhou força no período",
                evidencia="A PTAX avançou frente à observação anterior.",
                fonte="PTAX / BACEN",
            ),
        ),
    )
)
