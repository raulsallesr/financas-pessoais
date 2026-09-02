"""Tipos e cálculos puros para séries de preços e índices de mercado."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class PontoMercado:
    data: date
    valor: float


@dataclass(frozen=True)
class SerieMercado:
    codigo: str
    nome: str
    unidade: str
    fonte: str
    fonte_url: str
    pontos: tuple[PontoMercado, ...]


@dataclass(frozen=True)
class MovimentoMercado:
    codigo: str
    nome: str
    unidade: str
    valor_atual: float
    data_atual: date
    variacao_30d: float | None
    direcao: str


def consolidar_pontos(
    pontos: list[PontoMercado],
) -> tuple[PontoMercado, ...]:
    """Mantém o último valor recebido para cada data e ordena a série."""
    por_data = {ponto.data: ponto for ponto in pontos}
    return tuple(por_data[data_ponto] for data_ponto in sorted(por_data))


def valor_em_ou_antes(
    serie: SerieMercado,
    data_limite: date,
) -> PontoMercado | None:
    candidatos = [
        ponto for ponto in serie.pontos if ponto.data <= data_limite
    ]
    return candidatos[-1] if candidatos else None


def calcular_movimento(
    serie: SerieMercado,
    *,
    janela_dias: int = 30,
    limiar_lateral: float | None = None,
) -> MovimentoMercado:
    if not serie.pontos:
        raise ValueError("A série precisa ter ao menos um ponto.")
    atual = serie.pontos[-1]
    anterior = valor_em_ou_antes(
        serie,
        atual.data - timedelta(days=janela_dias),
    )
    variacao = None
    if anterior is not None and anterior.valor:
        variacao = round(
            ((atual.valor / anterior.valor) - 1) * 100,
            2,
        )

    limiares = {"USDBRL": 2.0, "BRENT": 5.0, "BTCBRL": 10.0}
    limiar = (
        limiar_lateral
        if limiar_lateral is not None
        else limiares.get(serie.codigo, 3.0)
    )
    if variacao is None or abs(variacao) < limiar:
        direcao = "lateral"
    elif variacao > 0:
        direcao = "alta"
    else:
        direcao = "queda"
    return MovimentoMercado(
        codigo=serie.codigo,
        nome=serie.nome,
        unidade=serie.unidade,
        valor_atual=atual.valor,
        data_atual=atual.data,
        variacao_30d=variacao,
        direcao=direcao,
    )


def pontos_base_100(
    serie: SerieMercado,
) -> tuple[PontoMercado, ...]:
    if not serie.pontos or serie.pontos[0].valor == 0:
        return ()
    base = serie.pontos[0].valor
    return tuple(
        PontoMercado(
            data=ponto.data,
            valor=round((ponto.valor / base) * 100, 4),
        )
        for ponto in serie.pontos
    )


def acumular_taxas_diarias(
    pontos: list[PontoMercado],
) -> tuple[PontoMercado, ...]:
    """Transforma taxas percentuais diárias em um índice acumulado base 100.

    O primeiro dia útil é a base comum, como ocorre com o primeiro preço das
    demais séries. Cada taxa posterior é composta sobre o índice anterior.
    """
    ordenados = consolidar_pontos(pontos)
    if not ordenados:
        return ()

    indice = 100.0
    acumulados = [PontoMercado(data=ordenados[0].data, valor=indice)]
    for ponto in ordenados[1:]:
        indice *= 1 + (ponto.valor / 100)
        acumulados.append(
            PontoMercado(data=ponto.data, valor=round(indice, 6))
        )
    return tuple(acumulados)
