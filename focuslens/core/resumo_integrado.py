"""Orquestração pura do Resumo do FocusLens BR.

O módulo recebe somente os contratos já calculados por Focus, Curva e
Convergência. Ele escolhe qual leitura deve liderar o Resumo e reduz a
evidência a duas–quatro provas, sem refazer fórmulas, acessar I/O ou conhecer
Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from focuslens.core.convergencia_modelo import EstadoConvergencia, LeituraConvergencia
from focuslens.ui.curva_apresentacao import formatar_bps
from focuslens.core.curva_modelo import (
    EstadoCurva,
    LeituraCurva,
    descricao_leitura_curva,
    titulo_leitura_curva,
)
from focuslens.ui.focus_apresentacao import (
    descricao_resumo_semanal,
    formatar_delta,
    formatar_valor,
    titulo_resumo_semanal,
)
from focuslens.core.focus_semanal import EstadoFocusSemanal, ResumoFocusSemanal
from focuslens.core.macro_modelo import CenarioMacro


FONTE_FOCUS = "BACEN · Focus"
FONTE_CURVA = "Tesouro Transparente"
FONTE_FOCUS_RADAR = "Boletim Focus / BACEN"


class PrioridadeResumo(str, Enum):
    """Assunto que merece abrir a leitura, sem indicar ação financeira."""

    FOCUS_CURVA = "Focus × Curva"
    EXPECTATIVAS = "Expectativas"
    CURVA = "Curva"
    QUALIDADE_DOS_DADOS = "Qualidade dos dados"


@dataclass(frozen=True)
class ProvaResumo:
    origem: str
    descricao: str


@dataclass(frozen=True)
class DatasFonteResumo:
    fonte: str
    datas: tuple[date, ...]


@dataclass(frozen=True)
class ResumoIntegrado:
    prioridade: PrioridadeResumo
    veredito: str
    provas: tuple[ProvaResumo, ...]
    datas_fontes: tuple[DatasFonteResumo, ...]
    limites: tuple[str, ...]
    condicoes_de_mudanca: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 2 <= len(self.provas) <= 4:
            raise ValueError("O Resumo integrado exige de duas a quatro provas.")
        if not self.veredito.strip():
            raise ValueError("O veredito do Resumo integrado não pode ser vazio.")


@dataclass(frozen=True)
class ContextoRadarResumo:
    """Único sinal externo que pode complementar o Resumo."""

    titulo: str
    evidencia: str
    fonte: str
    horizonte: str
    confianca: str


def selecionar_contexto_radar(
    cenario: CenarioMacro | None,
) -> ContextoRadarResumo | None:
    """Seleciona contexto externo sem repetir sinais do Focus.

    O maior impacto absoluto lidera. ``max`` preserva o primeiro sinal em
    empates, mantendo a ordem explicável do motor macro.
    """
    if cenario is None:
        return None
    candidatos = [
        sinal
        for sinal in cenario.sinais
        if sinal.fonte != FONTE_FOCUS_RADAR and sinal.impacto != 0
    ]
    if not candidatos:
        return None
    sinal = max(candidatos, key=lambda item: abs(item.impacto))
    return ContextoRadarResumo(
        titulo=sinal.titulo,
        evidencia=sinal.evidencia,
        fonte=sinal.fonte,
        horizonte=cenario.horizonte,
        confianca=cenario.confianca,
    )


def _datas_unicas(*datas: date | None) -> tuple[date, ...]:
    return tuple(sorted({data for data in datas if data is not None}))


def _datas_focus(
    focus: ResumoFocusSemanal,
    convergencia: LeituraConvergencia,
) -> tuple[date, ...]:
    if convergencia.focus is not None:
        return _datas_unicas(
            convergencia.focus.data_anterior,
            convergencia.focus.data_atual,
        )
    datas: list[date | None] = [focus.data_mais_recente]
    for destaque in focus.destaques:
        datas.append(destaque.atual.data_coleta)
        if destaque.anterior is not None:
            datas.append(destaque.anterior.data_coleta)
    return _datas_unicas(*datas)


def _datas_curva(
    curva: LeituraCurva,
    convergencia: LeituraConvergencia,
) -> tuple[date, ...]:
    if convergencia.curva is not None:
        return _datas_unicas(
            convergencia.curva.data_anterior,
            convergencia.curva.data_atual,
        )
    return _datas_unicas(
        curva.d21.data_referencia if curva.d21 else None,
        curva.d5.data_referencia if curva.d5 else None,
        curva.atual.data_referencia if curva.atual else None,
    )


def _prova_estado_focus(focus: ResumoFocusSemanal) -> ProvaResumo:
    return ProvaResumo(
        origem=FONTE_FOCUS,
        descricao=(
            f"{titulo_resumo_semanal(focus)}. "
            f"{descricao_resumo_semanal(focus)}"
        ),
    )


def _prova_estado_curva(curva: LeituraCurva) -> ProvaResumo:
    return ProvaResumo(
        origem=FONTE_CURVA,
        descricao=(
            f"{titulo_leitura_curva(curva)}. "
            f"{descricao_leitura_curva(curva)}"
        ),
    )


def _provas_focus(focus: ResumoFocusSemanal) -> list[ProvaResumo]:
    return [
        ProvaResumo(
            origem=FONTE_FOCUS,
            descricao=(
                f"{destaque.atual.indicador}: {formatar_valor(destaque)} "
                f"({formatar_delta(destaque)})."
            ),
        )
        for destaque in focus.destaques
    ]


def _provas_curva(curva: LeituraCurva) -> list[ProvaResumo]:
    provas: list[ProvaResumo] = []
    if curva.movimento_mediano_d5_bps is not None:
        provas.append(
            ProvaResumo(
                origem=FONTE_CURVA,
                descricao=(
                    "Movimento mediano frente a D-5: "
                    f"{formatar_bps(curva.movimento_mediano_d5_bps)}."
                ),
            )
        )
    if curva.inclinacao_atual_bps is not None:
        provas.append(
            ProvaResumo(
                origem=FONTE_CURVA,
                descricao=(
                    "Inclinação entre os vencimentos extremos: "
                    f"{formatar_bps(curva.inclinacao_atual_bps)}."
                ),
            )
        )
    return provas


def _completar_provas(
    candidatas: list[ProvaResumo],
    focus: ResumoFocusSemanal,
    curva: LeituraCurva,
) -> tuple[ProvaResumo, ...]:
    provas: list[ProvaResumo] = []
    for prova in candidatas:
        if prova not in provas:
            provas.append(prova)
        if len(provas) == 4:
            break
    for prova in (_prova_estado_focus(focus), _prova_estado_curva(curva)):
        if len(provas) >= 2:
            break
        if prova not in provas:
            provas.append(prova)
    if len(provas) < 2:
        raise ValueError("As fontes não produziram evidência mínima para o Resumo.")
    return tuple(provas)


def _focus_atual(focus: ResumoFocusSemanal) -> bool:
    return focus.estado in {
        EstadoFocusSemanal.ATUALIZADO,
        EstadoFocusSemanal.SEM_MUDANCA_RELEVANTE,
    }


def _curva_atual(curva: LeituraCurva) -> bool:
    return curva.estado in {EstadoCurva.ATUALIZADA, EstadoCurva.PARCIAL}


def montar_resumo_integrado(
    focus: ResumoFocusSemanal,
    curva: LeituraCurva,
    convergencia: LeituraConvergencia,
) -> ResumoIntegrado:
    """Escolhe a leitura principal sem alterar os três contratos de origem.

    A ordem é deliberadamente simples e documentável: convergência íntegra;
    revisão relevante do Focus; curva atual; Focus atual; qualidade dos dados.
    Estados incompletos nunca são promovidos a uma síntese Focus × Curva.
    """
    datas_fontes = (
        DatasFonteResumo(FONTE_FOCUS, _datas_focus(focus, convergencia)),
        DatasFonteResumo(FONTE_CURVA, _datas_curva(curva, convergencia)),
    )

    if convergencia.estado != EstadoConvergencia.DADOS_INSUFICIENTES:
        provas = [
            ProvaResumo("Focus × Curva", evidencia)
            for evidencia in convergencia.evidencias
        ]
        return ResumoIntegrado(
            prioridade=PrioridadeResumo.FOCUS_CURVA,
            veredito=convergencia.titulo,
            provas=_completar_provas(provas, focus, curva),
            datas_fontes=datas_fontes,
            limites=convergencia.ressalvas,
            condicoes_de_mudanca=convergencia.condicoes_de_mudanca,
        )

    if _focus_atual(focus) and focus.total_relevantes > 0:
        return ResumoIntegrado(
            prioridade=PrioridadeResumo.EXPECTATIVAS,
            veredito=titulo_resumo_semanal(focus),
            provas=_completar_provas(_provas_focus(focus), focus, curva),
            datas_fontes=datas_fontes,
            limites=tuple(
                dict.fromkeys(
                    (
                        "A leitura prioritária usa somente o Focus; a "
                        "convergência não tem dados comparáveis suficientes.",
                        convergencia.resumo,
                        *convergencia.ressalvas,
                    )
                )
            ),
            condicoes_de_mudanca=convergencia.condicoes_de_mudanca,
        )

    if _curva_atual(curva):
        return ResumoIntegrado(
            prioridade=PrioridadeResumo.CURVA,
            veredito=titulo_leitura_curva(curva),
            provas=_completar_provas(_provas_curva(curva), focus, curva),
            datas_fontes=datas_fontes,
            limites=tuple(
                dict.fromkeys(
                    (
                        "A leitura prioritária usa somente a curva; a "
                        "convergência não tem dados comparáveis suficientes.",
                        convergencia.resumo,
                        *convergencia.ressalvas,
                    )
                )
            ),
            condicoes_de_mudanca=convergencia.condicoes_de_mudanca,
        )

    if _focus_atual(focus):
        return ResumoIntegrado(
            prioridade=PrioridadeResumo.EXPECTATIVAS,
            veredito=titulo_resumo_semanal(focus),
            provas=_completar_provas(_provas_focus(focus), focus, curva),
            datas_fontes=datas_fontes,
            limites=tuple(
                dict.fromkeys(
                    (
                        "A leitura prioritária usa somente o Focus; a curva "
                        "atual não está disponível para completar a síntese.",
                        convergencia.resumo,
                        *convergencia.ressalvas,
                    )
                )
            ),
            condicoes_de_mudanca=convergencia.condicoes_de_mudanca,
        )

    return ResumoIntegrado(
        prioridade=PrioridadeResumo.QUALIDADE_DOS_DADOS,
        veredito="As fontes ainda não sustentam um Resumo integrado",
        provas=_completar_provas([], focus, curva),
        datas_fontes=datas_fontes,
        limites=tuple(
            dict.fromkeys(
                (*convergencia.ressalvas, convergencia.resumo)
            )
        ),
        condicoes_de_mudanca=convergencia.condicoes_de_mudanca,
    )
