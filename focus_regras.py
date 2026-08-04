"""Narrativa em linguagem simples (com analogias) do que mudou no Boletim Focus.

Regra de conteúdo: frases sempre descritivas/históricas, nunca imperativas.
Nunca usar verbos como "invista", "compre", "venda", "recomendo" -- ver
tests/test_focus_regras.py, que varre este arquivo em busca desse vocabulário.
"""

from __future__ import annotations

from financas_taxonomia import Direcao, UNIDADE_INDICADOR
from focus_data import ComparativoIndicador
from motor_indicadores import EfeitoClasseAtivo, efeitos_por_indicador

_ANALOGIAS = {
    "Selic": (
        'Pense na Selic como o "preço do dinheiro no atacado": quando ela '
        "sobe, todo o crédito da economia fica mais caro, do cartão ao "
        "financiamento."
    ),
    "IPCA": (
        "O IPCA é o termômetro da inflação: mede quanto mais caro ficou, em "
        "média, o que uma família brasileira compra todo mês."
    ),
    "Câmbio": (
        "O câmbio é quantos reais custam um dólar -- como o preço de uma "
        "mercadoria estrangeira, ele sobe quando há mais gente querendo "
        "comprar dólar do que vender."
    ),
    "PIB Total": (
        "O PIB mede o tamanho da economia: pense nele como o 'bolo' que o "
        "país inteiro produz em um ano -- quando a expectativa de "
        "crescimento sobe, o bolo esperado para este ano fica maior."
    ),
    "IGP-M": (
        "O IGP-M é outro termômetro de preços, mas olha mais para o atacado "
        "e o câmbio -- é o índice mais usado para reajustar contrato de "
        "aluguel, e pode se mover de forma bem diferente do IPCA."
    ),
    "Dívida líquida do setor público": (
        "Pense nisso como o cartão de crédito do país: mostra quanto o "
        "governo deve, em proporção a tudo que o país produz (o PIB) -- "
        "quanto maior essa conta, mais caro costuma ficar para o governo "
        "tomar dinheiro emprestado."
    ),
}


def explicar_leigo(comparativo: ComparativoIndicador) -> str:
    indicador = comparativo.atual.indicador
    analogia = _ANALOGIAS.get(indicador, "")
    unidade = UNIDADE_INDICADOR.get(indicador, "")

    if comparativo.anterior is None:
        return (
            f"Esta é a primeira leitura registrada de {indicador} "
            f"({comparativo.atual.mediana:.2f}{unidade}). {analogia}"
        )

    if comparativo.direcao == Direcao.ESTAVEL:
        return (
            f"A expectativa de {indicador} ficou praticamente estável esta "
            f"semana ({comparativo.atual.mediana:.2f}{unidade}, quase igual "
            f"à leitura anterior). {analogia}"
        )

    verbo = "subiu" if comparativo.direcao == Direcao.SUBIU else "caiu"
    return (
        f"A expectativa de {indicador} {verbo} de "
        f"{comparativo.anterior.mediana:.2f}{unidade} para "
        f"{comparativo.atual.mediana:.2f}{unidade} esta semana. {analogia}"
    )


def resumo_efeitos(comparativo: ComparativoIndicador) -> list[EfeitoClasseAtivo]:
    return efeitos_por_indicador(comparativo.atual.indicador, comparativo.direcao)
