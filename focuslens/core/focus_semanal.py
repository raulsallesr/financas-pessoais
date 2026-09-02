"""Motor puro do Focus Semanal: relevância, ranking e estado da leitura.

Recebe comparativos já calculados e não faz I/O, não acessa Streamlit e não
produz recomendação. A relevância é o delta absoluto dividido pelo limiar de
estabilidade do próprio indicador, permitindo comparar unidades diferentes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from focuslens.core.financas_taxonomia import Direcao
from focuslens.core.focus_atualizacao import dias_uteis_desde
from focuslens.core.focus_data import ComparativoIndicador
from focuslens.core.motor_indicadores import limiar_estavel


INDICADORES_FOCUS_SEMANAL = (
    "Selic",
    "IPCA",
    "Câmbio",
    "PIB Total",
)
LIMITE_DEFASAGEM_DIAS_UTEIS = 5


class EstadoFocusSemanal(str, Enum):
    ATUALIZADO = "Atualizado"
    DEFASADO = "Defasado"
    INDISPONIVEL = "Indisponível"
    SEM_MUDANCA_RELEVANTE = "Sem mudança relevante"


@dataclass(frozen=True)
class ResumoFocusSemanal:
    estado: EstadoFocusSemanal
    destaques: tuple[ComparativoIndicador, ...]
    total_acompanhados: int
    total_comparaveis: int
    total_relevantes: int
    data_mais_recente: date | None
    dias_uteis: int | None


def calcular_relevancia(comparativo: ComparativoIndicador) -> float:
    """Mede quantos limiares de estabilidade cabem no delta observado."""
    if comparativo.anterior is None:
        return 0.0
    limiar = max(limiar_estavel(comparativo.atual.indicador), 0.0001)
    return round(abs(comparativo.delta) / limiar, 6)


def ordenar_por_relevancia(
    comparativos: list[ComparativoIndicador],
) -> list[ComparativoIndicador]:
    """Ordena somente os quatro indicadores comparáveis da Etapa 1."""
    ordem = {
        indicador: indice
        for indice, indicador in enumerate(INDICADORES_FOCUS_SEMANAL)
    }
    acompanhados = [
        comparativo
        for comparativo in comparativos
        if comparativo.atual.indicador in ordem
        and comparativo.anterior is not None
    ]
    return sorted(
        acompanhados,
        key=lambda comparativo: (
            -calcular_relevancia(comparativo),
            ordem[comparativo.atual.indicador],
        ),
    )


def montar_resumo_semanal(
    comparativos: list[ComparativoIndicador],
    hoje: date,
) -> ResumoFocusSemanal:
    """Consolida a fotografia semanal e escolhe até três destaques."""
    ordem = {
        indicador: indice
        for indice, indicador in enumerate(INDICADORES_FOCUS_SEMANAL)
    }
    acompanhados = sorted(
        (
            comparativo
            for comparativo in comparativos
            if comparativo.atual.indicador in ordem
        ),
        key=lambda comparativo: ordem[comparativo.atual.indicador],
    )
    if not acompanhados:
        return ResumoFocusSemanal(
            estado=EstadoFocusSemanal.INDISPONIVEL,
            destaques=(),
            total_acompanhados=0,
            total_comparaveis=0,
            total_relevantes=0,
            data_mais_recente=None,
            dias_uteis=None,
        )

    ranking = ordenar_por_relevancia(acompanhados)
    relevantes = [
        comparativo
        for comparativo in ranking
        if comparativo.direcao != Direcao.ESTAVEL
    ]
    data_mais_recente = max(
        comparativo.atual.data_coleta for comparativo in acompanhados
    )
    dias_uteis = dias_uteis_desde(data_mais_recente, hoje)

    if dias_uteis > LIMITE_DEFASAGEM_DIAS_UTEIS:
        estado = EstadoFocusSemanal.DEFASADO
    elif ranking and not relevantes:
        estado = EstadoFocusSemanal.SEM_MUDANCA_RELEVANTE
    else:
        estado = EstadoFocusSemanal.ATUALIZADO

    destaques = tuple((ranking or acompanhados)[:3])
    return ResumoFocusSemanal(
        estado=estado,
        destaques=destaques,
        total_acompanhados=len(acompanhados),
        total_comparaveis=len(ranking),
        total_relevantes=len(relevantes),
        data_mais_recente=data_mais_recente,
        dias_uteis=dias_uteis,
    )
