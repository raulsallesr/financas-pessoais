"""Motor puro da leitura D-5/D-21 da curva prefixada observada."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from statistics import median

from focuslens.core.curva_data import PontoCurva, consolidar_pontos_curva
from focuslens.core.focus_atualizacao import dias_uteis_desde


LIMIAR_MOVIMENTO_BPS = 2.0
LIMITE_DEFASAGEM_DIAS_UTEIS = 2


class EstadoCurva(str, Enum):
    ATUALIZADA = "Atualizada"
    DEFASADA = "Defasada"
    PARCIAL = "Histórico parcial"
    INDISPONIVEL = "Indisponível"


@dataclass(frozen=True)
class FotografiaCurva:
    data_referencia: date
    pontos: tuple[PontoCurva, ...]


@dataclass(frozen=True)
class ComparacaoPontoCurva:
    atual: PontoCurva
    d5: PontoCurva | None
    d21: PontoCurva | None
    delta_d5_bps: float | None
    delta_d21_bps: float | None


@dataclass(frozen=True)
class LeituraCurva:
    estado: EstadoCurva
    atual: FotografiaCurva | None
    d5: FotografiaCurva | None
    d21: FotografiaCurva | None
    comparacoes: tuple[ComparacaoPontoCurva, ...]
    movimento_mediano_d5_bps: float | None
    inclinacao_atual_bps: float | None
    dias_uteis: int | None


def _fotografia(
    por_data: dict[date, tuple[PontoCurva, ...]],
    data_referencia: date | None,
) -> FotografiaCurva | None:
    if data_referencia is None:
        return None
    return FotografiaCurva(
        data_referencia=data_referencia,
        pontos=por_data[data_referencia],
    )


def _delta_bps(atual: float, anterior: float | None) -> float | None:
    if anterior is None:
        return None
    return round((atual - anterior) * 100, 1)


def montar_leitura_curva(
    pontos: list[PontoCurva] | tuple[PontoCurva, ...],
    hoje: date,
) -> LeituraCurva:
    consolidados = consolidar_pontos_curva(list(pontos))
    if not consolidados:
        return LeituraCurva(
            estado=EstadoCurva.INDISPONIVEL,
            atual=None,
            d5=None,
            d21=None,
            comparacoes=(),
            movimento_mediano_d5_bps=None,
            inclinacao_atual_bps=None,
            dias_uteis=None,
        )

    datas = sorted({ponto.data_referencia for ponto in consolidados})
    por_data = {
        data_ref: tuple(
            sorted(
                (
                    ponto
                    for ponto in consolidados
                    if ponto.data_referencia == data_ref
                ),
                key=lambda ponto: ponto.vencimento,
            )
        )
        for data_ref in datas
    }
    atual = _fotografia(por_data, datas[-1])
    d5 = _fotografia(por_data, datas[-6] if len(datas) >= 6 else None)
    d21 = _fotografia(
        por_data,
        datas[-22] if len(datas) >= 22 else None,
    )
    mapa_d5 = {ponto.vencimento: ponto for ponto in d5.pontos} if d5 else {}
    mapa_d21 = (
        {ponto.vencimento: ponto for ponto in d21.pontos}
        if d21
        else {}
    )
    comparacoes = tuple(
        ComparacaoPontoCurva(
            atual=ponto,
            d5=mapa_d5.get(ponto.vencimento),
            d21=mapa_d21.get(ponto.vencimento),
            delta_d5_bps=_delta_bps(
                ponto.taxa_compra,
                (
                    mapa_d5[ponto.vencimento].taxa_compra
                    if ponto.vencimento in mapa_d5
                    else None
                ),
            ),
            delta_d21_bps=_delta_bps(
                ponto.taxa_compra,
                (
                    mapa_d21[ponto.vencimento].taxa_compra
                    if ponto.vencimento in mapa_d21
                    else None
                ),
            ),
        )
        for ponto in atual.pontos
    )
    deltas_d5 = [
        comparacao.delta_d5_bps
        for comparacao in comparacoes
        if comparacao.delta_d5_bps is not None
    ]
    movimento = (
        round(float(median(deltas_d5)), 1) if deltas_d5 else None
    )
    inclinacao = (
        round(
            (
                atual.pontos[-1].taxa_compra
                - atual.pontos[0].taxa_compra
            )
            * 100,
            1,
        )
        if len(atual.pontos) >= 2
        else None
    )
    dias_uteis = dias_uteis_desde(atual.data_referencia, hoje)
    if dias_uteis > LIMITE_DEFASAGEM_DIAS_UTEIS:
        estado = EstadoCurva.DEFASADA
    elif d5 is None or d21 is None or len(atual.pontos) < 2:
        estado = EstadoCurva.PARCIAL
    else:
        estado = EstadoCurva.ATUALIZADA
    return LeituraCurva(
        estado=estado,
        atual=atual,
        d5=d5,
        d21=d21,
        comparacoes=comparacoes,
        movimento_mediano_d5_bps=movimento,
        inclinacao_atual_bps=inclinacao,
        dias_uteis=dias_uteis,
    )


def titulo_leitura_curva(leitura: LeituraCurva) -> str:
    if leitura.estado == EstadoCurva.INDISPONIVEL:
        return "Curva prefixada indisponível no momento"
    if leitura.estado == EstadoCurva.DEFASADA:
        return "A última curva disponível está defasada"
    if leitura.estado == EstadoCurva.PARCIAL:
        return "Curva atual disponível; histórico ainda parcial"
    movimento = leitura.movimento_mediano_d5_bps
    if movimento is None:
        return "Histórico insuficiente para comparar a curva"
    altas = sum(
        comparacao.delta_d5_bps is not None
        and comparacao.delta_d5_bps > LIMIAR_MOVIMENTO_BPS
        for comparacao in leitura.comparacoes
    )
    quedas = sum(
        comparacao.delta_d5_bps is not None
        and comparacao.delta_d5_bps < -LIMIAR_MOVIMENTO_BPS
        for comparacao in leitura.comparacoes
    )
    if altas and quedas and abs(movimento) <= LIMIAR_MOVIMENTO_BPS:
        return "A curva prefixada teve movimentos mistos"
    if movimento > LIMIAR_MOVIMENTO_BPS:
        return "Taxas prefixadas subiram frente a D-5"
    if movimento < -LIMIAR_MOVIMENTO_BPS:
        return "Taxas prefixadas caíram frente a D-5"
    return "Curva prefixada ficou praticamente estável"


def descricao_leitura_curva(leitura: LeituraCurva) -> str:
    if leitura.estado == EstadoCurva.INDISPONIVEL:
        return (
            "Ainda não há uma fotografia íntegra salva. A atualização usa "
            "o CSV público do Tesouro Transparente."
        )
    if leitura.estado == EstadoCurva.DEFASADA:
        data_ref = leitura.atual.data_referencia.strftime("%d/%m/%Y")
        return (
            f"A fotografia é de {data_ref} e tem "
            f"{leitura.dias_uteis} dias úteis. Os pontos continuam "
            "visíveis, mas não representam a curva atual."
        )
    if leitura.estado == EstadoCurva.PARCIAL:
        return (
            "A taxa atual está disponível, mas ainda faltam observações "
            "comparáveis para completar D-5 e D-21."
        )
    deltas = [
        comparacao.delta_d5_bps
        for comparacao in leitura.comparacoes
        if comparacao.delta_d5_bps is not None
    ]
    altas = sum(delta > LIMIAR_MOVIMENTO_BPS for delta in deltas)
    quedas = sum(delta < -LIMIAR_MOVIMENTO_BPS for delta in deltas)
    estaveis = len(deltas) - altas - quedas
    movimento = leitura.movimento_mediano_d5_bps
    movimento_texto = f"{movimento:+.1f}".replace(".", ",")
    estabilidade = (
        "1 ficou estável"
        if estaveis == 1
        else f"{estaveis} ficaram estáveis"
    )
    return (
        f"A variação mediana foi de {movimento_texto} bps em "
        f"{len(deltas)} vencimentos comparáveis: {altas} subiram, "
        f"{quedas} caíram e {estabilidade}."
    )
