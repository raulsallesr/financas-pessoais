"""Baixa os dados públicos brutos que alimentam o módulo Ativos (CVM e B3).

Uso: python -m scripts.baixar_dados_ativos [--ano AAAA] [--listar]

Os arquivos vão para o cache bruto (`%USERPROFILE%\\.cache\\lastro\\raw`, ou
`LASTRO_CACHE_DIR`), fora do repositório. O download é idempotente: ano encerrado
nunca é baixado de novo; o ano corrente é renovado se tiver mais de um dia. São
cerca de 400 MB na primeira execução. Depois, rode `python -m scripts.atualizar_ativos`.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import requests

from ativos.adapters.b3_cotahist import baixar_cotahist
from ativos.adapters.cvm import baixar_cadastro, baixar_documento, baixar_informe_fii

# Quantos exercícios de DFP o pipeline de ações usa (CAGR de 5 anos precisa de 6).
ANOS_DFP = 6


def planejar(ano: int) -> list[tuple[str, Callable[..., Path]]]:
    """Lista (rótulo, função de download) na ordem em que serão executados."""
    plano: list[tuple[str, Callable[..., Path]]] = [
        ("CVM cadastro de companhias", lambda **kw: baixar_cadastro(**kw)),
    ]
    for referencia in range(ano - ANOS_DFP, ano + 1):
        plano.append(
            (f"CVM DFP {referencia}", lambda r=referencia, **kw: baixar_documento("dfp", r, **kw))
        )
    for referencia in (ano - 1, ano):
        plano.append(
            (f"CVM ITR {referencia}", lambda r=referencia, **kw: baixar_documento("itr", r, **kw))
        )
        plano.append(
            (f"CVM FCA {referencia}", lambda r=referencia, **kw: baixar_documento("fca", r, **kw))
        )
        plano.append(
            (
                f"CVM FII mensal {referencia}",
                lambda r=referencia, **kw: baixar_informe_fii("mensal", r, **kw),
            )
        )
        plano.append(
            (
                f"CVM FII trimestral {referencia}",
                lambda r=referencia, **kw: baixar_informe_fii("trimestral", r, **kw),
            )
        )
        plano.append(
            (f"B3 COTAHIST {referencia}", lambda r=referencia, **kw: baixar_cotahist(r, **kw))
        )
    return plano


def executar(
    ano: int,
    *,
    pasta: Path | None = None,
    cliente: Any = requests,
    saida: Callable[[str], None] = print,
) -> tuple[list[str], list[str]]:
    """Executa o plano; devolve (baixados_ou_em_cache, indisponiveis)."""
    plano = planejar(ano)
    ok: list[str] = []
    indisponiveis: list[str] = []
    for posicao, (rotulo, baixar) in enumerate(plano, start=1):
        saida(f"[{posicao}/{len(plano)}] {rotulo} ...")
        try:
            caminho = baixar(pasta=pasta, cliente=cliente)
        except requests.HTTPError as erro:
            status = getattr(erro.response, "status_code", "?")
            saida(f"    indisponível (HTTP {status}); segue sem ele")
            indisponiveis.append(rotulo)
            continue
        tamanho = caminho.stat().st_size / 1e6 if caminho.exists() else 0
        saida(f"    ok ({tamanho:.1f} MB)")
        ok.append(rotulo)
    return ok, indisponiveis


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ano", type=int, default=date.today().year)
    parser.add_argument("--listar", action="store_true", help="só mostra o que seria baixado")
    args = parser.parse_args(argv)

    if args.listar:
        for rotulo, _ in planejar(args.ano):
            print(rotulo)
        return 0

    ok, indisponiveis = executar(args.ano)
    print(f"\nConcluído: {len(ok)} arquivos disponíveis, {len(indisponiveis)} indisponíveis.")
    if indisponiveis:
        print("Indisponíveis (normal para o ano corrente cedo): " + ", ".join(indisponiveis))
    print("Próximo passo: python -m scripts.atualizar_ativos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
