"""Cenários mecânicos e puros sobre a fotografia atual da curva."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite

from focuslens.core.curva_modelo import FotografiaCurva


LIMITE_ABSOLUTO_CHOQUE_BPS = 200.0
LIMITES_CENARIO_PARALELO = (
    "É uma hipótese mecânica, não uma previsão nem uma probabilidade.",
    "Não calcula preço, retorno, duration, impostos ou custos dos títulos.",
    "Todos os vencimentos recebem o mesmo choque; mudanças de inclinação "
    "ficam fora deste cenário.",
)


@dataclass(frozen=True)
class PontoCenarioCurva:
    vencimento: date
    taxa_observada: float
    taxa_cenario: float


@dataclass(frozen=True)
class CenarioCurva:
    data_base: date
    choque_bps: float
    pontos: tuple[PontoCenarioCurva, ...]
    inclinacao_observada_bps: float | None
    inclinacao_cenario_bps: float | None
    titulo: str
    resumo: str
    limites: tuple[str, ...] = LIMITES_CENARIO_PARALELO


def _formatar_numero(valor: float, casas: int = 2) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def _formatar_bps(valor: float) -> str:
    if valor == 0:
        return "0 bps"
    casas = 0 if valor.is_integer() else 1
    return f"{valor:+.{casas}f} bps".replace(".", ",")


def _inclinacao_bps(taxas: tuple[float, ...]) -> float | None:
    if len(taxas) < 2:
        return None
    return round((taxas[-1] - taxas[0]) * 100, 1)


def _resumo(
    choque_bps: float,
    total_pontos: int,
    inclinacao_bps: float | None,
) -> str:
    deslocamento_pp = _formatar_numero(abs(choque_bps) / 100)
    if choque_bps > 0:
        movimento = f"sobem {deslocamento_pp} p.p."
    elif choque_bps < 0:
        movimento = f"caem {deslocamento_pp} p.p."
    else:
        movimento = "permanecem no nível observado"
    texto = (
        f"As taxas {movimento} nos {total_pontos} vencimentos observados."
    )
    if inclinacao_bps is None:
        return texto + " Há somente um ponto; não existe inclinação para comparar."
    return (
        texto
        + " A inclinação permanece em "
        + _formatar_bps(inclinacao_bps)
        + " porque o deslocamento é igual em todos os vencimentos."
    )


def simular_choque_paralelo(
    fotografia: FotografiaCurva,
    choque_bps: float,
) -> CenarioCurva:
    """Aplica o mesmo deslocamento a cada taxa sem alterar a fotografia."""
    if (
        isinstance(choque_bps, bool)
        or not isinstance(choque_bps, (int, float))
        or not isfinite(float(choque_bps))
    ):
        raise ValueError("choque_bps deve ser um número finito.")
    choque = float(choque_bps)
    if abs(choque) > LIMITE_ABSOLUTO_CHOQUE_BPS:
        raise ValueError(
            "choque_bps deve ficar entre -200 e +200 pontos-base."
        )
    if not fotografia.pontos:
        raise ValueError("A fotografia precisa ter ao menos um ponto.")
    if any(
        ponto.data_referencia != fotografia.data_referencia
        for ponto in fotografia.pontos
    ):
        raise ValueError("Todos os pontos devem pertencer à data-base.")

    pontos_observados = tuple(
        sorted(fotografia.pontos, key=lambda ponto: ponto.vencimento)
    )
    pontos = tuple(
        PontoCenarioCurva(
            vencimento=ponto.vencimento,
            taxa_observada=ponto.taxa_compra,
            taxa_cenario=round(ponto.taxa_compra + choque / 100, 6),
        )
        for ponto in pontos_observados
    )
    inclinacao_observada = _inclinacao_bps(
        tuple(ponto.taxa_observada for ponto in pontos)
    )
    inclinacao_cenario = _inclinacao_bps(
        tuple(ponto.taxa_cenario for ponto in pontos)
    )
    return CenarioCurva(
        data_base=fotografia.data_referencia,
        choque_bps=choque,
        pontos=pontos,
        inclinacao_observada_bps=inclinacao_observada,
        inclinacao_cenario_bps=inclinacao_cenario,
        titulo=f"Choque paralelo de {_formatar_bps(choque)}",
        resumo=_resumo(choque, len(pontos), inclinacao_cenario),
    )
