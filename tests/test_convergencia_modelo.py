import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from convergencia_modelo import (
    DirecaoSinal,
    EstadoConvergencia,
    montar_leitura_convergencia,
)
from curva_data import PontoCurva
from curva_modelo import montar_leitura_curva
from financas_taxonomia import Direcao
from focus_data import ComparativoIndicador, LeituraIndicador, comparar


HOJE = date(2026, 8, 26)
VENCIMENTOS = (2027, 2028, 2029, 2031, 2032)


def _datas_uteis(total: int = 22, fim: date = HOJE) -> list[date]:
    datas = []
    cursor = fim
    while len(datas) < total:
        if cursor.weekday() < 5:
            datas.append(cursor)
        cursor -= timedelta(days=1)
    return sorted(datas)


def _curva(
    deltas_bps: tuple[float, ...],
    *,
    total_datas: int = 22,
    fim: date = HOJE,
    hoje: date = HOJE,
):
    pontos = []
    datas = _datas_uteis(total_datas, fim)
    for indice, data_ref in enumerate(datas):
        for posicao, ano in enumerate(VENCIMENTOS):
            taxa = 12.0 + posicao * 0.2
            if indice == len(datas) - 1:
                taxa += deltas_bps[posicao] / 100
            pontos.append(
                PontoCurva(
                    data_referencia=data_ref,
                    tipo_titulo="Tesouro Prefixado",
                    vencimento=date(ano, 1, 1),
                    taxa_compra=taxa,
                    taxa_venda=None,
                    pu_compra=None,
                    pu_venda=None,
                    fonte="Teste sintético",
                )
            )
    return montar_leitura_curva(pontos, hoje)


def _leitura_selic(
    valor: float,
    data_coleta: date,
    referencia: str = "R6/2026",
) -> LeituraIndicador:
    return LeituraIndicador(
        indicador="Selic",
        referencia=referencia,
        data_coleta=data_coleta,
        mediana=valor,
        media=valor,
        minimo=valor - 0.25,
        maximo=valor + 0.25,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def _focus(delta_pp: float) -> list[ComparativoIndicador]:
    anterior = _leitura_selic(13.75, date(2026, 8, 14))
    atual = _leitura_selic(13.75 + delta_pp, date(2026, 8, 21))
    return [comparar(atual, anterior)]


@pytest.mark.parametrize(
    ("delta_focus", "deltas_curva", "estado"),
    [
        (0.0, (0.0, 0.0, 0.0, 0.0, 0.0), EstadoConvergencia.ALINHADOS),
        (0.25, (8.0, 9.0, 10.0, 11.0, 12.0), EstadoConvergencia.ALINHADOS),
        (-0.25, (-8.0, -9.0, -10.0, -11.0, -12.0), EstadoConvergencia.ALINHADOS),
        (0.0, (8.0, 9.0, 10.0, 11.0, 12.0), EstadoConvergencia.CURVA_MAIS_PRESSIONADA),
        (0.0, (-8.0, -9.0, -10.0, -11.0, -12.0), EstadoConvergencia.CURVA_MAIS_BENIGNA),
        (-0.25, (0.0, 0.0, 0.0, 0.0, 0.0), EstadoConvergencia.CURVA_MAIS_PRESSIONADA),
        (0.25, (0.0, 0.0, 0.0, 0.0, 0.0), EstadoConvergencia.CURVA_MAIS_BENIGNA),
    ],
)
def test_classifica_estados_pela_ordem_das_direcoes(
    delta_focus,
    deltas_curva,
    estado,
):
    leitura = montar_leitura_convergencia(
        _focus(delta_focus),
        _curva(deltas_curva),
        HOJE,
    )

    assert leitura.estado == estado
    assert leitura.focus is not None
    assert leitura.curva is not None
    assert len(leitura.evidencias) == 4
    assert leitura.datas_das_fontes == (
        date(2026, 8, 14),
        date(2026, 8, 21),
        date(2026, 8, 19),
        date(2026, 8, 26),
    )


def test_pontas_opostas_preservam_sinal_misto():
    leitura = montar_leitura_convergencia(
        _focus(0.0),
        _curva((-12.0, -8.0, 0.0, 8.0, 12.0)),
        HOJE,
    )

    assert leitura.estado == EstadoConvergencia.SINAIS_MISTOS
    assert leitura.curva.direcao == DirecaoSinal.MISTA
    assert leitura.ponta_curta.direcao == DirecaoSinal.BENIGNA
    assert leitura.ponta_curta.delta_mediano_bps == -10.0
    assert leitura.ponta_longa.direcao == DirecaoSinal.PRESSIONADA
    assert leitura.ponta_longa.delta_mediano_bps == 10.0
    assert "deixa de ser mista" in leitura.condicoes_de_mudanca[0]


def test_limites_exatos_permanecem_estaveis():
    leitura = montar_leitura_convergencia(
        _focus(0.10),
        _curva((-2.0, -2.0, 0.0, 2.0, 2.0)),
        HOJE,
    )

    assert leitura.estado == EstadoConvergencia.ALINHADOS
    assert leitura.focus.direcao == DirecaoSinal.ESTAVEL
    assert leitura.curva.direcao == DirecaoSinal.ESTAVEL


@pytest.mark.parametrize("caso", ["sem_anterior", "referencia", "defasado"])
def test_focus_incomparavel_resulta_em_dados_insuficientes(caso):
    atual = _leitura_selic(13.75, date(2026, 8, 21))
    anterior = _leitura_selic(13.50, date(2026, 8, 14))
    hoje = HOJE
    if caso == "sem_anterior":
        comparativo = comparar(atual, None)
    elif caso == "referencia":
        anterior = _leitura_selic(
            13.50,
            date(2026, 8, 14),
            referencia="R5/2026",
        )
        comparativo = ComparativoIndicador(
            atual=atual,
            anterior=anterior,
            delta=0.25,
            direcao=Direcao.SUBIU,
        )
    else:
        hoje = date(2026, 9, 15)
        comparativo = comparar(atual, anterior)

    leitura = montar_leitura_convergencia(
        [comparativo],
        _curva((0.0, 0.0, 0.0, 0.0, 0.0)),
        hoje,
    )

    assert leitura.estado == EstadoConvergencia.DADOS_INSUFICIENTES
    assert leitura.focus is None
    assert leitura.evidencias
    assert leitura.condicoes_de_mudanca


def test_curva_sem_dois_vencimentos_em_comum_e_insuficiente():
    leitura_curva = _curva((0.0, 0.0, 0.0, 0.0, 0.0))
    leitura_curva = leitura_curva.__class__(
        estado=leitura_curva.estado,
        atual=leitura_curva.atual,
        d5=leitura_curva.d5,
        d21=leitura_curva.d21,
        comparacoes=leitura_curva.comparacoes[:1],
        movimento_mediano_d5_bps=0.0,
        inclinacao_atual_bps=leitura_curva.inclinacao_atual_bps,
        dias_uteis=leitura_curva.dias_uteis,
    )

    leitura = montar_leitura_convergencia(_focus(0.0), leitura_curva, HOJE)

    assert leitura.estado == EstadoConvergencia.DADOS_INSUFICIENTES
    assert "dois vencimentos" in leitura.resumo


def test_curva_defasada_e_insuficiente():
    curva = _curva(
        (0.0, 0.0, 0.0, 0.0, 0.0),
        fim=date(2026, 8, 14),
        hoje=HOJE,
    )

    leitura = montar_leitura_convergencia(_focus(0.0), curva, HOJE)

    assert leitura.estado == EstadoConvergencia.DADOS_INSUFICIENTES
    assert "defasada" in leitura.resumo


def test_d21_nao_e_exigido_quando_d5_e_suficiente():
    curva = _curva(
        (-8.0, -9.0, -10.0, -11.0, -12.0),
        total_datas=6,
    )

    leitura = montar_leitura_convergencia(_focus(0.0), curva, HOJE)

    assert leitura.estado == EstadoConvergencia.CURVA_MAIS_BENIGNA
    assert leitura.curva.vencimentos_comparaveis == 5


def test_motor_recalcula_delta_focus_a_partir_dos_valores():
    anterior = _leitura_selic(13.50, date(2026, 8, 14))
    atual = _leitura_selic(13.75, date(2026, 8, 21))
    inconsistente = ComparativoIndicador(
        atual=atual,
        anterior=anterior,
        delta=-9.0,
        direcao=Direcao.CAIU,
    )

    leitura = montar_leitura_convergencia(
        [inconsistente],
        _curva((10.0, 10.0, 10.0, 10.0, 10.0)),
        HOJE,
    )

    assert leitura.estado == EstadoConvergencia.ALINHADOS
    assert leitura.focus.delta_pp == 0.25
    assert leitura.focus.direcao == DirecaoSinal.PRESSIONADA
