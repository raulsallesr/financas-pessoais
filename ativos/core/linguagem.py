"""Guardrail de linguagem do módulo Ativos.

Scores e faixas de valor são cálculos quantitativos de uso pessoal. Nenhum texto
exibido pode soar como ordem ou aconselhamento de investimento. Mesmo padrão de
`tests/test_focus_regras.py`, aplicado aos textos deste módulo.
"""

import re

VERBOS_PROIBIDOS = re.compile(
    r"\b(invista|invisto|compre|comprar|venda|vender|recomendo|recomendamos|recomendação"
    r"|preço[- ]alvo)\w*",
    re.IGNORECASE,
)


def textos_proibidos(textos: list[str]) -> list[str]:
    """Devolve os textos que violam o guardrail (vazio = tudo certo)."""
    return [texto for texto in textos if VERBOS_PROIBIDOS.search(texto)]
