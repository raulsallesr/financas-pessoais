"""Motor puro: dataclasses e cálculo de comparação semana-a-semana.

Sem I/O -- só recebe leituras já carregadas (de focus_leitura.py) e calcula
deltas/tendências. Isso permite testar toda a lógica de comparação sem rede.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from financas_taxonomia import Direcao
from motor_indicadores import classificar_direcao


@dataclass(frozen=True)
class LeituraIndicador:
    indicador: str
    referencia: str  # ex.: "R5/2026" (Selic) ou "2026" (IPCA/Câmbio anual)
    data_coleta: date
    mediana: float
    media: float
    minimo: float
    maximo: float
    desvio_padrao: float
    num_respondentes: int


@dataclass(frozen=True)
class ComparativoIndicador:
    atual: LeituraIndicador
    anterior: LeituraIndicador | None
    delta: float
    direcao: Direcao


def calcular_delta(atual: LeituraIndicador, anterior: LeituraIndicador | None) -> float:
    if anterior is None:
        return 0.0
    return round(atual.mediana - anterior.mediana, 4)


def comparar(atual: LeituraIndicador, anterior: LeituraIndicador | None) -> ComparativoIndicador:
    delta = calcular_delta(atual, anterior)
    direcao = classificar_direcao(delta) if anterior is not None else Direcao.ESTAVEL
    return ComparativoIndicador(atual=atual, anterior=anterior, delta=delta, direcao=direcao)


def leitura_mais_recente(historico: list[LeituraIndicador]) -> LeituraIndicador | None:
    if not historico:
        return None
    return max(historico, key=lambda leitura: leitura.data_coleta)


def leitura_anterior(
    historico: list[LeituraIndicador], referencia_atual: LeituraIndicador
) -> LeituraIndicador | None:
    """Leitura mais recente do mesmo indicador+referência, coletada antes da atual."""
    candidatos = [
        leitura
        for leitura in historico
        if leitura.indicador == referencia_atual.indicador
        and leitura.referencia == referencia_atual.referencia
        and leitura.data_coleta < referencia_atual.data_coleta
    ]
    if not candidatos:
        return None
    return max(candidatos, key=lambda leitura: leitura.data_coleta)


def serie_historica(historico: list[LeituraIndicador], indicador: str) -> list[LeituraIndicador]:
    """Todas as leituras de um indicador, ordenadas por data de coleta (para gráfico de tendência).

    Não filtra por `referencia`: para a Selic, a "próxima reunião do Copom"
    muda com o tempo, então a série mostra a leitura mais próxima disponível
    em cada semana, não uma única reunião fixa do início ao fim.
    """
    leituras = [leitura for leitura in historico if leitura.indicador == indicador]
    return sorted(leituras, key=lambda leitura: leitura.data_coleta)
