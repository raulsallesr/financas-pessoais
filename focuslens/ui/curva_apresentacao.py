"""Transformações puras de apresentação para a Curva Tesouro."""

from __future__ import annotations

from focuslens.core.curva_cenarios import CenarioCurva
from focuslens.core.curva_modelo import FotografiaCurva, LeituraCurva


CORES_PERIODOS = ("#0F766E", "#A16207", "#64748B")
TRACOS_PERIODOS = ((), (7, 4), (2, 4))


def formatar_numero(valor: float, casas: int = 2) -> str:
    return (
        f"{valor:,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_bps(valor: float | None) -> str:
    if valor is None:
        return "Sem comparação"
    if float(valor).is_integer():
        return f"{valor:+.0f} bps"
    return f"{valor:+.1f} bps".replace(".", ",")


def _fotografias_rotuladas(
    leitura: LeituraCurva,
) -> tuple[tuple[str, FotografiaCurva], ...]:
    fotografias: list[tuple[str, FotografiaCurva]] = []
    if leitura.atual is not None:
        fotografias.append(
            (
                f"Atual · {leitura.atual.data_referencia:%d/%m}",
                leitura.atual,
            )
        )
    if leitura.d5 is not None:
        fotografias.append(
            (f"D-5 · {leitura.d5.data_referencia:%d/%m}", leitura.d5)
        )
    if leitura.d21 is not None:
        fotografias.append(
            (f"D-21 · {leitura.d21.data_referencia:%d/%m}", leitura.d21)
        )
    return tuple(fotografias)


def linhas_grafico(leitura: LeituraCurva) -> list[dict[str, object]]:
    return [
        {
            "Vencimento": ponto.vencimento.strftime("%d/%m/%Y"),
            "Taxa": ponto.taxa_compra,
            "Período": rotulo,
            "Data da curva": fotografia.data_referencia,
        }
        for rotulo, fotografia in _fotografias_rotuladas(leitura)
        for ponto in fotografia.pontos
    ]


def especificacao_grafico(
    linhas: list[dict[str, object]],
) -> dict[str, object]:
    periodos = list(
        dict.fromkeys(str(linha["Período"]) for linha in linhas)
    )
    cores = list(CORES_PERIODOS[: len(periodos)])
    tracos = [list(traco) for traco in TRACOS_PERIODOS[: len(periodos)]]
    return {
        "mark": {
            "type": "line",
            "point": {"filled": True, "size": 65},
            "strokeWidth": 2.5,
        },
        "encoding": {
            "x": {
                "field": "Vencimento",
                "type": "ordinal",
                "sort": None,
                "axis": {"title": "Vencimento", "labelAngle": 0},
            },
            "y": {
                "field": "Taxa",
                "type": "quantitative",
                "scale": {"zero": False},
                "axis": {"title": "Taxa de compra (% a.a.)"},
            },
            "color": {
                "field": "Período",
                "type": "nominal",
                "scale": {"domain": periodos, "range": cores},
                "legend": {"title": None, "orient": "top"},
            },
            "strokeDash": {
                "field": "Período",
                "type": "nominal",
                "scale": {"domain": periodos, "range": tracos},
                "legend": None,
            },
            "tooltip": [
                {"field": "Período", "type": "nominal"},
                {"field": "Vencimento", "type": "ordinal"},
                {
                    "field": "Taxa",
                    "type": "quantitative",
                    "format": ".2f",
                    "title": "Taxa (% a.a.)",
                },
            ],
        },
        "height": 360,
    }


def linhas_tabela(leitura: LeituraCurva) -> list[dict[str, object]]:
    return [
        {
            "Vencimento": item.atual.vencimento,
            "Atual (% a.a.)": item.atual.taxa_compra,
            "D-5 (% a.a.)": item.d5.taxa_compra if item.d5 else None,
            "Δ D-5 (bps)": item.delta_d5_bps,
            "D-21 (% a.a.)": item.d21.taxa_compra if item.d21 else None,
            "Δ D-21 (bps)": item.delta_d21_bps,
        }
        for item in leitura.comparacoes
    ]


def linhas_grafico_cenario(
    cenario: CenarioCurva,
) -> list[dict[str, object]]:
    rotulo_observado = f"Observada · {cenario.data_base:%d/%m}"
    rotulo_cenario = f"Cenário · {formatar_bps(cenario.choque_bps)}"
    return [
        {
            "Vencimento": ponto.vencimento.strftime("%d/%m/%Y"),
            "Taxa": taxa,
            "Curva": rotulo,
        }
        for ponto in cenario.pontos
        for rotulo, taxa in (
            (rotulo_observado, ponto.taxa_observada),
            (rotulo_cenario, ponto.taxa_cenario),
        )
    ]


def especificacao_grafico_cenario(
    linhas: list[dict[str, object]],
) -> dict[str, object]:
    curvas = list(dict.fromkeys(str(linha["Curva"]) for linha in linhas))
    return {
        "mark": {
            "type": "line",
            "point": {"filled": True, "size": 70},
            "strokeWidth": 2.7,
        },
        "encoding": {
            "x": {
                "field": "Vencimento",
                "type": "ordinal",
                "sort": None,
                "axis": {"title": "Vencimento", "labelAngle": 0},
            },
            "y": {
                "field": "Taxa",
                "type": "quantitative",
                "scale": {"zero": False},
                "axis": {"title": "Taxa (% a.a.)"},
            },
            "color": {
                "field": "Curva",
                "type": "nominal",
                "scale": {
                    "domain": curvas,
                    "range": [CORES_PERIODOS[0], CORES_PERIODOS[1]],
                },
                "legend": {"title": None, "orient": "top"},
            },
            "strokeDash": {
                "field": "Curva",
                "type": "nominal",
                "scale": {"domain": curvas, "range": [[], [7, 4]]},
                "legend": None,
            },
            "tooltip": [
                {"field": "Curva", "type": "nominal"},
                {"field": "Vencimento", "type": "ordinal"},
                {
                    "field": "Taxa",
                    "type": "quantitative",
                    "format": ".2f",
                    "title": "Taxa (% a.a.)",
                },
            ],
        },
        "height": 320,
    }


def linhas_tabela_cenario(
    cenario: CenarioCurva,
) -> list[dict[str, object]]:
    return [
        {
            "Vencimento": ponto.vencimento,
            "Observada (% a.a.)": ponto.taxa_observada,
            "Cenário (% a.a.)": ponto.taxa_cenario,
            "Choque (bps)": cenario.choque_bps,
        }
        for ponto in cenario.pontos
    ]
