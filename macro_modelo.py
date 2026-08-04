"""Motor macro explicável baseado em sinais públicos e regras condicionais.

Não produz recomendação personalizada nem alvo de preço. A saída descreve
um cenário-base, seus sinais, possíveis efeitos e condições de invalidação.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from financas_taxonomia import Direcao
from focus_data import ComparativoIndicador
from mercado_data import MovimentoMercado, SerieMercado, calcular_movimento
from noticias_data import Noticia, normalizar_texto


@dataclass(frozen=True)
class SinalMacro:
    eixo: str
    impacto: int
    titulo: str
    evidencia: str
    fonte: str


@dataclass(frozen=True)
class EixoMacro:
    codigo: str
    nome: str
    saldo: int
    leitura: str
    evidencias: tuple[str, ...]


@dataclass(frozen=True)
class PerspectivaClasse:
    classe: str
    estado: str
    explicacao: str


@dataclass(frozen=True)
class TemaEditorial:
    tema: str
    ocorrencias: int


@dataclass(frozen=True)
class CenarioMacro:
    titulo: str
    horizonte: str
    confianca: str
    resumo: str
    projecoes: tuple[str, ...]
    eixos: tuple[EixoMacro, ...]
    perspectivas: tuple[PerspectivaClasse, ...]
    invalidadores: tuple[str, ...]
    temas_editoriais: tuple[TemaEditorial, ...]
    sinais: tuple[SinalMacro, ...]


_TERMOS_TEMAS = {
    "Inflação": ("inflacao", "ipca", "precos"),
    "Juros": ("juros", "selic", "copom", "taxa"),
    "Fiscal": ("fiscal", "divida", "orcamento", "gasto publico"),
    "Atividade": ("pib", "atividade", "emprego", "industria", "varejo"),
    "Exterior": ("fed", "eua", "china", "dolar", "tarifa"),
    "Commodities": ("petroleo", "brent", "opep", "commodity"),
    "Cripto": ("bitcoin", "cripto", "btc"),
}


def _numero_pt(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def extrair_temas_editoriais(
    noticias: list[Noticia],
    *,
    limite: int = 4,
) -> tuple[TemaEditorial, ...]:
    contagens: dict[str, int] = {}
    for noticia in noticias:
        texto = normalizar_texto(
            " ".join((noticia.titulo, *noticia.categorias))
        )
        for tema, termos in _TERMOS_TEMAS.items():
            if any(termo in texto for termo in termos):
                contagens[tema] = contagens.get(tema, 0) + 1
    ordenados = sorted(
        contagens.items(),
        key=lambda item: (-item[1], item[0]),
    )
    return tuple(
        TemaEditorial(tema=tema, ocorrencias=ocorrencias)
        for tema, ocorrencias in ordenados[:limite]
    )


def _sinais_focus(
    comparativos: list[ComparativoIndicador],
) -> list[SinalMacro]:
    mapa = {
        comparativo.atual.indicador: comparativo
        for comparativo in comparativos
    }
    sinais: list[SinalMacro] = []

    def adicionar_direcao(
        indicador: str,
        eixo: str,
        peso: int,
        alta: str,
        queda: str,
    ) -> None:
        comparativo = mapa.get(indicador)
        if comparativo is None or comparativo.anterior is None:
            return
        if comparativo.direcao == Direcao.ESTAVEL:
            return
        subiu = comparativo.direcao == Direcao.SUBIU
        sinais.append(
            SinalMacro(
                eixo=eixo,
                impacto=peso if subiu else -peso,
                titulo=alta if subiu else queda,
                evidencia=(
                    f"{indicador}: {_numero_pt(comparativo.anterior.mediana)} "
                    f"→ {_numero_pt(comparativo.atual.mediana)}."
                ),
                fonte="Boletim Focus / BACEN",
            )
        )

    adicionar_direcao(
        "IPCA",
        "inflacao",
        2,
        "Inflação esperada ganhou pressão",
        "Inflação esperada perdeu pressão",
    )
    adicionar_direcao(
        "Câmbio",
        "inflacao",
        1,
        "Câmbio esperado adicionou pressão",
        "Câmbio esperado trouxe alívio",
    )
    adicionar_direcao(
        "Selic",
        "monetario",
        1,
        "Expectativa de juros subiu",
        "Expectativa de juros caiu",
    )
    adicionar_direcao(
        "PIB Total",
        "atividade",
        2,
        "Atividade esperada ganhou força",
        "Atividade esperada perdeu força",
    )
    adicionar_direcao(
        "Dívida líquida do setor público",
        "fiscal",
        2,
        "Risco fiscal esperado aumentou",
        "Risco fiscal esperado diminuiu",
    )

    selic = mapa.get("Selic")
    if selic is not None:
        nivel = selic.atual.mediana
        if nivel >= 10:
            sinais.append(
                SinalMacro(
                    eixo="monetario",
                    impacto=2,
                    titulo="Nível de juros segue restritivo",
                    evidencia=f"Mediana da Selic em {_numero_pt(nivel)}%.",
                    fonte="Boletim Focus / BACEN",
                )
            )
    return sinais


def _sinais_mercado(
    movimentos: list[MovimentoMercado],
) -> list[SinalMacro]:
    mapa = {movimento.codigo: movimento for movimento in movimentos}
    sinais: list[SinalMacro] = []
    dolar = mapa.get("USDBRL")
    if dolar and dolar.variacao_30d is not None:
        if dolar.variacao_30d >= 2:
            sinais.append(
                SinalMacro(
                    eixo="risco",
                    impacto=1,
                    titulo="Dólar sinaliza maior cautela",
                    evidencia=(
                        f"PTAX variou {dolar.variacao_30d:+.2f}% em 30 dias."
                    ),
                    fonte="PTAX / BACEN",
                )
            )
        elif dolar.variacao_30d <= -2:
            sinais.append(
                SinalMacro(
                    eixo="risco",
                    impacto=-1,
                    titulo="Dólar sinaliza menor aversão",
                    evidencia=(
                        f"PTAX variou {dolar.variacao_30d:+.2f}% em 30 dias."
                    ),
                    fonte="PTAX / BACEN",
                )
            )

    brent = mapa.get("BRENT")
    if brent and brent.variacao_30d is not None:
        if brent.variacao_30d >= 5:
            sinais.append(
                SinalMacro(
                    eixo="inflacao",
                    impacto=1,
                    titulo="Petróleo adiciona pressão de custos",
                    evidencia=(
                        f"Brent variou {brent.variacao_30d:+.2f}% em 30 dias."
                    ),
                    fonte="EIA via FRED",
                )
            )
        elif brent.variacao_30d <= -5:
            sinais.append(
                SinalMacro(
                    eixo="inflacao",
                    impacto=-1,
                    titulo="Petróleo traz alívio de custos",
                    evidencia=(
                        f"Brent variou {brent.variacao_30d:+.2f}% em 30 dias."
                    ),
                    fonte="EIA via FRED",
                )
            )

    bitcoin = mapa.get("BTCBRL")
    if bitcoin and bitcoin.variacao_30d is not None:
        if bitcoin.variacao_30d >= 10:
            sinais.append(
                SinalMacro(
                    eixo="risco",
                    impacto=-1,
                    titulo="Bitcoin indica maior apetite a risco",
                    evidencia=(
                        f"BTC/BRL variou "
                        f"{bitcoin.variacao_30d:+.2f}% em 30 dias."
                    ),
                    fonte="Binance",
                )
            )
        elif bitcoin.variacao_30d <= -10:
            sinais.append(
                SinalMacro(
                    eixo="risco",
                    impacto=1,
                    titulo="Bitcoin indica menor apetite a risco",
                    evidencia=(
                        f"BTC/BRL variou "
                        f"{bitcoin.variacao_30d:+.2f}% em 30 dias."
                    ),
                    fonte="Binance",
                )
            )
    return sinais


def _montar_eixos(sinais: list[SinalMacro]) -> tuple[EixoMacro, ...]:
    configuracao = (
        ("inflacao", "Inflação e custos"),
        ("monetario", "Condições monetárias"),
        ("atividade", "Atividade econômica"),
        ("fiscal", "Risco fiscal"),
        ("risco", "Apetite a risco"),
    )
    eixos: list[EixoMacro] = []
    for codigo, nome in configuracao:
        sinais_eixo = [sinal for sinal in sinais if sinal.eixo == codigo]
        saldo = sum(sinal.impacto for sinal in sinais_eixo)
        if codigo == "atividade":
            leitura = (
                "ganhando força"
                if saldo >= 2
                else "perdendo força"
                if saldo <= -2
                else "sem direção forte"
            )
        elif codigo == "risco":
            leitura = (
                "mais cautela"
                if saldo >= 1
                else "mais apetite"
                if saldo <= -1
                else "equilibrado"
            )
        else:
            leitura = (
                "pressão"
                if saldo >= 1
                else "alívio"
                if saldo <= -1
                else "neutro"
            )
        eixos.append(
            EixoMacro(
                codigo=codigo,
                nome=nome,
                saldo=saldo,
                leitura=leitura,
                evidencias=tuple(
                    f"{sinal.evidencia} · {sinal.fonte}"
                    for sinal in sinais_eixo
                ),
            )
        )
    return tuple(eixos)


def _perspectivas(
    eixos: tuple[EixoMacro, ...],
    movimentos: list[MovimentoMercado],
) -> tuple[PerspectivaClasse, ...]:
    saldos = {eixo.codigo: eixo.saldo for eixo in eixos}
    movimento = {item.codigo: item for item in movimentos}
    monetario = saldos.get("monetario", 0)
    inflacao = saldos.get("inflacao", 0)
    atividade = saldos.get("atividade", 0)
    fiscal = saldos.get("fiscal", 0)
    risco = saldos.get("risco", 0)

    pontuacoes = {
        "Pós-fixados": monetario,
        "Prefixados longos": -monetario - inflacao - fiscal,
        "Fundos imobiliários / FIAGRO": -monetario,
        "Bolsa brasileira": atividade - monetario - risco,
        "Dólar": risco + fiscal,
        "Commodities / energia": atividade + (
            1
            if movimento.get("BRENT")
            and movimento["BRENT"].direcao == "alta"
            else -1
            if movimento.get("BRENT")
            and movimento["BRENT"].direcao == "queda"
            else 0
        ),
        "Bitcoin": -risco,
    }
    explicacoes = {
        "Pós-fixados": (
            "Juros elevados sustentam o carrego, mas esse vento diminui se "
            "a expectativa de Selic começar a cair."
        ),
        "Prefixados longos": (
            "Inflação, juros e risco fiscal maiores elevam a taxa exigida e "
            "podem pressionar preços no curto prazo."
        ),
        "Fundos imobiliários / FIAGRO": (
            "Juros altos elevam a taxa de desconto e competem com os "
            "rendimentos distribuídos. Imóveis, recebíveis e FIAGROs reagem "
            "de formas diferentes a inflação, crédito e commodities, então "
            "esta é apenas uma leitura agregada."
        ),
        "Bolsa brasileira": (
            "Atividade ajuda, enquanto juros altos e aversão a risco pesam "
            "sobre custo de capital e múltiplos."
        ),
        "Dólar": (
            "Aversão a risco e preocupação fiscal tendem a sustentar a moeda; "
            "a reversão desses sinais pode retirar esse suporte."
        ),
        "Commodities / energia": (
            "O movimento do Brent e a força da atividade global importam mais "
            "do que um único indicador doméstico."
        ),
        "Bitcoin": (
            "É um ativo de alta volatilidade e costuma reagir ao apetite a "
            "risco; a direção recente não garante continuidade."
        ),
    }

    resultado = []
    for classe, pontuacao in pontuacoes.items():
        estado = (
            "vento favorável"
            if pontuacao >= 2
            else "mais pressionado"
            if pontuacao <= -2
            else "cenário misto"
        )
        resultado.append(
            PerspectivaClasse(
                classe=classe,
                estado=estado,
                explicacao=explicacoes[classe],
            )
        )
    resultado.append(
        PerspectivaClasse(
            classe="Títulos IPCA+",
            estado="proteção com ressalvas",
            explicacao=(
                "A correção pela inflação atua no vencimento, mas juros reais "
                "e marcação a mercado podem dominar o preço no curto prazo."
            ),
        )
    )
    return tuple(resultado)


def construir_cenario(
    comparativos: list[ComparativoIndicador],
    series: list[SerieMercado],
    noticias: list[Noticia],
    *,
    hoje: date | None = None,
) -> CenarioMacro:
    data_referencia = hoje or date.today()
    tolerancia_dias = {"USDBRL": 7, "BRENT": 14, "BTCBRL": 2}
    movimentos = [
        calcular_movimento(serie)
        for serie in series
        if serie.pontos
        and (
            data_referencia - serie.pontos[-1].data
        ).days <= tolerancia_dias.get(serie.codigo, 7)
    ]
    sinais = _sinais_focus(comparativos) + _sinais_mercado(movimentos)
    eixos = _montar_eixos(sinais)
    saldos = {eixo.codigo: eixo.saldo for eixo in eixos}
    inflacao = saldos["inflacao"]
    monetario = saldos["monetario"]
    atividade = saldos["atividade"]
    risco = saldos["risco"]

    if monetario >= 2 and inflacao >= 1:
        titulo = "Juros altos com pressão inflacionária"
        resumo = (
            "O cenário-base mantém condições financeiras apertadas. "
            "Inflação, câmbio e custos precisam aliviar de forma consistente "
            "antes de uma mudança mais confortável no ciclo de juros."
        )
    elif monetario >= 2 and inflacao <= 0:
        titulo = "Juros altos, mas inflação sem aceleração clara"
        resumo = (
            "As condições monetárias continuam restritivas, enquanto os "
            "sinais de preços não apontam pressão sincronizada."
        )
    elif atividade <= -2:
        titulo = "Atividade perdendo força"
        resumo = (
            "A desaceleração esperada ganha peso no cenário e aumenta a "
            "sensibilidade dos ativos a qualquer surpresa de inflação."
        )
    elif risco >= 1:
        titulo = "Cautela com risco ganhou espaço"
        resumo = (
            "Dólar e ativos de maior volatilidade sugerem postura mais "
            "defensiva do mercado, ainda sem formar uma previsão fechada."
        )
    else:
        titulo = "Cenário macro ainda misto"
        resumo = (
            "Os sinais disponíveis não apontam uma única direção dominante. "
            "O melhor diagnóstico é acompanhar as condições que destravam "
            "ou deterioram cada cenário."
        )

    projecoes: list[str] = []
    if monetario >= 2:
        projecoes.append(
            "Nas próximas 4–12 semanas, o cenário-base mantém juros "
            "restritivos enquanto inflação e expectativas não cederem."
        )
    elif monetario <= -1:
        projecoes.append(
            "A continuidade do alívio de juros depende de inflação e câmbio "
            "confirmarem a mesma direção."
        )
    if inflacao >= 1:
        projecoes.append(
            "Pressão de preços reduz o espaço para flexibilização monetária "
            "e mantém ativos longos mais sensíveis."
        )
    elif inflacao <= -1:
        projecoes.append(
            "Alívio de preços abre espaço para condições financeiras menos "
            "apertadas, desde que o fiscal não piore."
        )
    if atividade >= 2:
        projecoes.append(
            "Atividade mais firme ajuda receitas, mas também pode prolongar "
            "a cautela com inflação e juros."
        )
    elif atividade <= -2:
        projecoes.append(
            "Atividade mais fraca tende a pressionar resultados cíclicos e "
            "pode aumentar a discussão sobre queda de juros."
        )
    if not projecoes:
        projecoes.append(
            "Sem direção dominante, mudanças sincronizadas em inflação, "
            "juros e dólar são o principal gatilho a observar."
        )

    invalidadores = (
        "IPCA esperado e dólar mudarem de direção por mais de uma coleta.",
        "A expectativa de Selic romper o padrão atual de forma consistente.",
        "Dólar, Brent ou Bitcoin mudarem de direção além dos limiares do motor.",
    )
    confianca = (
        "moderada"
        if len(comparativos) >= 3
        and len(movimentos) >= 2
        and any(abs(eixo.saldo) >= 2 for eixo in eixos)
        else "baixa"
    )
    return CenarioMacro(
        titulo=titulo,
        horizonte="4–12 semanas",
        confianca=confianca,
        resumo=resumo,
        projecoes=tuple(projecoes[:3]),
        eixos=eixos,
        perspectivas=_perspectivas(eixos, movimentos),
        invalidadores=invalidadores,
        temas_editoriais=extrair_temas_editoriais(noticias),
        sinais=tuple(sinais),
    )
