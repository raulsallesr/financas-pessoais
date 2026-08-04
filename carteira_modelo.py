"""Cálculos puros para a carteira pessoal, isolados da camada visual.

O módulo cruza valores informados na sessão com a leitura macro já produzida.
Ele descreve exposição, resultado e contexto; não gera ordem de compra/venda.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Iterable, Mapping

from macro_modelo import CenarioMacro
from mercado_data import SerieMercado, pontos_base_100


CLASSES_CARTEIRA = (
    "Renda fixa pós-fixada",
    "Renda fixa prefixada",
    "Títulos IPCA+",
    "Bolsa brasileira",
    "Exterior / dólar",
    "Commodities / energia",
    "Bitcoin / cripto",
    "Outros",
)

BENCHMARKS = (
    "Sem comparação",
    "CDI",
    "Selic",
    "Dólar PTAX",
    "Petróleo Brent",
    "Bitcoin",
)

_CODIGO_BENCHMARK = {
    "CDI": "CDI",
    "Selic": "SELIC",
    "Dólar PTAX": "USDBRL",
    "Petróleo Brent": "BRENT",
    "Bitcoin": "BTCBRL",
}

_PERSPECTIVA_POR_CLASSE = {
    "Renda fixa pós-fixada": "Pós-fixados",
    "Renda fixa prefixada": "Prefixados longos",
    "Títulos IPCA+": "Títulos IPCA+",
    "Bolsa brasileira": "Bolsa brasileira",
    "Exterior / dólar": "Dólar",
    "Commodities / energia": "Commodities / energia",
    "Bitcoin / cripto": "Bitcoin",
}


@dataclass(frozen=True)
class PosicaoCarteira:
    ativo: str
    classe: str
    valor_atual: float
    valor_investido: float | None = None
    benchmark: str = "Sem comparação"

    @property
    def resultado(self) -> float | None:
        if self.valor_investido is None:
            return None
        return self.valor_atual - self.valor_investido

    @property
    def retorno_percentual(self) -> float | None:
        if not self.valor_investido:
            return None
        return ((self.valor_atual / self.valor_investido) - 1) * 100


@dataclass(frozen=True)
class ResumoCarteira:
    total_atual: float
    quantidade_posicoes: int
    maior_concentracao_percentual: float
    valor_investido_conhecido: float
    resultado_conhecido: float | None
    retorno_conhecido_percentual: float | None
    alocacao_por_classe: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class ImpactoClasseCarteira:
    classe: str
    valor_atual: float
    peso_percentual: float
    estado: str
    explicacao: str


@dataclass(frozen=True)
class ComparacaoPosicao:
    ativo: str
    benchmark: str
    retorno_posicao_percentual: float | None
    retorno_benchmark_percentual: float


def _numero_positivo_ou_zero(valor: Any) -> float | None:
    if valor is None or (
        isinstance(valor, str) and not valor.strip()
    ):
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if not isfinite(numero) or numero < 0:
        return None
    return numero


def _texto(valor: Any) -> str:
    if valor is None:
        return ""
    texto = str(valor).strip()
    return "" if texto.casefold() in {"nan", "<na>", "none"} else texto


def montar_posicoes(
    registros: Iterable[Mapping[str, Any]],
) -> tuple[PosicaoCarteira, ...]:
    """Normaliza linhas do editor e ignora linhas vazias ou sem valor."""
    posicoes: list[PosicaoCarteira] = []
    for registro in registros:
        ativo = _texto(registro.get("Ativo"))
        valor_atual = _numero_positivo_ou_zero(
            registro.get("Valor atual (R$)")
        )
        if not ativo or valor_atual is None or valor_atual <= 0:
            continue

        classe = _texto(registro.get("Classe")) or CLASSES_CARTEIRA[-1]
        if classe not in CLASSES_CARTEIRA:
            classe = CLASSES_CARTEIRA[-1]

        benchmark = _texto(registro.get("Comparar com")) or BENCHMARKS[0]
        if benchmark not in BENCHMARKS:
            benchmark = BENCHMARKS[0]

        valor_investido = _numero_positivo_ou_zero(
            registro.get("Valor investido (R$)")
        )
        if valor_investido == 0:
            valor_investido = None
        posicoes.append(
            PosicaoCarteira(
                ativo=ativo,
                classe=classe,
                valor_atual=valor_atual,
                valor_investido=valor_investido,
                benchmark=benchmark,
            )
        )
    return tuple(posicoes)


def resumir_carteira(
    posicoes: Iterable[PosicaoCarteira],
) -> ResumoCarteira:
    posicoes = tuple(posicoes)
    total = sum(posicao.valor_atual for posicao in posicoes)
    maior = max(
        (posicao.valor_atual for posicao in posicoes),
        default=0.0,
    )
    alocacao: dict[str, float] = {}
    for posicao in posicoes:
        alocacao[posicao.classe] = (
            alocacao.get(posicao.classe, 0.0) + posicao.valor_atual
        )

    com_custo = [
        posicao
        for posicao in posicoes
        if posicao.valor_investido is not None
    ]
    investido = sum(
        posicao.valor_investido or 0.0 for posicao in com_custo
    )
    atual_com_custo = sum(
        posicao.valor_atual for posicao in com_custo
    )
    resultado = atual_com_custo - investido if com_custo else None
    retorno = (
        ((atual_com_custo / investido) - 1) * 100
        if investido > 0
        else None
    )
    return ResumoCarteira(
        total_atual=total,
        quantidade_posicoes=len(posicoes),
        maior_concentracao_percentual=(
            (maior / total) * 100 if total else 0.0
        ),
        valor_investido_conhecido=investido,
        resultado_conhecido=resultado,
        retorno_conhecido_percentual=retorno,
        alocacao_por_classe=tuple(
            sorted(
                alocacao.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
    )


def cruzar_cenario(
    posicoes: Iterable[PosicaoCarteira],
    cenario: CenarioMacro | None,
) -> tuple[ImpactoClasseCarteira, ...]:
    posicoes = tuple(posicoes)
    resumo = resumir_carteira(posicoes)
    por_classe = dict(resumo.alocacao_por_classe)
    perspectivas = (
        {item.classe: item for item in cenario.perspectivas}
        if cenario is not None
        else {}
    )
    impactos: list[ImpactoClasseCarteira] = []
    for classe, valor in resumo.alocacao_por_classe:
        perspectiva = perspectivas.get(_PERSPECTIVA_POR_CLASSE.get(classe))
        impactos.append(
            ImpactoClasseCarteira(
                classe=classe,
                valor_atual=valor,
                peso_percentual=(
                    (valor / resumo.total_atual) * 100
                    if resumo.total_atual
                    else 0.0
                ),
                estado=(
                    perspectiva.estado
                    if perspectiva is not None
                    else "sem leitura específica"
                ),
                explicacao=(
                    perspectiva.explicacao
                    if perspectiva is not None
                    else (
                        "O Radar ainda não tem uma relação macro específica "
                        "para esta classe."
                    )
                ),
            )
        )
    return tuple(
        sorted(
            impactos,
            key=lambda item: (
                -por_classe.get(item.classe, 0.0),
                item.classe,
            ),
        )
    )


def comparar_com_benchmarks(
    posicoes: Iterable[PosicaoCarteira],
    series: Iterable[SerieMercado],
) -> tuple[ComparacaoPosicao, ...]:
    series_por_codigo = {serie.codigo: serie for serie in series}
    comparacoes: list[ComparacaoPosicao] = []
    for posicao in posicoes:
        codigo = _CODIGO_BENCHMARK.get(posicao.benchmark)
        serie = series_por_codigo.get(codigo)
        if serie is None:
            continue
        pontos = pontos_base_100(serie)
        if len(pontos) < 2:
            continue
        retorno_benchmark = pontos[-1].valor - 100
        retorno_posicao = posicao.retorno_percentual
        comparacoes.append(
            ComparacaoPosicao(
                ativo=posicao.ativo,
                benchmark=posicao.benchmark,
                retorno_posicao_percentual=retorno_posicao,
                retorno_benchmark_percentual=retorno_benchmark,
            )
        )
    return tuple(comparacoes)
