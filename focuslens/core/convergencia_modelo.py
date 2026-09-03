"""Motor puro da leitura direcional Focus × Curva.

Compara a revisão da mediana da Selic para a mesma reunião do Focus com o
movimento D-5 dos vencimentos idênticos da curva prefixada. O motor descreve
convergência, não causalidade, previsão ou recomendação.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from statistics import median

from focuslens.core.curva_modelo import (
    LIMIAR_MOVIMENTO_BPS,
    EstadoCurva,
    LeituraCurva,
)
from focuslens.core.financas_taxonomia import Direcao
from focuslens.core.focus_atualizacao import dias_uteis_desde
from focuslens.core.focus_data import ComparativoIndicador
from focuslens.core.focus_semanal import LIMITE_DEFASAGEM_DIAS_UTEIS
from focuslens.core.motor_indicadores import classificar_direcao, limiar_estavel

MINIMO_VENCIMENTOS_COMPARAVEIS = 2
MINIMO_VENCIMENTOS_PARA_PONTAS = 4


class DirecaoSinal(str, Enum):
    BENIGNA = "Mais benigna"
    ESTAVEL = "Estável"
    PRESSIONADA = "Mais pressionada"
    MISTA = "Mista"
    INDISPONIVEL = "Indisponível"


class EstadoConvergencia(str, Enum):
    ALINHADOS = "Alinhados"
    CURVA_MAIS_PRESSIONADA = "Curva mais pressionada"
    CURVA_MAIS_BENIGNA = "Curva mais benigna"
    SINAIS_MISTOS = "Sinais mistos"
    DADOS_INSUFICIENTES = "Dados insuficientes"


@dataclass(frozen=True)
class SinalFocus:
    referencia: str
    data_anterior: date
    data_atual: date
    valor_anterior: float
    valor_atual: float
    delta_pp: float
    direcao: DirecaoSinal


@dataclass(frozen=True)
class SinalCurva:
    data_anterior: date
    data_atual: date
    delta_mediano_bps: float
    vencimentos_comparaveis: int
    direcao: DirecaoSinal


@dataclass(frozen=True)
class SinalPonta:
    nome: str
    delta_mediano_bps: float
    vencimentos: tuple[date, ...]
    direcao: DirecaoSinal


@dataclass(frozen=True)
class LeituraConvergencia:
    estado: EstadoConvergencia
    titulo: str
    resumo: str
    focus: SinalFocus | None
    curva: SinalCurva | None
    ponta_curta: SinalPonta | None
    ponta_longa: SinalPonta | None
    evidencias: tuple[str, ...]
    ressalvas: tuple[str, ...]
    condicoes_de_mudanca: tuple[str, ...]
    datas_das_fontes: tuple[date, ...]


def _direcao_focus(direcao: Direcao) -> DirecaoSinal:
    return {
        Direcao.SUBIU: DirecaoSinal.PRESSIONADA,
        Direcao.CAIU: DirecaoSinal.BENIGNA,
        Direcao.ESTAVEL: DirecaoSinal.ESTAVEL,
    }[direcao]


def _direcao_delta_bps(delta: float) -> DirecaoSinal:
    if delta > LIMIAR_MOVIMENTO_BPS:
        return DirecaoSinal.PRESSIONADA
    if delta < -LIMIAR_MOVIMENTO_BPS:
        return DirecaoSinal.BENIGNA
    return DirecaoSinal.ESTAVEL


def _formatar_numero(valor: float, casas: int = 2) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def _formatar_delta(valor: float, unidade: str, casas: int = 2) -> str:
    return f"{valor:+.{casas}f}".replace(".", ",") + f" {unidade}"


def _sinal_focus(
    comparativos: list[ComparativoIndicador],
    hoje: date,
) -> tuple[SinalFocus | None, str | None]:
    candidatos = [
        item for item in comparativos if item.atual.indicador == "Selic"
    ]
    if not candidatos:
        return None, "Falta a leitura da Selic no Focus."
    comparativo = max(candidatos, key=lambda item: item.atual.data_coleta)
    anterior = comparativo.anterior
    if anterior is None:
        return None, "Falta uma coleta anterior comparável da Selic."
    if (
        anterior.indicador != "Selic"
        or anterior.referencia != comparativo.atual.referencia
        or anterior.data_coleta >= comparativo.atual.data_coleta
    ):
        return None, "As coletas da Selic não usam a mesma referência."
    if (
        dias_uteis_desde(comparativo.atual.data_coleta, hoje)
        > LIMITE_DEFASAGEM_DIAS_UTEIS
    ):
        return None, "A coleta mais recente da Selic está defasada."
    delta = round(comparativo.atual.mediana - anterior.mediana, 4)
    return (
        SinalFocus(
            referencia=comparativo.atual.referencia,
            data_anterior=anterior.data_coleta,
            data_atual=comparativo.atual.data_coleta,
            valor_anterior=anterior.mediana,
            valor_atual=comparativo.atual.mediana,
            delta_pp=delta,
            direcao=_direcao_focus(classificar_direcao(delta, "Selic")),
        ),
        None,
    )


def _deltas_curva(
    leitura: LeituraCurva,
) -> list[tuple[date, float]]:
    return sorted(
        (
            (item.atual.vencimento, item.delta_d5_bps)
            for item in leitura.comparacoes
            if item.delta_d5_bps is not None
        ),
        key=lambda item: item[0],
    )


def _sinal_ponta(
    nome: str,
    pontos: list[tuple[date, float]],
) -> SinalPonta:
    delta = round(float(median(valor for _, valor in pontos)), 1)
    return SinalPonta(
        nome=nome,
        delta_mediano_bps=delta,
        vencimentos=tuple(vencimento for vencimento, _ in pontos),
        direcao=_direcao_delta_bps(delta),
    )


def _sinais_curva(
    leitura: LeituraCurva,
) -> tuple[SinalCurva | None, SinalPonta | None, SinalPonta | None, str | None]:
    if leitura.estado == EstadoCurva.INDISPONIVEL or leitura.atual is None:
        return None, None, None, "Falta uma fotografia íntegra da curva."
    if leitura.estado == EstadoCurva.DEFASADA:
        return None, None, None, "A fotografia mais recente da curva está defasada."
    if leitura.d5 is None:
        return None, None, None, "Falta a fotografia D-5 da curva."
    deltas = _deltas_curva(leitura)
    if len(deltas) < MINIMO_VENCIMENTOS_COMPARAVEIS:
        return (
            None,
            None,
            None,
            "Faltam ao menos dois vencimentos iguais entre a curva atual e D-5.",
        )

    delta_geral = round(float(median(valor for _, valor in deltas)), 1)
    direcao_geral = _direcao_delta_bps(delta_geral)
    curta = longa = None
    if len(deltas) >= MINIMO_VENCIMENTOS_PARA_PONTAS:
        tamanho = len(deltas) // 2
        curta = _sinal_ponta("Ponta curta", deltas[:tamanho])
        longa = _sinal_ponta("Ponta longa", deltas[-tamanho:])
        opostas = {
            curta.direcao,
            longa.direcao,
        } == {DirecaoSinal.BENIGNA, DirecaoSinal.PRESSIONADA}
        if opostas:
            direcao_geral = DirecaoSinal.MISTA

    deltas_relevantes = {
        _direcao_delta_bps(valor)
        for _, valor in deltas
        if _direcao_delta_bps(valor) != DirecaoSinal.ESTAVEL
    }
    if (
        direcao_geral == DirecaoSinal.ESTAVEL
        and deltas_relevantes
        == {DirecaoSinal.BENIGNA, DirecaoSinal.PRESSIONADA}
    ):
        direcao_geral = DirecaoSinal.MISTA

    curva = SinalCurva(
        data_anterior=leitura.d5.data_referencia,
        data_atual=leitura.atual.data_referencia,
        delta_mediano_bps=delta_geral,
        vencimentos_comparaveis=len(deltas),
        direcao=direcao_geral,
    )
    return curva, curta, longa, None


def _estado(
    focus: SinalFocus,
    curva: SinalCurva,
) -> EstadoConvergencia:
    if curva.direcao == DirecaoSinal.MISTA:
        return EstadoConvergencia.SINAIS_MISTOS
    escala = {
        DirecaoSinal.BENIGNA: -1,
        DirecaoSinal.ESTAVEL: 0,
        DirecaoSinal.PRESSIONADA: 1,
    }
    focus_nivel = escala[focus.direcao]
    curva_nivel = escala[curva.direcao]
    if focus_nivel == curva_nivel:
        return EstadoConvergencia.ALINHADOS
    if curva_nivel > focus_nivel:
        return EstadoConvergencia.CURVA_MAIS_PRESSIONADA
    return EstadoConvergencia.CURVA_MAIS_BENIGNA


def _titulo(
    estado: EstadoConvergencia,
    focus: SinalFocus | None,
) -> str:
    if estado == EstadoConvergencia.DADOS_INSUFICIENTES:
        return "Ainda não há evidência comparável suficiente"
    if estado == EstadoConvergencia.SINAIS_MISTOS:
        return "A curva trouxe sinais mistos entre os vencimentos"
    if estado == EstadoConvergencia.CURVA_MAIS_PRESSIONADA:
        return "A curva ficou mais pressionada que o Focus"
    if estado == EstadoConvergencia.CURVA_MAIS_BENIGNA:
        return "A curva ficou mais benigna que o Focus"
    if focus and focus.direcao == DirecaoSinal.PRESSIONADA:
        return "Focus e curva apontam mais pressão nos juros"
    if focus and focus.direcao == DirecaoSinal.BENIGNA:
        return "Focus e curva apontam alívio nos juros"
    return "Focus e curva ficaram dentro dos limiares"


def _resumo(focus: SinalFocus, curva: SinalCurva) -> str:
    return (
        f"No Focus, a Selic {focus.referencia} foi de "
        f"{_formatar_numero(focus.valor_anterior)}% para "
        f"{_formatar_numero(focus.valor_atual)}% "
        f"({_formatar_delta(focus.delta_pp, 'p.p.')}; "
        f"{focus.direcao.value.lower()}). Na curva, a mediana de "
        f"{curva.vencimentos_comparaveis} vencimentos mudou "
        f"{_formatar_delta(curva.delta_mediano_bps, 'bps', 1)} "
        f"({curva.direcao.value.lower()}) frente a D‑5."
    )


def _evidencias(
    focus: SinalFocus,
    curva: SinalCurva,
    curta: SinalPonta | None,
    longa: SinalPonta | None,
) -> tuple[str, ...]:
    itens = [
        (
            f"Focus · Selic {focus.referencia}: "
            f"{_formatar_numero(focus.valor_anterior)}% → "
            f"{_formatar_numero(focus.valor_atual)}% entre "
            f"{focus.data_anterior:%d/%m/%Y} e {focus.data_atual:%d/%m/%Y}."
        ),
        (
            f"Curva · mediana: "
            f"{_formatar_delta(curva.delta_mediano_bps, 'bps', 1)} em "
            f"{curva.vencimentos_comparaveis} vencimentos entre "
            f"{curva.data_anterior:%d/%m/%Y} e {curva.data_atual:%d/%m/%Y}."
        ),
    ]
    for ponta in (curta, longa):
        if ponta is not None:
            anos = ", ".join(str(data.year) for data in ponta.vencimentos)
            itens.append(
                f"{ponta.nome}: {_formatar_delta(ponta.delta_mediano_bps, 'bps', 1)} "
                f"nos vencimentos {anos} ({ponta.direcao.value.lower()})."
            )
    return tuple(itens)


def _condicoes(
    estado: EstadoConvergencia,
) -> tuple[str, ...]:
    limiar_focus = _formatar_numero(limiar_estavel("Selic"))
    limiar_curva = _formatar_numero(LIMIAR_MOVIMENTO_BPS, 0)
    base = (
        f"A direção do Focus muda quando a revisão da Selic ultrapassa "
        f"±{limiar_focus} p.p. para a mesma reunião.",
        f"A direção da curva muda quando a mediana D‑5 cruza "
        f"±{limiar_curva} bps.",
    )
    if estado == EstadoConvergencia.SINAIS_MISTOS:
        return (
            "A leitura deixa de ser mista quando as pontas param de apontar "
            "direções opostas e a mediana consolida um sentido.",
            *base,
        )
    return base


def _insuficiente(
    motivos: list[str],
    focus: SinalFocus | None,
    curva: SinalCurva | None,
    curta: SinalPonta | None,
    longa: SinalPonta | None,
) -> LeituraConvergencia:
    motivos_unicos = tuple(dict.fromkeys(motivos))
    resumo = " ".join(motivos_unicos)
    evidencias = list(motivos_unicos)
    datas: list[date] = []
    if focus is not None:
        evidencias.insert(
            0,
            f"Focus · Selic {focus.referencia}: "
            f"{_formatar_numero(focus.valor_anterior)}% → "
            f"{_formatar_numero(focus.valor_atual)}%.",
        )
        datas.extend((focus.data_anterior, focus.data_atual))
    if curva is not None:
        evidencias.insert(
            0,
            f"Curva · mediana: "
            f"{_formatar_delta(curva.delta_mediano_bps, 'bps', 1)}.",
        )
        datas.extend((curva.data_anterior, curva.data_atual))
    return LeituraConvergencia(
        estado=EstadoConvergencia.DADOS_INSUFICIENTES,
        titulo=_titulo(EstadoConvergencia.DADOS_INSUFICIENTES, None),
        resumo=resumo,
        focus=focus,
        curva=curva,
        ponta_curta=curta,
        ponta_longa=longa,
        evidencias=tuple(evidencias),
        ressalvas=(
            "Sem dados comparáveis, o motor não completa lacunas com narrativa.",
        ),
        condicoes_de_mudanca=(
            "São necessárias duas coletas recentes da Selic para a mesma "
            "reunião e ao menos dois vencimentos iguais na curva atual e D-5.",
        ),
        datas_das_fontes=tuple(datas),
    )


def montar_leitura_convergencia(
    comparativos_focus: list[ComparativoIndicador],
    leitura_curva: LeituraCurva,
    hoje: date,
) -> LeituraConvergencia:
    """Monta os cinco estados da Etapa 3 sem acessar rede, cache ou UI."""
    focus, erro_focus = _sinal_focus(comparativos_focus, hoje)
    curva, curta, longa, erro_curva = _sinais_curva(leitura_curva)
    motivos = [motivo for motivo in (erro_focus, erro_curva) if motivo]
    if focus is None or curva is None:
        return _insuficiente(motivos, focus, curva, curta, longa)

    estado = _estado(focus, curva)
    return LeituraConvergencia(
        estado=estado,
        titulo=_titulo(estado, focus),
        resumo=_resumo(focus, curva),
        focus=focus,
        curva=curva,
        ponta_curta=curta,
        ponta_longa=longa,
        evidencias=_evidencias(focus, curva, curta, longa),
        ressalvas=(
            "Os intervalos do Focus e da curva podem ter datas diferentes; "
            "ambos ficam visíveis na evidência.",
            "Taxa de título não é previsão pura da Selic: prêmio de prazo, "
            "risco e liquidez também podem mover a curva.",
        ),
        condicoes_de_mudanca=_condicoes(estado),
        datas_das_fontes=(
            focus.data_anterior,
            focus.data_atual,
            curva.data_anterior,
            curva.data_atual,
        ),
    )
