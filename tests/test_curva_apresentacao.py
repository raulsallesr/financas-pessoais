import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.core.curva_cenarios import simular_choque_paralelo
from focuslens.core.curva_data import PontoCurva
from focuslens.core.curva_modelo import (
    ComparacaoPontoCurva,
    EstadoCurva,
    FotografiaCurva,
    LeituraCurva,
)
from focuslens.ui.curva_apresentacao import (
    CORES_PERIODOS,
    especificacao_grafico,
    especificacao_grafico_cenario,
    formatar_bps,
    formatar_numero,
    linhas_grafico,
    linhas_grafico_cenario,
    linhas_tabela,
    linhas_tabela_cenario,
)


def _ponto(data_ref: date, ano: int, taxa: float) -> PontoCurva:
    return PontoCurva(
        data_referencia=data_ref,
        tipo_titulo="Tesouro Prefixado",
        vencimento=date(ano, 1, 1),
        taxa_compra=taxa,
        taxa_venda=taxa + 0.1,
        pu_compra=800.0,
        pu_venda=799.0,
        fonte="Teste",
    )


def _leitura() -> LeituraCurva:
    atual_curto = _ponto(date(2026, 8, 26), 2029, 14.0)
    atual_longo = _ponto(date(2026, 8, 26), 2032, 14.4)
    d5_curto = _ponto(date(2026, 8, 19), 2029, 14.2)
    d21_curto = _ponto(date(2026, 7, 28), 2029, 14.3)
    d21_longo = _ponto(date(2026, 7, 28), 2032, 14.6)
    return LeituraCurva(
        estado=EstadoCurva.ATUALIZADA,
        atual=FotografiaCurva(
            data_referencia=date(2026, 8, 26),
            pontos=(atual_curto, atual_longo),
        ),
        d5=FotografiaCurva(
            data_referencia=date(2026, 8, 19),
            pontos=(d5_curto,),
        ),
        d21=FotografiaCurva(
            data_referencia=date(2026, 7, 28),
            pontos=(d21_curto, d21_longo),
        ),
        comparacoes=(
            ComparacaoPontoCurva(
                atual=atual_curto,
                d5=d5_curto,
                d21=d21_curto,
                delta_d5_bps=-20.0,
                delta_d21_bps=-30.0,
            ),
            ComparacaoPontoCurva(
                atual=atual_longo,
                d5=None,
                d21=d21_longo,
                delta_d5_bps=None,
                delta_d21_bps=-20.0,
            ),
        ),
        movimento_mediano_d5_bps=-20.0,
        inclinacao_atual_bps=40.0,
        dias_uteis=0,
    )


def test_formatacao_pt_br_e_ausencia_de_comparacao():
    assert formatar_numero(14.4) == "14,40"
    assert formatar_bps(-20.0) == "-20 bps"
    assert formatar_bps(2.5) == "+2,5 bps"
    assert formatar_bps(None) == "Sem comparação"


def test_grafico_preserva_ordem_e_diferencia_periodos_sem_cor_isolada():
    linhas = linhas_grafico(_leitura())
    especificacao = especificacao_grafico(linhas)
    periodos = list(dict.fromkeys(linha["Período"] for linha in linhas))
    escalas = especificacao["encoding"]

    assert len(linhas) == 5
    assert periodos == ["Atual · 26/08", "D-5 · 19/08", "D-21 · 28/07"]
    assert escalas["color"]["scale"]["range"] == list(CORES_PERIODOS)
    assert escalas["strokeDash"]["scale"]["range"] == [
        [],
        [7, 4],
        [2, 4],
    ]
    assert escalas["y"]["scale"]["zero"] is False


def test_tabela_preserva_lacuna_sem_inventar_taxa():
    linhas = linhas_tabela(_leitura())

    assert linhas[0]["Δ D-5 (bps)"] == -20.0
    assert linhas[1]["D-5 (% a.a.)"] is None
    assert linhas[1]["Δ D-5 (bps)"] is None


def test_apresentacao_do_cenario_diferencia_hipotese_sem_usar_so_cor():
    cenario = simular_choque_paralelo(_leitura().atual, 25)
    linhas = linhas_grafico_cenario(cenario)
    especificacao = especificacao_grafico_cenario(linhas)
    curvas = list(dict.fromkeys(linha["Curva"] for linha in linhas))
    tabela = linhas_tabela_cenario(cenario)

    assert len(linhas) == 4
    assert curvas == ["Observada · 26/08", "Cenário · +25 bps"]
    assert especificacao["encoding"]["color"]["scale"]["range"] == [
        CORES_PERIODOS[0],
        CORES_PERIODOS[1],
    ]
    assert especificacao["encoding"]["strokeDash"]["scale"]["range"] == [
        [],
        [7, 4],
    ]
    assert tabela[0]["Observada (% a.a.)"] == 14.0
    assert tabela[0]["Cenário (% a.a.)"] == 14.25
    assert tabela[0]["Choque (bps)"] == 25
