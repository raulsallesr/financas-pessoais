"""Análise lexical conservadora de uma matéria já extraída.

O módulo não faz I/O e não guarda o corpo editorial no resultado. Ele
identifica sinais verificáveis no texto, relaciona-os à última mudança do
Focus e deixa explícitos os limites da automação.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from focuslens.adapters.noticias_artigo import ArtigoExtraido
from focuslens.core.financas_taxonomia import Direcao
from focuslens.core.focus_data import ComparativoIndicador
from focuslens.core.noticias_data import Noticia, normalizar_texto


@dataclass(frozen=True)
class ConexaoFocus:
    tema: str
    indicador_focus: str
    relacao: str
    explicacao: str


@dataclass(frozen=True)
class EvidenciaNumerica:
    valor: str
    contexto: str


@dataclass(frozen=True)
class AnaliseArtigo:
    noticia: Noticia
    origem: str
    palavras_lidas: int
    temas: tuple[str, ...]
    sintese: str
    conexoes: tuple[ConexaoFocus, ...]
    numeros: tuple[EvidenciaNumerica, ...]
    instituicoes: tuple[str, ...]
    onde_olhar: tuple[str, ...]
    trecho_verificacao: str
    limitacao: str


@dataclass(frozen=True)
class _Tema:
    nome: str
    indicador_focus: str
    termos: tuple[str, ...]
    sinais_alta: tuple[str, ...]
    sinais_baixa: tuple[str, ...]
    leitura_alta: str
    leitura_baixa: str
    onde_olhar: tuple[str, ...]


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
            "tesouro direto",
            "tesouro ipca",
            "renda fixa",
        ),
        sinais_alta=(
            "alta de juros",
            "juros mais altos",
            "eleva juros",
            "aperto monetario",
            "taxa sobe",
        ),
        sinais_baixa=(
            "corte de juros",
            "queda de juros",
            "reduz juros",
            "flexibilizacao monetaria",
            "taxa cai",
        ),
        leitura_alta="pressão de alta nos juros",
        leitura_baixa="alívio nos juros",
        onde_olhar=(
            "Próxima decisão e comunicado do Copom",
            "Revisões da Selic no próximo Focus",
            "Juros reais dos títulos públicos",
        ),
    ),
    _Tema(
        nome="Inflação",
        indicador_focus="IPCA",
        termos=(
            "ipca",
            "inflacao",
            "precos",
            "alimentos",
            "combustivel",
            "gasolina",
            "indice da fao",
            "tesouro ipca",
        ),
        sinais_alta=(
            "inflacao acelera",
            "inflacao alta",
            "precos sobem",
            "indice da fao sobe",
            "pressao inflacionaria",
            "aceleracao dos precos",
        ),
        sinais_baixa=(
            "inflacao desacelera",
            "precos caem",
            "indice da fao cai",
            "alivio da inflacao",
            "desaceleracao dos precos",
            "deflacao",
        ),
        leitura_alta="pressão de alta nos preços",
        leitura_baixa="alívio nos preços",
        onde_olhar=(
            "Próximas leituras de IPCA e IPCA-15",
            "Preços de alimentos, energia e combustíveis",
            "Revisões do IPCA no próximo Focus",
        ),
    ),
    _Tema(
        nome="Fiscal",
        indicador_focus="Dívida líquida do setor público",
        termos=(
            "divida publica",
            "divida bruta",
            "divida liquida",
            "resultado primario",
            "deficit",
            "superavit",
            "gasto publico",
            "contas publicas",
            "risco fiscal",
            "meta fiscal",
            "orcamento",
        ),
        sinais_alta=(
            "aumento da divida",
            "divida sobe",
            "divida publica sobe",
            "divida bruta sobe",
            "divida liquida sobe",
            "deficit aumenta",
            "risco fiscal",
            "piora fiscal",
            "gasto cresce",
        ),
        sinais_baixa=(
            "queda da divida",
            "divida cai",
            "divida publica cai",
            "divida bruta cai",
            "divida liquida cai",
            "deficit cai",
            "superavit",
            "ajuste fiscal",
            "melhora fiscal",
        ),
        leitura_alta="mais pressão fiscal",
        leitura_baixa="alívio fiscal",
        onde_olhar=(
            "Dívida pública como proporção do PIB",
            "Resultado primário e cumprimento da meta fiscal",
            "Reação dos juros longos às contas públicas",
        ),
    ),
    _Tema(
        nome="Câmbio",
        indicador_focus="Câmbio",
        termos=(
            "dolar",
            "cambio",
            "real brasileiro",
            "moeda brasileira",
        ),
        sinais_alta=(
            "dolar sobe",
            "dolar avanca",
            "alta do dolar",
            "real desvaloriza",
            "real recua",
        ),
        sinais_baixa=(
            "dolar cai",
            "dolar recua",
            "queda do dolar",
            "real valoriza",
            "real avanca",
        ),
        leitura_alta="pressão de alta no dólar",
        leitura_baixa="alívio no dólar",
        onde_olhar=(
            "PTAX e volatilidade do real",
            "Diferencial de juros Brasil–exterior",
            "Commodities e percepção de risco externo",
        ),
    ),
    _Tema(
        nome="Atividade",
        indicador_focus="PIB Total",
        termos=(
            "pib",
            "atividade economica",
            "producao",
            "emprego",
            "desemprego",
            "varejo",
            "industria",
            "crescimento economico",
        ),
        sinais_alta=(
            "pib cresce",
            "atividade avanca",
            "economia cresce",
            "producao sobe",
            "emprego cresce",
            "desemprego cai",
        ),
        sinais_baixa=(
            "pib cai",
            "atividade recua",
            "economia desacelera",
            "producao cai",
            "emprego cai",
            "desemprego sobe",
        ),
        leitura_alta="atividade mais forte",
        leitura_baixa="atividade mais fraca",
        onde_olhar=(
            "Próximas leituras de PIB e IBC-Br",
            "Emprego, varejo e produção industrial",
            "Revisões do PIB no próximo Focus",
        ),
    ),
)

_INSTITUICOES = (
    (
        "Banco Central do Brasil",
        ("banco central do brasil", "banco central", "bcb", "bc"),
    ),
    ("Copom", ("copom",)),
    ("IBGE", ("ibge",)),
    ("Tesouro Nacional", ("tesouro nacional", "tesouro direto")),
    (
        "Ministério da Fazenda",
        ("ministerio da fazenda", "ministro da fazenda"),
    ),
    ("FAO", ("fao",)),
    ("FMI", ("fmi", "fundo monetario internacional")),
    ("Federal Reserve", ("federal reserve", "fed")),
)

_PADRAO_NUMERO = re.compile(
    r"""
    (?:
        R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d+)?
        (?:
            \s*(?:
                trilh(?:ão|ões|ao|oes)
                |bilh(?:ão|ões|ao|oes)
                |milh(?:ão|ões|ao|oes)
            )
        )?
        |
        \d{1,3}(?:\.\d{3})*(?:,\d+)?\s*
        (?:
            %|p\.p\.|ponto(?:s)?\s+percentual(?:is)?
            |trilh(?:ão|ões|ao|oes)
            |bilh(?:ão|ões|ao|oes)
            |milh(?:ão|ões|ao|oes)
        )
    )
    """,
    flags=re.IGNORECASE | re.VERBOSE,
)

_CORES_RELACAO = {
    "Em linha",
    "Em tensão",
    "Monitorar",
    "Sem direção clara",
}


def analisar_artigo(
    artigo: ArtigoExtraido,
    comparativos: list[ComparativoIndicador],
) -> AnaliseArtigo:
    """Resume sinais auditáveis sem devolver nem persistir o texto integral."""
    texto_normalizado = normalizar_texto(artigo.texto)
    temas_pontuados = [
        (tema, _pontuar_tema(texto_normalizado, tema))
        for tema in _TEMAS
    ]
    temas_pontuados = [
        item for item in temas_pontuados if item[1] > 0
    ]
    temas_pontuados.sort(key=lambda item: item[1], reverse=True)
    temas = [tema for tema, _ in temas_pontuados[:3]]
    conexoes = tuple(
        _conectar_focus(tema, texto_normalizado, comparativos)
        for tema in temas
    )

    if temas:
        nomes = _listar_naturalmente([tema.nome for tema in temas])
        direcionais = [
            conexao.explicacao
            for conexao in conexoes
            if conexao.relacao != "Sem direção clara"
        ]
        detalhe = (
            f" O sinal mais útil para comparação é: {direcionais[0]}"
            if direcionais
            else " O texto é principalmente contextual, sem direção inequívoca."
        )
        sintese = (
            f"A matéria concentra-se em {nomes}.{detalhe}"
        )
    else:
        sintese = (
            "A matéria traz contexto econômico, mas não contém sinais "
            "suficientes para ligá-la com segurança aos indicadores do Focus."
        )

    return AnaliseArtigo(
        noticia=artigo.noticia,
        origem=artigo.origem,
        palavras_lidas=artigo.palavras,
        temas=tuple(tema.nome for tema in temas),
        sintese=sintese,
        conexoes=conexoes,
        numeros=_extrair_numeros(artigo, temas),
        instituicoes=_detectar_instituicoes(texto_normalizado),
        onde_olhar=_montar_onde_olhar(temas),
        trecho_verificacao=artigo.trecho_verificacao,
        limitacao=(
            "Leitura automatizada por termos e contexto. Ela ajuda a localizar "
            "sinais, mas não substitui a matéria nem atribui intenção ao autor."
        ),
    )


def _pontuar_tema(texto: str, tema: _Tema) -> int:
    return sum(texto.count(termo) for termo in tema.termos)


def _conectar_focus(
    tema: _Tema,
    texto: str,
    comparativos: list[ComparativoIndicador],
) -> ConexaoFocus:
    direcao_texto = _direcao_texto(texto, tema)
    comparativo = next(
        (
            item
            for item in comparativos
            if item.atual.indicador == tema.indicador_focus
        ),
        None,
    )
    if comparativo is None:
        return ConexaoFocus(
            tema=tema.nome,
            indicador_focus=tema.indicador_focus,
            relacao="Sem direção clara",
            explicacao=(
                f"O texto trata de {tema.nome.lower()}, mas não há uma "
                f"leitura comparável de {tema.indicador_focus} no Focus."
            ),
        )

    movimento_focus = {
        Direcao.SUBIU: "subiu",
        Direcao.CAIU: "caiu",
        Direcao.ESTAVEL: "ficou estável",
    }[comparativo.direcao]
    if direcao_texto == 0:
        return ConexaoFocus(
            tema=tema.nome,
            indicador_focus=tema.indicador_focus,
            relacao="Sem direção clara",
            explicacao=(
                f"A matéria dá contexto a {tema.nome.lower()}, sem formar "
                f"uma direção predominante; no Focus, "
                f"{tema.indicador_focus} {movimento_focus}."
            ),
        )

    leitura = tema.leitura_alta if direcao_texto > 0 else tema.leitura_baixa
    if comparativo.direcao is Direcao.ESTAVEL:
        relacao = "Monitorar"
        explicacao = (
            f"A matéria sinaliza {leitura}, enquanto "
            f"{tema.indicador_focus} ficou estável no Focus."
        )
    else:
        direcao_focus = (
            1 if comparativo.direcao is Direcao.SUBIU else -1
        )
        relacao = (
            "Em linha" if direcao_focus == direcao_texto else "Em tensão"
        )
        ligacao = "e" if relacao == "Em linha" else "mas"
        explicacao = (
            f"A matéria sinaliza {leitura} {ligacao} "
            f"{tema.indicador_focus} {movimento_focus} no Focus."
        )
    assert relacao in _CORES_RELACAO
    return ConexaoFocus(
        tema=tema.nome,
        indicador_focus=tema.indicador_focus,
        relacao=relacao,
        explicacao=explicacao,
    )


def _direcao_texto(texto: str, tema: _Tema) -> int:
    altas = sum(texto.count(sinal) for sinal in tema.sinais_alta)
    baixas = sum(texto.count(sinal) for sinal in tema.sinais_baixa)
    if altas == baixas:
        return 0
    return 1 if altas > baixas else -1


def _extrair_numeros(
    artigo: ArtigoExtraido,
    temas: list[_Tema],
) -> tuple[EvidenciaNumerica, ...]:
    evidencias: list[EvidenciaNumerica] = []
    vistos: set[str] = set()
    for paragrafo in artigo.paragrafos:
        for correspondencia in _PADRAO_NUMERO.finditer(paragrafo):
            valor = re.sub(r"\s+", " ", correspondencia.group()).strip()
            chave = normalizar_texto(valor)
            if chave in vistos:
                continue
            vistos.add(chave)
            evidencias.append(
                EvidenciaNumerica(
                    valor=valor,
                    contexto=_contexto_numero(
                        paragrafo,
                        correspondencia.group(),
                        temas,
                    ),
                )
            )
            if len(evidencias) == 8:
                return tuple(evidencias)
    return tuple(evidencias)


def _contexto_numero(
    paragrafo: str,
    valor: str,
    temas: list[_Tema],
) -> str:
    sentencas = re.split(r"(?<=[.!?])\s+", paragrafo)
    sentenca = next(
        (item for item in sentencas if valor in item),
        paragrafo,
    )
    texto = normalizar_texto(sentenca)
    pontuadas = [
        (tema, _pontuar_tema(texto, tema))
        for tema in temas
    ]
    pontuadas.sort(key=lambda item: item[1], reverse=True)
    if pontuadas and pontuadas[0][1] > 0:
        return pontuadas[0][0].nome
    return "Contexto geral"


def _detectar_instituicoes(texto: str) -> tuple[str, ...]:
    return tuple(
        nome
        for nome, termos in _INSTITUICOES
        if any(_contem_termo(texto, termo) for termo in termos)
    )


def _contem_termo(texto: str, termo: str) -> bool:
    return bool(re.search(rf"\b{re.escape(termo)}\b", texto))


def _montar_onde_olhar(temas: list[_Tema]) -> tuple[str, ...]:
    itens: list[str] = []
    for tema in temas:
        for item in tema.onde_olhar:
            if item not in itens:
                itens.append(item)
            if len(itens) == 5:
                return tuple(itens)
    return tuple(itens)


def _listar_naturalmente(itens: list[str]) -> str:
    if len(itens) <= 1:
        return "".join(itens)
    return ", ".join(itens[:-1]) + f" e {itens[-1]}"
