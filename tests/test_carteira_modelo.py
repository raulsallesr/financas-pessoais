import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.core.carteira_modelo import (
    PosicaoCarteira,
    comparar_com_benchmarks,
    cruzar_cenario,
    montar_posicoes,
    resumir_carteira,
)
from focuslens.core.macro_modelo import CenarioMacro, PerspectivaClasse
from focuslens.core.mercado_data import PontoMercado, SerieMercado


def _cenario():
    return CenarioMacro(
        titulo="Cenário de teste",
        horizonte="4–12 semanas",
        confianca="moderada",
        resumo="Resumo",
        projecoes=(),
        eixos=(),
        perspectivas=(
            PerspectivaClasse(
                classe="Pós-fixados",
                estado="vento favorável",
                explicacao="Juros altos elevam a remuneração corrente.",
            ),
            PerspectivaClasse(
                classe="Bolsa brasileira",
                estado="mais pressionado",
                explicacao="Juros altos pressionam o custo de capital.",
            ),
        ),
        invalidadores=(),
        temas_editoriais=(),
        sinais=(),
    )


def test_montar_posicoes_ignora_linha_vazia_e_normaliza_valores():
    posicoes = montar_posicoes(
        [
            {
                "Ativo": "",
                "Classe": "Outros",
                "Valor atual (R$)": None,
            },
            {
                "Ativo": "Tesouro Selic",
                "Classe": "Renda fixa pós-fixada",
                "Valor atual (R$)": 12_000,
                "Valor investido (R$)": 10_000,
                "Comparar com": "CDI",
            },
        ]
    )
    assert posicoes == (
        PosicaoCarteira(
            ativo="Tesouro Selic",
            classe="Renda fixa pós-fixada",
            valor_atual=12_000,
            valor_investido=10_000,
            benchmark="CDI",
        ),
    )


def test_resumo_calcula_alocacao_resultado_e_concentracao():
    posicoes = (
        PosicaoCarteira(
            "Tesouro Selic",
            "Renda fixa pós-fixada",
            12_000,
            10_000,
        ),
        PosicaoCarteira(
            "ETF",
            "Bolsa brasileira",
            8_000,
            10_000,
        ),
    )
    resumo = resumir_carteira(posicoes)
    assert resumo.total_atual == 20_000
    assert resumo.maior_concentracao_percentual == 60
    assert resumo.resultado_conhecido == 0
    assert resumo.retorno_conhecido_percentual == 0
    assert dict(resumo.alocacao_por_classe) == {
        "Renda fixa pós-fixada": 12_000,
        "Bolsa brasileira": 8_000,
    }


def test_carteira_cruza_peso_com_perspectiva_sem_gerar_recomendacao():
    posicoes = (
        PosicaoCarteira(
            "Tesouro Selic",
            "Renda fixa pós-fixada",
            75_000,
        ),
        PosicaoCarteira("ETF", "Bolsa brasileira", 25_000),
    )
    impactos = cruzar_cenario(posicoes, _cenario())
    assert impactos[0].estado == "vento favorável"
    assert impactos[0].peso_percentual == 75
    assert impactos[1].estado == "mais pressionado"


def test_comparacao_usa_retorno_informado_e_base_100_do_ano():
    posicao = PosicaoCarteira(
        "Tesouro Selic",
        "Renda fixa pós-fixada",
        11_000,
        10_000,
        "CDI",
    )
    serie = SerieMercado(
        codigo="CDI",
        nome="CDI acumulado",
        unidade="Índice acumulado",
        fonte="Teste",
        fonte_url="https://example.com",
        pontos=(
            PontoMercado(date(2026, 1, 2), 100),
            PontoMercado(date(2026, 8, 4), 108),
        ),
    )
    comparacao = comparar_com_benchmarks((posicao,), (serie,))[0]
    assert round(comparacao.retorno_posicao_percentual, 2) == 10
    assert comparacao.retorno_benchmark_percentual == 8
