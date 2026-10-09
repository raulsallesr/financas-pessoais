"""Premissas transparentes usadas pelos modelos de valor estimado."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from math import isfinite

import numpy as np

from focuslens.adapters.curva_fontes import ErroCacheCurva, carregar_cache
from focuslens.core.curva_data import PontoCurva

RF_FALLBACK = 0.12
ERP_PADRAO = 0.05
G_PADRAO = 0.04
BAZIN_TAXA_PADRAO = 0.06
GRAHAM_MULT_PADRAO = 22.5
MIN_PARES_SETOR_PADRAO = 6


@dataclass(frozen=True)
class ReferenciaTaxa:
    """Taxa interpolada e a evidência que permite explicá-la na interface."""

    taxa: float
    data_referencia: date | None
    fonte: str
    rf_padrao: bool


@dataclass(frozen=True)
class PremissasValuation:
    """Conjunto imutável de premissas editáveis de uma sessão de cálculo."""

    rf: float = RF_FALLBACK
    erp: float = ERP_PADRAO
    g: float = G_PADRAO
    bazin_taxa: float = BAZIN_TAXA_PADRAO
    graham_mult: float = GRAHAM_MULT_PADRAO
    min_pares_setor: int = MIN_PARES_SETOR_PADRAO
    fonte_rf: str = "Padrão documentado"
    data_curva: date | None = None
    rf_padrao: bool = True

    def __post_init__(self) -> None:
        taxas = (self.rf, self.erp, self.g, self.bazin_taxa)
        if any(not isfinite(valor) or valor < 0 for valor in taxas):
            raise ValueError("Taxas de valuation devem ser finitas e não negativas.")
        if not isfinite(self.graham_mult) or self.graham_mult <= 0:
            raise ValueError("O multiplicador de Graham deve ser positivo.")
        if isinstance(self.min_pares_setor, bool) or self.min_pares_setor < 1:
            raise ValueError("O mínimo de pares do setor deve ser positivo.")

    @property
    def k(self) -> float:
        """Custo do capital próprio, derivado da taxa livre de risco e do ERP."""
        return self.rf + self.erp

    @property
    def fii_taxa_exigida(self) -> float:
        """Equivalência com o Tesouro líquido da alíquota de IR de 15%."""
        return self.rf * (1 - 0.15)


def _fallback() -> ReferenciaTaxa:
    return ReferenciaTaxa(
        taxa=RF_FALLBACK,
        data_referencia=None,
        fonte="Padrão documentado",
        rf_padrao=True,
    )


def taxa_livre_de_risco(
    pontos: Sequence[PontoCurva] | None = None,
    anos_alvo: float = 5,
) -> ReferenciaTaxa:
    """Interpola a curva prefixada mais recente e falha de forma explícita para 12%."""
    if not isfinite(anos_alvo) or anos_alvo <= 0:
        raise ValueError("O prazo-alvo deve ser positivo.")
    try:
        disponiveis = list(carregar_cache() if pontos is None else pontos)
    except (ErroCacheCurva, OSError, TypeError, UnicodeError, ValueError):
        return _fallback()
    if not disponiveis:
        return _fallback()

    data_mais_recente = max(ponto.data_referencia for ponto in disponiveis)
    recentes = [
        ponto
        for ponto in disponiveis
        if ponto.data_referencia == data_mais_recente
        and ponto.vencimento > ponto.data_referencia
        and isfinite(float(ponto.taxa_compra))
    ]
    if not recentes:
        return _fallback()
    recentes.sort(key=lambda ponto: ponto.vencimento)
    prazos = np.array(
        [(ponto.vencimento - data_mais_recente).days / 365.25 for ponto in recentes],
        dtype=float,
    )
    taxas_percentuais = np.array([ponto.taxa_compra for ponto in recentes], dtype=float)
    taxa = float(np.interp(anos_alvo, prazos, taxas_percentuais)) / 100
    return ReferenciaTaxa(
        taxa=taxa,
        data_referencia=data_mais_recente,
        fonte=recentes[0].fonte,
        rf_padrao=False,
    )


def premissas_padrao(
    pontos: Sequence[PontoCurva] | None = None,
    *,
    anos_alvo: float = 5,
) -> PremissasValuation:
    """Monta os padrões documentados usando somente o cache local da curva."""
    referencia = taxa_livre_de_risco(pontos, anos_alvo=anos_alvo)
    return PremissasValuation(
        rf=referencia.taxa,
        fonte_rf=referencia.fonte,
        data_curva=referencia.data_referencia,
        rf_padrao=referencia.rf_padrao,
    )
