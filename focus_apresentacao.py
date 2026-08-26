"""Regras puras de apresentação para a página do Boletim Focus."""

from __future__ import annotations

from focus_data import ComparativoIndicador
from financas_taxonomia import Direcao
from focus_semanal import EstadoFocusSemanal, ResumoFocusSemanal
from motor_indicadores import limiar_estavel

ORDEM_INDICADORES = (
    "Selic",
    "IPCA",
    "Câmbio",
    "PIB Total",
    "IGP-M",
    "Dívida líquida do setor público",
)
INDICADORES_PRIORITARIOS = ORDEM_INDICADORES[:3]


def ordenar_comparativos(
    comparativos: list[ComparativoIndicador],
) -> list[ComparativoIndicador]:
    ordem = {indicador: indice for indice, indicador in enumerate(ORDEM_INDICADORES)}
    return sorted(
        comparativos,
        key=lambda comparativo: (
            ordem.get(comparativo.atual.indicador, len(ordem)),
            comparativo.atual.indicador,
        ),
    )


def escolher_destaque(
    comparativos: list[ComparativoIndicador],
) -> ComparativoIndicador:
    """Compara cada delta com o limiar do próprio indicador."""
    if not comparativos:
        raise ValueError("É necessário ao menos um comparativo.")

    com_anterior = [
        comparativo
        for comparativo in comparativos
        if comparativo.anterior is not None
    ]
    candidatas = com_anterior or comparativos
    return max(
        candidatas,
        key=lambda comparativo: (
            abs(comparativo.delta)
            / max(limiar_estavel(comparativo.atual.indicador), 0.0001),
            -ORDEM_INDICADORES.index(comparativo.atual.indicador)
            if comparativo.atual.indicador in ORDEM_INDICADORES
            else -len(ORDEM_INDICADORES),
        ),
    )


def titulo_resumo(comparativos: list[ComparativoIndicador]) -> str:
    if not comparativos:
        return "Ainda não há uma leitura disponível"
    com_anterior = [
        comparativo
        for comparativo in comparativos
        if comparativo.anterior is not None
    ]
    if not com_anterior:
        return "Esta é a primeira fotografia das expectativas"

    mudancas = [
        comparativo
        for comparativo in com_anterior
        if comparativo.direcao != Direcao.ESTAVEL
    ]
    if not mudancas:
        return "Pouca mudança nas expectativas acompanhadas"

    destaque = escolher_destaque(mudancas)
    movimento = (
        "alta" if destaque.direcao == Direcao.SUBIU else "queda"
    )
    return (
        f"{destaque.atual.indicador} concentrou o movimento de "
        f"{movimento} mais relevante"
    )


def titulo_resumo_semanal(resumo: ResumoFocusSemanal) -> str:
    if resumo.estado == EstadoFocusSemanal.INDISPONIVEL:
        return "Focus indisponível no momento"
    if resumo.estado == EstadoFocusSemanal.DEFASADO:
        return "A última fotografia do Focus está defasada"
    if resumo.estado == EstadoFocusSemanal.SEM_MUDANCA_RELEVANTE:
        return "Expectativas seguem praticamente estáveis"
    if resumo.total_comparaveis == 0:
        return "Primeira fotografia das expectativas disponível"

    destaque = resumo.destaques[0]
    movimento = "alta" if destaque.direcao == Direcao.SUBIU else "queda"
    return f"{destaque.atual.indicador} liderou as revisões de {movimento}"


def descricao_resumo_semanal(resumo: ResumoFocusSemanal) -> str:
    if resumo.estado == EstadoFocusSemanal.INDISPONIVEL:
        return (
            "Ainda não existe uma fotografia íntegra salva. Atualize os "
            "dados para consultar as expectativas do Banco Central."
        )
    if resumo.estado == EstadoFocusSemanal.DEFASADO:
        data = resumo.data_mais_recente.strftime("%d/%m/%Y")
        return (
            f"A coleta disponível é de {data} e tem "
            f"{resumo.dias_uteis} dias úteis. Os números permanecem "
            "visíveis, mas não representam uma leitura atual."
        )
    if resumo.estado == EstadoFocusSemanal.SEM_MUDANCA_RELEVANTE:
        return (
            f"Os {resumo.total_comparaveis} indicadores comparáveis "
            "ficaram dentro do limiar de estabilidade definido para cada "
            "série."
        )
    if resumo.total_comparaveis == 0:
        return (
            "Ainda não há uma leitura anterior da mesma referência; por "
            "isso não calculamos variação."
        )
    return (
        f"{resumo.total_relevantes} de {resumo.total_comparaveis} "
        "indicadores comparáveis ultrapassaram o próprio limiar de "
        "estabilidade."
    )


def formatar_numero(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_valor(comparativo: ComparativoIndicador) -> str:
    valor = formatar_numero(comparativo.atual.mediana)
    if comparativo.atual.indicador == "Câmbio":
        return f"R$ {valor}"
    if comparativo.atual.indicador == "Dívida líquida do setor público":
        return f"{valor}% do PIB"
    return f"{valor}%"


def formatar_delta(comparativo: ComparativoIndicador) -> str:
    if comparativo.anterior is None:
        return "Primeira leitura"
    sinal = "+" if comparativo.delta > 0 else ""
    valor = formatar_numero(comparativo.delta)
    data_anterior = comparativo.anterior.data_coleta.strftime("%d/%m")
    if comparativo.atual.indicador == "Câmbio":
        return f"{sinal}R$ {valor} desde {data_anterior}"
    return f"{sinal}{valor} p.p. desde {data_anterior}"
