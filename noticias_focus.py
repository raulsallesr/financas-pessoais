"""Cruza temas das manchetes com a mudança mais recente do Focus.

O motor usa somente título e categorias dos feeds. Não lê o corpo das
matérias, não infere recomendação e não depende de rede ou Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass

from financas_taxonomia import Direcao
from focus_data import ComparativoIndicador
from noticias_data import Noticia, normalizar_texto, selecionar_destaques


@dataclass(frozen=True)
class LeituraNoticiasFocus:
    tema: str
    indicador_focus: str
    mencoes: int
    fontes: tuple[str, ...]
    relacao: str
    resumo: str
    destaques: tuple[Noticia, ...]


@dataclass(frozen=True)
class _Tema:
    nome: str
    indicador_focus: str
    termos: tuple[str, ...]
    sinais_alta: tuple[str, ...]
    sinais_baixa: tuple[str, ...]
    leitura_alta: str
    leitura_baixa: str


_TEMAS = (
    _Tema(
        nome="Juros",
        indicador_focus="Selic",
        termos=(
            "selic",
            "copom",
            "juros",
            "taxa basica",
            "politica monetaria",
        ),
        sinais_alta=(
            "selic sobe",
            "alta da selic",
            "alta de juros",
            "juros sobem",
            "eleva juros",
            "aperto monetario",
        ),
        sinais_baixa=(
            "selic cai",
            "queda da selic",
            "corte de juros",
            "juros caem",
            "reduz juros",
            "flexibilizacao monetaria",
        ),
        leitura_alta="juros mais altos",
        leitura_baixa="alívio nos juros",
    ),
    _Tema(
        nome="Inflação",
        indicador_focus="IPCA",
        termos=(
            "ipca",
            "inflacao",
            "precos",
            "cesta basica",
            "alimentos",
            "combustivel",
            "gasolina",
        ),
        sinais_alta=(
            "ipca sobe",
            "inflacao acelera",
            "inflacao alta",
            "precos sobem",
            "alimentos sobem",
            "indice da fao sobe",
            "pressao inflacionaria",
            "eleva expectativa de inflacao",
        ),
        sinais_baixa=(
            "ipca cai",
            "inflacao desacelera",
            "precos caem",
            "alimentos caem",
            "indice da fao cai",
            "deflacao",
            "alivio da inflacao",
            "reduz expectativa de inflacao",
        ),
        leitura_alta="mais pressão sobre os preços",
        leitura_baixa="alívio nos preços",
    ),
    _Tema(
        nome="Câmbio",
        indicador_focus="Câmbio",
        termos=(
            "dolar",
            "cambio",
            "moeda brasileira",
            "real brasileiro",
        ),
        sinais_alta=(
            "dolar sobe",
            "dolar avanca",
            "alta do dolar",
            "real cai",
            "real recua",
            "real desvaloriza",
        ),
        sinais_baixa=(
            "dolar cai",
            "dolar recua",
            "queda do dolar",
            "real sobe",
            "real avanca",
            "real valoriza",
        ),
        leitura_alta="dólar mais pressionado para cima",
        leitura_baixa="dólar com sinal de alívio",
    ),
    _Tema(
        nome="Atividade",
        indicador_focus="PIB Total",
        termos=(
            "pib",
            "atividade economica",
            "economia cresce",
            "producao",
            "emprego",
            "desemprego",
            "varejo",
            "industria",
        ),
        sinais_alta=(
            "pib cresce",
            "atividade avanca",
            "economia cresce",
            "producao sobe",
            "emprego cresce",
            "desemprego cai",
            "vendas crescem",
        ),
        sinais_baixa=(
            "pib cai",
            "atividade recua",
            "economia desacelera",
            "producao cai",
            "emprego cai",
            "desemprego sobe",
            "vendas caem",
        ),
        leitura_alta="atividade mais forte",
        leitura_baixa="atividade mais fraca",
    ),
    _Tema(
        nome="Fiscal",
        indicador_focus="Dívida líquida do setor público",
        termos=(
            "risco fiscal",
            "meta fiscal",
            "resultado fiscal",
            "politica fiscal",
            "divida publica",
            "aumento da divida",
            "deficit primario",
            "superavit primario",
            "gasto publico",
            "contas publicas",
            "orcamento",
            "arcabouco fiscal",
        ),
        sinais_alta=(
            "divida sobe",
            "aumento da divida",
            "deficit aumenta",
            "rombo fiscal",
            "risco fiscal",
            "gasto cresce",
            "piora fiscal",
        ),
        sinais_baixa=(
            "divida cai",
            "deficit cai",
            "superavit",
            "ajuste fiscal",
            "gasto recua",
            "melhora fiscal",
        ),
        leitura_alta="mais pressão fiscal",
        leitura_baixa="alívio fiscal",
    ),
)


def cruzar_noticias_com_focus(
    comparativos: list[ComparativoIndicador],
    noticias: list[Noticia],
    limite_temas: int = 3,
) -> list[LeituraNoticiasFocus]:
    """Prioriza temas multifuente e compara direção editorial com o Focus."""
    if limite_temas <= 0:
        return []

    por_indicador = {
        comparativo.atual.indicador: comparativo
        for comparativo in comparativos
    }
    leituras: list[LeituraNoticiasFocus] = []

    for tema in _TEMAS:
        comparativo = por_indicador.get(tema.indicador_focus)
        if comparativo is None:
            continue
        relacionadas = [
            noticia
            for noticia in noticias
            if _noticia_trata_do_tema(noticia, tema)
        ]
        if not relacionadas:
            continue

        fontes = tuple(sorted({noticia.fonte for noticia in relacionadas}))
        direcao_noticias = _direcao_predominante(relacionadas, tema)
        relacao, resumo = _explicar_relacao(
            tema,
            comparativo.direcao,
            direcao_noticias,
            len(relacionadas),
            len(fontes),
        )
        leituras.append(
            LeituraNoticiasFocus(
                tema=tema.nome,
                indicador_focus=tema.indicador_focus,
                mencoes=len(relacionadas),
                fontes=fontes,
                relacao=relacao,
                resumo=resumo,
                destaques=tuple(
                    selecionar_destaques(relacionadas, limite=3)
                ),
            )
        )

    leituras.sort(
        key=lambda leitura: (
            leitura.relacao != "Sem direção clara",
            len(leitura.fontes),
            leitura.mencoes,
        ),
        reverse=True,
    )
    return leituras[:limite_temas]


def _noticia_trata_do_tema(noticia: Noticia, tema: _Tema) -> bool:
    texto = normalizar_texto(noticia.titulo)
    return any(termo in texto for termo in tema.termos)


def _direcao_predominante(noticias: list[Noticia], tema: _Tema) -> int:
    altas = 0
    baixas = 0
    for noticia in noticias:
        texto = normalizar_texto(noticia.titulo)
        altas += int(any(sinal in texto for sinal in tema.sinais_alta))
        baixas += int(any(sinal in texto for sinal in tema.sinais_baixa))
    if altas == baixas:
        return 0
    return 1 if altas > baixas else -1


def _explicar_relacao(
    tema: _Tema,
    direcao_focus: Direcao,
    direcao_noticias: int,
    mencoes: int,
    quantidade_fontes: int,
) -> tuple[str, str]:
    abertura = (
        f"{mencoes} manchetes em {quantidade_fontes} "
        f"{'fonte' if quantidade_fontes == 1 else 'fontes'} tratam do tema."
    )
    movimento_focus = {
        Direcao.SUBIU: "subiu",
        Direcao.CAIU: "caiu",
        Direcao.ESTAVEL: "ficou estável",
    }[direcao_focus]

    if direcao_noticias == 0:
        return (
            "Sem direção clara",
            f"{abertura} Os títulos não formam uma direção predominante; "
            f"no Focus, {tema.indicador_focus} {movimento_focus}.",
        )

    leitura_editorial = (
        tema.leitura_alta if direcao_noticias > 0 else tema.leitura_baixa
    )
    if direcao_focus is Direcao.ESTAVEL:
        return (
            "Monitorar",
            f"{abertura} Os títulos apontam {leitura_editorial}, enquanto "
            f"{tema.indicador_focus} ficou estável no Focus.",
        )

    direcao_focus_numerica = (
        1 if direcao_focus is Direcao.SUBIU else -1
    )
    if direcao_focus_numerica == direcao_noticias:
        return (
            "Em linha",
            f"{abertura} Os títulos apontam {leitura_editorial} e "
            f"{tema.indicador_focus} {movimento_focus} no Focus: os sinais "
            "seguem na mesma direção.",
        )
    return (
        "Em tensão",
        f"{abertura} Os títulos apontam {leitura_editorial}, mas "
        f"{tema.indicador_focus} {movimento_focus} no Focus: os sinais "
        "seguem em direções diferentes.",
    )
