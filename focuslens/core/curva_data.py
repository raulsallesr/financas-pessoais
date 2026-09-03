"""Tipos e transformações puras dos pontos da Curva Tesouro."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite

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

    def __post_init__(self) -> None:
        if not isinstance(self.data_referencia, date):
            raise ValueError("data_referencia deve ser uma data.")
        if not isinstance(self.vencimento, date):
            raise ValueError("vencimento deve ser uma data.")
        if self.vencimento <= self.data_referencia:
            raise ValueError("vencimento deve ser posterior à data-base.")
        if not isinstance(self.tipo_titulo, str) or not self.tipo_titulo.strip():
            raise ValueError("tipo_titulo deve ser informado.")
        if not isinstance(self.fonte, str) or not self.fonte.strip():
            raise ValueError("fonte deve ser informada.")
        for campo, valor, obrigatorio in (
            ("taxa_compra", self.taxa_compra, True),
            ("taxa_venda", self.taxa_venda, False),
            ("pu_compra", self.pu_compra, False),
            ("pu_venda", self.pu_venda, False),
        ):
            if valor is None and not obrigatorio:
                continue
            if (
                valor is None
                or isinstance(valor, bool)
                or not isinstance(valor, (int, float))
                or not isfinite(float(valor))
            ):
                raise ValueError(f"{campo} deve ser um número finito.")


def consolidar_pontos_curva(
    pontos: list[PontoCurva],
) -> tuple[PontoCurva, ...]:
    """Remove duplicatas idênticas e rejeita versões conflitantes."""
    unicos: dict[tuple[date, str, date], PontoCurva] = {}
    for ponto in pontos:
        chave = (
            ponto.data_referencia,
            ponto.tipo_titulo,
            ponto.vencimento,
        )
        existente = unicos.get(chave)
        if existente is not None and existente != ponto:
            raise ValueError(
                "Existem pontos conflitantes para a mesma data e título."
            )
        unicos[chave] = ponto
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
