"""Taxonomia compartilhada de classes de ativo, direções de indicador e
unidades de exibição.

Este módulo não depende de nenhum outro módulo do projeto -- é a base comum
que o Boletim Focus e (no futuro) a carteira/calculadora vão reaproveitar.
"""

from enum import Enum


class ClasseAtivo(str, Enum):
    POS_FIXADO = "Renda fixa pós-fixada (CDI/Selic)"
    PRE_FIXADO = "Renda fixa prefixada"
    IPCA_MAIS = "Renda fixa atrelada à inflação (IPCA+)"
    BOLSA = "Ações / Bolsa"
    CAMBIO = "Dólar / moeda estrangeira"


class Direcao(str, Enum):
    SUBIU = "subiu"
    CAIU = "caiu"
    ESTAVEL = "estável"


UNIDADE_INDICADOR = {
    "Selic": "% a.a.",
    "IPCA": "% no ano",
    "Câmbio": "R$",
}
