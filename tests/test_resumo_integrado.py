import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from convergencia_modelo import (
    DirecaoSinal,
    EstadoConvergencia,
    LeituraConvergencia,
    SinalCurva,
    SinalFocus,
    montar_leitura_convergencia,
)
from curva_data import PontoCurva, TIPO_PREFIXADO_SEM_CUPOM
from curva_modelo import (
    EstadoCurva,
    FotografiaCurva,
    LeituraCurva,
    montar_leitura_curva,
)
from focus_data import LeituraIndicador, comparar
from focus_semanal import (
    EstadoFocusSemanal,
    ResumoFocusSemanal,
    montar_resumo_semanal,
)
from resumo_integrado import (
    FONTE_CURVA,
    FONTE_FOCUS,
    PrioridadeResumo,
    montar_resumo_integrado,
)


HOJE = date(2026, 8, 27)


def _leitura(indicador: str, mediana: float, coleta: date) -> LeituraIndicador:
    return LeituraIndicador(
        indicador=indicador,
        referencia="R6/2026" if indicador == "Selic" else "2026",
        data_coleta=coleta,
        mediana=mediana,
        media=mediana,
        minimo=mediana - 0.2,
        maximo=mediana + 0.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def _focus_atualizado() -> ResumoFocusSemanal:
    comparativos = [
        comparar(
            _leitura("Selic", 13.75, date(2026, 8, 21)),
            _leitura("Selic", 13.50, date(2026, 8, 14)),
        ),
        comparar(
            _leitura("IPCA", 4.85, date(2026, 8, 21)),
            _leitura("IPCA", 4.95, date(2026, 8, 14)),
        ),
    ]
    return montar_resumo_semanal(comparativos, HOJE)


def _focus_indisponivel() -> ResumoFocusSemanal:
    return ResumoFocusSemanal(
        estado=EstadoFocusSemanal.INDISPONIVEL,
        destaques=(),
        total_acompanhados=0,
        total_comparaveis=0,
        total_relevantes=0,
        data_mais_recente=None,
        dias_uteis=None,
    )


def _curva(estado: EstadoCurva = EstadoCurva.ATUALIZADA) -> LeituraCurva:
    atual = FotografiaCurva(date(2026, 8, 26), ())
    d5 = FotografiaCurva(date(2026, 8, 19), ())
    d21 = FotografiaCurva(date(2026, 7, 27), ())
    return LeituraCurva(
        estado=estado,
        atual=atual if estado != EstadoCurva.INDISPONIVEL else None,
        d5=d5 if estado == EstadoCurva.ATUALIZADA else None,
        d21=d21 if estado == EstadoCurva.ATUALIZADA else None,
        comparacoes=(),
        movimento_mediano_d5_bps=(
            -24.0 if estado == EstadoCurva.ATUALIZADA else None
        ),
        inclinacao_atual_bps=(
            82.0 if estado != EstadoCurva.INDISPONIVEL else None
        ),
        dias_uteis=0 if estado != EstadoCurva.INDISPONIVEL else None,
    )


def _convergencia(
    estado: EstadoConvergencia,
) -> LeituraConvergencia:
    publicavel = estado != EstadoConvergencia.DADOS_INSUFICIENTES
    sinal_focus = (
        SinalFocus(
            referencia="R6/2026",
            data_anterior=date(2026, 8, 14),
            data_atual=date(2026, 8, 21),
            valor_anterior=13.50,
            valor_atual=13.75,
            delta_pp=0.25,
            direcao=DirecaoSinal.PRESSIONADA,
        )
        if publicavel
        else None
    )
    sinal_curva = (
        SinalCurva(
            data_anterior=date(2026, 8, 19),
            data_atual=date(2026, 8, 26),
            delta_mediano_bps=-24.0,
            vencimentos_comparaveis=5,
            direcao=DirecaoSinal.BENIGNA,
        )
        if publicavel
        else None
    )
    return LeituraConvergencia(
        estado=estado,
        titulo=(
            "A curva ficou mais benigna que o Focus"
            if publicavel
            else "Ainda não há evidência comparável suficiente"
        ),
        resumo=(
            "Focus subiu e curva caiu frente a D-5."
            if publicavel
            else "Faltam séries comparáveis recentes."
        ),
        focus=sinal_focus,
        curva=sinal_curva,
        ponta_curta=None,
        ponta_longa=None,
        evidencias=(
            (
                "Focus · Selic R6/2026: 13,50% → 13,75%.",
                "Curva · mediana: -24,0 bps.",
            )
            if publicavel
            else ("Faltam séries comparáveis recentes.",)
        ),
        ressalvas=(
            "Taxa de título não é previsão pura da Selic.",
        ),
        condicoes_de_mudanca=(
            "Duas coletas recentes e dois vencimentos em comum.",
        ),
        datas_das_fontes=(
            (
                date(2026, 8, 14),
                date(2026, 8, 21),
                date(2026, 8, 19),
                date(2026, 8, 26),
            )
            if publicavel
            else ()
        ),
    )


def test_convergencia_integra_lidera_sem_recalcular_os_contratos():
    focus = _focus_atualizado()
    curva = _curva()
    convergencia = _convergencia(EstadoConvergencia.CURVA_MAIS_BENIGNA)

    resumo = montar_resumo_integrado(focus, curva, convergencia)

    assert resumo.prioridade == PrioridadeResumo.FOCUS_CURVA
    assert resumo.veredito == convergencia.titulo
    assert [prova.descricao for prova in resumo.provas[:2]] == list(
        convergencia.evidencias
    )
    assert resumo.limites == convergencia.ressalvas
    assert resumo.condicoes_de_mudanca == convergencia.condicoes_de_mudanca
    assert 2 <= len(resumo.provas) <= 4


def test_sem_convergencia_revisao_relevante_do_focus_lidera():
    resumo = montar_resumo_integrado(
        _focus_atualizado(),
        _curva(),
        _convergencia(EstadoConvergencia.DADOS_INSUFICIENTES),
    )

    assert resumo.prioridade == PrioridadeResumo.EXPECTATIVAS
    assert "Selic liderou" in resumo.veredito
    assert any("13,75%" in prova.descricao for prova in resumo.provas)
    assert 2 <= len(resumo.provas) <= 4


def test_curva_atual_permanece_util_quando_focus_falha():
    resumo = montar_resumo_integrado(
        _focus_indisponivel(),
        _curva(),
        _convergencia(EstadoConvergencia.DADOS_INSUFICIENTES),
    )

    assert resumo.prioridade == PrioridadeResumo.CURVA
    assert "caíram" in resumo.veredito
    assert resumo.provas[0].origem == FONTE_CURVA
    assert "-24 bps" in resumo.provas[0].descricao


def test_focus_atual_permanece_util_quando_curva_falha():
    resumo = montar_resumo_integrado(
        _focus_atualizado(),
        _curva(EstadoCurva.INDISPONIVEL),
        _convergencia(EstadoConvergencia.DADOS_INSUFICIENTES),
    )

    assert resumo.prioridade == PrioridadeResumo.EXPECTATIVAS
    assert any(prova.origem == FONTE_FOCUS for prova in resumo.provas)
    assert any("usa somente o Focus" in limite for limite in resumo.limites)


def test_duas_fontes_indisponiveis_nao_viram_sintese_inventada():
    resumo = montar_resumo_integrado(
        _focus_indisponivel(),
        _curva(EstadoCurva.INDISPONIVEL),
        _convergencia(EstadoConvergencia.DADOS_INSUFICIENTES),
    )

    assert resumo.prioridade == PrioridadeResumo.QUALIDADE_DOS_DADOS
    assert resumo.veredito == "As fontes ainda não sustentam um Resumo integrado"
    assert len(resumo.provas) == 2
    assert {prova.origem for prova in resumo.provas} == {
        FONTE_FOCUS,
        FONTE_CURVA,
    }
    assert all(not item.datas for item in resumo.datas_fontes)


def test_datas_ficam_separadas_por_fonte_e_sem_duplicatas():
    resumo = montar_resumo_integrado(
        _focus_atualizado(),
        _curva(),
        _convergencia(EstadoConvergencia.CURVA_MAIS_BENIGNA),
    )

    datas = {item.fonte: item.datas for item in resumo.datas_fontes}
    assert datas[FONTE_FOCUS] == (
        date(2026, 8, 14),
        date(2026, 8, 21),
    )
    assert datas[FONTE_CURVA] == (
        date(2026, 8, 19),
        date(2026, 8, 26),
    )


def test_motores_reais_compoem_o_resumo_com_dados_sinteticos():
    comparativos = [
        comparar(
            _leitura("Selic", 13.75, date(2026, 8, 21)),
            _leitura("Selic", 13.50, date(2026, 8, 14)),
        ),
        comparar(
            _leitura("IPCA", 4.85, date(2026, 8, 21)),
            _leitura("IPCA", 4.95, date(2026, 8, 14)),
        ),
    ]
    datas_curva = (
        date(2026, 8, 19),
        date(2026, 8, 20),
        date(2026, 8, 21),
        date(2026, 8, 24),
        date(2026, 8, 25),
        date(2026, 8, 26),
    )
    pontos = [
        PontoCurva(
            data_referencia=data_ref,
            tipo_titulo=TIPO_PREFIXADO_SEM_CUPOM,
            vencimento=vencimento,
            taxa_compra=taxa_inicial - indice * 0.05,
            taxa_venda=None,
            pu_compra=None,
            pu_venda=None,
            fonte="Tesouro Transparente · fixture sintética",
        )
        for indice, data_ref in enumerate(datas_curva)
        for vencimento, taxa_inicial in (
            (date(2028, 1, 1), 13.0),
            (date(2030, 1, 1), 13.8),
        )
    ]

    focus = montar_resumo_semanal(comparativos, HOJE)
    curva = montar_leitura_curva(pontos, HOJE)
    convergencia = montar_leitura_convergencia(comparativos, curva, HOJE)
    resumo = montar_resumo_integrado(focus, curva, convergencia)

    assert convergencia.estado == EstadoConvergencia.CURVA_MAIS_BENIGNA
    assert resumo.prioridade == PrioridadeResumo.FOCUS_CURVA
    assert resumo.veredito == convergencia.titulo
    assert resumo.datas_fontes[0].datas == (
        date(2026, 8, 14),
        date(2026, 8, 21),
    )
    assert resumo.datas_fontes[1].datas == (
        date(2026, 8, 19),
        date(2026, 8, 26),
    )
