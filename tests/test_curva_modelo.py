import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.core.curva_data import PontoCurva
from focuslens.core.curva_modelo import (
    EstadoCurva,
    descricao_leitura_curva,
    montar_leitura_curva,
    titulo_leitura_curva,
)


HOJE = date(2026, 8, 26)


def _datas_uteis(total: int) -> list[date]:
    datas: list[date] = []
    cursor = HOJE
    while len(datas) < total:
        if cursor.weekday() < 5:
            datas.append(cursor)
        cursor -= timedelta(days=1)
    return sorted(datas)


def _ponto(data_ref: date, ano: int, taxa: float) -> PontoCurva:
    return PontoCurva(
        data_referencia=data_ref,
        tipo_titulo="Tesouro Prefixado",
        vencimento=date(ano, 1, 1),
        taxa_compra=taxa,
        taxa_venda=taxa + 0.12,
        pu_compra=800.0,
        pu_venda=799.0,
        fonte="Teste",
    )


def _historico(total_datas: int = 22) -> list[PontoCurva]:
    pontos = []
    for indice, data_ref in enumerate(_datas_uteis(total_datas)):
        for ano, premio in ((2028, 0.0), (2030, 0.3), (2032, 0.6)):
            pontos.append(
                _ponto(data_ref, ano, 13.0 + premio + indice * 0.01)
            )
    return pontos


def test_leitura_escolhe_datas_observadas_d5_d21_e_calcula_bps():
    leitura = montar_leitura_curva(_historico(), HOJE)

    assert leitura.estado == EstadoCurva.ATUALIZADA
    assert leitura.atual.data_referencia == HOJE
    assert leitura.d5.data_referencia == _datas_uteis(22)[-6]
    assert leitura.d21.data_referencia == _datas_uteis(22)[0]
    assert leitura.movimento_mediano_d5_bps == 5.0
    assert leitura.inclinacao_atual_bps == 60.0
    assert all(
        comparacao.delta_d5_bps == 5.0
        for comparacao in leitura.comparacoes
    )
    assert titulo_leitura_curva(leitura) == (
        "Taxas prefixadas subiram frente a D-5"
    )
    assert "+5,0 bps" in descricao_leitura_curva(leitura)


def test_comparacao_nao_inventa_taxa_para_vencimento_ausente():
    historico = _historico()
    data_d5 = _datas_uteis(22)[-6]
    historico = [
        ponto
        for ponto in historico
        if not (
            ponto.data_referencia == data_d5
            and ponto.vencimento.year == 2032
        )
    ]

    leitura = montar_leitura_curva(historico, HOJE)
    comparacao = next(
        item
        for item in leitura.comparacoes
        if item.atual.vencimento.year == 2032
    )

    assert comparacao.d5 is None
    assert comparacao.delta_d5_bps is None


def test_estados_indisponivel_parcial_e_defasado():
    indisponivel = montar_leitura_curva([], HOJE)
    parcial = montar_leitura_curva(_historico(5), HOJE)
    antigos = [
        PontoCurva(
            data_referencia=ponto.data_referencia - timedelta(days=10),
            tipo_titulo=ponto.tipo_titulo,
            vencimento=ponto.vencimento,
            taxa_compra=ponto.taxa_compra,
            taxa_venda=ponto.taxa_venda,
            pu_compra=ponto.pu_compra,
            pu_venda=ponto.pu_venda,
            fonte=ponto.fonte,
        )
        for ponto in _historico()
    ]
    defasado = montar_leitura_curva(antigos, HOJE)

    assert indisponivel.estado == EstadoCurva.INDISPONIVEL
    assert parcial.estado == EstadoCurva.PARCIAL
    assert defasado.estado == EstadoCurva.DEFASADA
    assert "indisponível" in titulo_leitura_curva(indisponivel)
    assert "histórico ainda parcial" in titulo_leitura_curva(parcial)
    assert "defasada" in titulo_leitura_curva(defasado)


def test_movimento_misto_recebe_titulo_proprio():
    historico = _historico()
    atuais = [
        ponto
        for ponto in historico
        if ponto.data_referencia == HOJE
    ]
    ajustes = {2028: 0.08, 2030: -0.12, 2032: -0.07}
    historico = [
        ponto
        for ponto in historico
        if ponto.data_referencia != HOJE
    ] + [
        _ponto(
            ponto.data_referencia,
            ponto.vencimento.year,
            ponto.taxa_compra + ajustes[ponto.vencimento.year],
        )
        for ponto in atuais
    ]

    leitura = montar_leitura_curva(historico, HOJE)

    assert titulo_leitura_curva(leitura) == (
        "A curva prefixada teve movimentos mistos"
    )
