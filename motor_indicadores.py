"""Motor genérico: traduz uma mudança de expectativa de um indicador macro em
efeitos esperados por classe de ativo.

Recebe só indicador + direção -- nunca dados do usuário (patrimônio, carteira,
perfil). Isso mantém o conteúdo educacional e histórico, nunca uma
recomendação personalizada. Features futuras (carteira, calculadora) cruzam
esta saída com os dados do usuário fora deste módulo.
"""

from __future__ import annotations

from dataclasses import dataclass

from financas_taxonomia import ClasseAtivo, Direcao

LIMIAR_ESTAVEL_PADRAO = 0.05
LIMIARES_ESTAVEL = {
    "Selic": 0.10,
    "IPCA": 0.05,
    "Câmbio": 0.05,
    "PIB Total": 0.05,
    "IGP-M": 0.10,
    "Dívida líquida do setor público": 0.25,
}


@dataclass(frozen=True)
class EfeitoClasseAtivo:
    classe: ClasseAtivo
    sentido: str  # "positivo", "negativo" ou "neutro"
    explicacao: str


_REGRAS = {
    ("Selic", Direcao.SUBIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.POS_FIXADO, "positivo",
            "Historicamente, quando a expectativa de Selic sobe, os títulos "
            "pós-fixados (que rendem um percentual do CDI) passam a pagar "
            "mais na prática para quem já está posicionado neles.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.PRE_FIXADO, "negativo",
            "Títulos prefixados comprados antes tendem a marcar a mercado "
            "para baixo no curto prazo, porque o mercado passa a exigir uma "
            "taxa maior para travar prazos longos.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.BOLSA, "negativo",
            "Juro mais alto encarece o custo de capital das empresas e tende "
            "a competir com a renda variável por atenção do investidor -- "
            "historicamente um vento contrário para a bolsa no curto prazo.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.CAMBIO, "negativo",
            "Um juro doméstico mais alto tende a atrair capital estrangeiro "
            "em busca de retorno, o que historicamente pressiona o real a se "
            "valorizar frente ao dólar e pode reduzir, em reais, o valor de "
            "uma exposição comprada em moeda estrangeira.",
        ),
    ],
    ("Selic", Direcao.CAIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.POS_FIXADO, "negativo",
            "Com a expectativa de Selic caindo, o rendimento de quem já está "
            "posicionado em pós-fixado tende a diminuir.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.PRE_FIXADO, "positivo",
            "Prefixados comprados antes tendem a se valorizar, já que "
            "travaram uma taxa que passa a parecer mais atrativa frente à "
            "nova expectativa mais baixa.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.BOLSA, "positivo",
            "Juro mais baixo reduz o custo de capital das empresas e "
            "historicamente tende a favorecer a renda variável.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.CAMBIO, "positivo",
            "Juro doméstico mais baixo tende a reduzir o atrativo do real "
            "para capital estrangeiro, historicamente pressionando o dólar "
            "para cima e elevando, em reais, o valor de uma exposição "
            "comprada em moeda estrangeira.",
        ),
    ],
    ("IPCA", Direcao.SUBIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.IPCA_MAIS, "neutro",
            "No vencimento, o principal é corrigido pela inflação, mas o "
            "preço do título no curto prazo depende também da taxa real "
            "exigida pelo mercado. Inflação esperada maior, sozinha, não "
            "define se a marcação a mercado sobe ou cai.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.PRE_FIXADO, "negativo",
            "Inflação mais alta corrói o retorno real de quem trava uma taxa "
            "fixa hoje, o que tende a pressionar o preço desses títulos para "
            "baixo.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.BOLSA, "neutro",
            "O efeito na bolsa depende mais de como o Banco Central vai "
            "reagir à inflação (subindo ou não a Selic) do que da inflação "
            "isolada.",
        ),
    ],
    ("IPCA", Direcao.CAIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.IPCA_MAIS, "neutro",
            "Inflação esperada menor reduz a correção projetada do principal "
            "no vencimento, mas o preço no curto prazo depende também da "
            "taxa real exigida pelo mercado. O efeito de marcação a mercado "
            "continua misto.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.PRE_FIXADO, "positivo",
            "Inflação mais baixa preserva melhor o retorno real de quem já "
            "trava uma taxa fixa hoje.",
        ),
    ],
    ("Câmbio", Direcao.SUBIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.CAMBIO, "positivo",
            "Uma expectativa de dólar mais alto favorece diretamente quem já "
            "tem exposição em moeda estrangeira.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.BOLSA, "neutro",
            "Empresas exportadoras tendem a se beneficiar de um dólar mais "
            "alto, enquanto importadoras tendem a sofrer -- o efeito na "
            "bolsa como um todo é misto.",
        ),
    ],
    ("Câmbio", Direcao.CAIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.CAMBIO, "negativo",
            "Uma expectativa de dólar mais baixo reduz o retorno (em reais) "
            "de quem já está posicionado em moeda estrangeira.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.BOLSA, "neutro",
            "Importadoras tendem a se beneficiar de um dólar mais baixo, "
            "enquanto exportadoras tendem a sofrer -- efeito misto na bolsa "
            "como um todo.",
        ),
    ],
    ("PIB Total", Direcao.SUBIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.BOLSA, "positivo",
            "Quando a expectativa de crescimento da economia sobe, as "
            "empresas listadas tendem a faturar e lucrar mais, o que "
            "historicamente favorece a bolsa.",
        ),
    ],
    ("PIB Total", Direcao.CAIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.BOLSA, "negativo",
            "Quando a expectativa de crescimento da economia cai, o "
            "faturamento e os lucros futuros das empresas listadas tendem a "
            "ficar mais fracos, um vento contrário historicamente para a "
            "bolsa.",
        ),
    ],
    ("Dívida líquida do setor público", Direcao.SUBIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.CAMBIO, "positivo",
            "Uma dívida pública maior do que o esperado tende a aumentar a "
            "percepção de risco do país, o que historicamente pressiona o "
            "dólar para cima.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.PRE_FIXADO, "negativo",
            "Mais risco fiscal tende a fazer o mercado exigir uma taxa maior "
            "para financiar o governo por muitos anos, o que pressiona o "
            "preço dos prefixados para baixo.",
        ),
    ],
    ("Dívida líquida do setor público", Direcao.CAIU): [
        EfeitoClasseAtivo(
            ClasseAtivo.CAMBIO, "negativo",
            "Uma dívida pública menor do que o esperado tende a reduzir a "
            "percepção de risco do país, historicamente um alívio para o "
            "dólar.",
        ),
        EfeitoClasseAtivo(
            ClasseAtivo.PRE_FIXADO, "positivo",
            "Menos risco fiscal tende a permitir que o governo se financie "
            "por muitos anos a uma taxa menor, o que favorece o preço dos "
            "prefixados.",
        ),
    ],
}


def limiar_estavel(indicador: str | None = None) -> float:
    if indicador is None:
        return LIMIAR_ESTAVEL_PADRAO
    return LIMIARES_ESTAVEL.get(indicador, LIMIAR_ESTAVEL_PADRAO)


def classificar_direcao(
    delta: float, indicador: str | None = None
) -> Direcao:
    limiar = limiar_estavel(indicador)
    if delta > limiar:
        return Direcao.SUBIU
    if delta < -limiar:
        return Direcao.CAIU
    return Direcao.ESTAVEL


def efeitos_por_indicador(indicador: str, direcao: Direcao) -> list[EfeitoClasseAtivo]:
    return _REGRAS.get((indicador, direcao), [])
