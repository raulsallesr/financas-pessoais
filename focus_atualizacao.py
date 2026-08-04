"""Regras puras para atualização e diagnóstico de atualidade do Focus."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class StatusAtualidade:
    rotulo: str
    descricao: str
    cor: str
    icone: str
    dias_uteis: int | None


def dias_uteis_desde(data_coleta: date, hoje: date) -> int:
    """Conta dias úteis após a coleta, sem penalizar sábado e domingo."""
    if data_coleta >= hoje:
        return 0

    cursor = data_coleta + timedelta(days=1)
    total = 0
    while cursor <= hoje:
        if cursor.weekday() < 5:
            total += 1
        cursor += timedelta(days=1)
    return total


def deve_verificar_automaticamente(
    ultima_verificacao: date | None,
    hoje: date,
) -> bool:
    """No máximo uma verificação por dia útil; sem cache, tenta imediatamente."""
    if ultima_verificacao is None:
        return True
    if ultima_verificacao >= hoje:
        return False
    return hoje.weekday() < 5


def avaliar_atualidade(
    data_coleta: date | None,
    hoje: date,
) -> StatusAtualidade:
    if data_coleta is None:
        return StatusAtualidade(
            rotulo="Sem dados salvos",
            descricao="A primeira atualização será feita automaticamente.",
            cor="gray",
            icone="database_off",
            dias_uteis=None,
        )

    dias = dias_uteis_desde(data_coleta, hoje)
    if dias == 0:
        return StatusAtualidade(
            rotulo="Coleta mais recente",
            descricao="Os dados disponíveis são de hoje.",
            cor="green",
            icone="check_circle",
            dias_uteis=0,
        )
    if dias == 1:
        return StatusAtualidade(
            rotulo="Dados recentes",
            descricao="A coleta disponível tem 1 dia útil.",
            cor="green",
            icone="schedule",
            dias_uteis=1,
        )
    if dias <= 5:
        return StatusAtualidade(
            rotulo=f"Há {dias} dias úteis",
            descricao=(
                "O app verifica automaticamente se existe uma coleta mais "
                "recente quando é aberto."
            ),
            cor="blue",
            icone="update",
            dias_uteis=dias,
        )
    return StatusAtualidade(
        rotulo="Pode estar desatualizado",
        descricao=(
            f"A última coleta disponível tem {dias} dias úteis. "
            "A verificação automática pode estar sem acesso ao BACEN."
        ),
        cor="orange",
        icone="warning",
        dias_uteis=dias,
    )
