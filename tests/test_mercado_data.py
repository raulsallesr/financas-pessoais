import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mercado_data import (
    PontoMercado,
    SerieMercado,
    calcular_movimento,
    consolidar_pontos,
    pontos_base_100,
)


def _serie(codigo: str, valores: list[tuple[date, float]]) -> SerieMercado:
    return SerieMercado(
        codigo=codigo,
        nome=codigo,
        unidade="R$",
        fonte="Teste",
        fonte_url="https://example.com",
        pontos=tuple(PontoMercado(*item) for item in valores),
    )


def test_consolidar_pontos_ordena_e_mantem_ultimo_valor_do_dia():
    pontos = consolidar_pontos(
        [
            PontoMercado(date(2026, 8, 2), 2.0),
            PontoMercado(date(2026, 8, 1), 1.0),
            PontoMercado(date(2026, 8, 2), 2.2),
        ]
    )
    assert pontos == (
        PontoMercado(date(2026, 8, 1), 1.0),
        PontoMercado(date(2026, 8, 2), 2.2),
    )


def test_movimento_usa_variacao_de_30_dias_e_limiar_por_ativo():
    serie = _serie(
        "USDBRL",
        [
            (date(2026, 7, 1), 5.0),
            (date(2026, 8, 1), 5.2),
        ],
    )
    movimento = calcular_movimento(serie)
    assert movimento.variacao_30d == 4.0
    assert movimento.direcao == "alta"


def test_base_100_preserva_movimento_relativo():
    serie = _serie(
        "BRENT",
        [
            (date(2026, 7, 1), 80.0),
            (date(2026, 8, 1), 88.0),
        ],
    )
    assert [ponto.valor for ponto in pontos_base_100(serie)] == [
        100.0,
        110.0,
    ]
