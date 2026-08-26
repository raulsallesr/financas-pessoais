"""Tipos e transformações puras dos pontos da Curva Tesouro."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


TIPO_PREFIXADO_SEM_CUPOM = "Tesouro Prefixado"


@dataclass(frozen=True)
class PontoCurva:
    data_referencia: date
    tipo_titulo: str
    vencimento: date
    taxa_compra: float
    taxa_venda: float | None
    pu_compra: float | None
    pu_venda: float | None
    fonte: str


def consolidar_pontos_curva(
    pontos: list[PontoCurva],
) -> tuple[PontoCurva, ...]:
    """Remove duplicatas por fotografia+título e ordena o histórico."""
    unicos = {
        (
            ponto.data_referencia,
            ponto.tipo_titulo,
            ponto.vencimento,
        ): ponto
        for ponto in pontos
    }
    return tuple(
        unicos[chave]
        for chave in sorted(unicos)
    )


def manter_datas_recentes(
    pontos: list[PontoCurva],
    *,
    max_datas: int,
) -> tuple[PontoCurva, ...]:
    if max_datas < 1:
        raise ValueError("max_datas deve ser positivo.")
    consolidados = consolidar_pontos_curva(pontos)
    datas = sorted({ponto.data_referencia for ponto in consolidados})
    permitidas = set(datas[-max_datas:])
    return tuple(
        ponto
        for ponto in consolidados
        if ponto.data_referencia in permitidas
    )
