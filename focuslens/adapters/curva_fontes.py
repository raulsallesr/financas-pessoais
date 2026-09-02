"""Adaptador e cache da curva prefixada do Tesouro Transparente."""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path

import requests

from focuslens.core.curva_data import (
    PontoCurva,
    TIPO_PREFIXADO_SEM_CUPOM,
    manter_datas_recentes,
)
from focuslens.paths import DATA_DIR


CURVA_CSV_URL = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
    "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/"
    "precotaxatesourodireto.csv"
)
CURVA_FONTE_URL = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "taxas-dos-titulos-ofertados-pelo-tesouro-direto"
)
CURVA_FONTE = "Tesouro Transparente"
CURVA_LICENCA = "ODbL 1.0"
CACHE_PATH = DATA_DIR / "curva_prefixada_cache.json"
MAX_BYTES = 20_000_000
MAX_DATAS_CACHE = 45
TIMEOUT_SEGUNDOS = (5, 60)
USER_AGENT = "focuslens-br/1.13 (curva tesouro educacional)"

_COLUNAS_OBRIGATORIAS = {
    "Tipo Titulo",
    "Data Vencimento",
    "Data Base",
    "Taxa Compra Manha",
    "Taxa Venda Manha",
    "PU Compra Manha",
    "PU Venda Manha",
}


class ErroFonteCurva(Exception):
    """Falha controlada ao baixar ou interpretar a fonte pública."""


class ErroCacheCurva(Exception):
    """O cache da curva não pôde ser lido ou persistido com segurança."""


def _numero_br(valor: str | None, *, obrigatorio: bool) -> float | None:
    if valor is None or not valor.strip():
        if obrigatorio:
            raise ValueError("Campo numérico obrigatório vazio.")
        return None
    normalizado = valor.strip().replace(".", "").replace(",", ".")
    return float(normalizado)


def interpretar_csv(
    conteudo: bytes,
    *,
    max_datas: int = MAX_DATAS_CACHE,
) -> tuple[PontoCurva, ...]:
    """Interpreta somente Tesouro Prefixado sem cupom e mantém datas recentes."""
    try:
        texto = conteudo.decode("utf-8-sig")
        leitor = csv.DictReader(io.StringIO(texto), delimiter=";")
        colunas = set(leitor.fieldnames or ())
        if not _COLUNAS_OBRIGATORIAS.issubset(colunas):
            raise ErroFonteCurva(
                "O CSV do Tesouro mudou de estrutura."
            )
        pontos: list[PontoCurva] = []
        for linha in leitor:
            if linha.get("Tipo Titulo") != TIPO_PREFIXADO_SEM_CUPOM:
                continue
            pontos.append(
                PontoCurva(
                    data_referencia=datetime.strptime(
                        linha["Data Base"], "%d/%m/%Y"
                    ).date(),
                    tipo_titulo=linha["Tipo Titulo"],
                    vencimento=datetime.strptime(
                        linha["Data Vencimento"], "%d/%m/%Y"
                    ).date(),
                    taxa_compra=float(
                        _numero_br(
                            linha["Taxa Compra Manha"],
                            obrigatorio=True,
                        )
                    ),
                    taxa_venda=_numero_br(
                        linha["Taxa Venda Manha"],
                        obrigatorio=False,
                    ),
                    pu_compra=_numero_br(
                        linha["PU Compra Manha"],
                        obrigatorio=False,
                    ),
                    pu_venda=_numero_br(
                        linha["PU Venda Manha"],
                        obrigatorio=False,
                    ),
                    fonte=CURVA_FONTE,
                )
            )
    except ErroFonteCurva:
        raise
    except (KeyError, TypeError, UnicodeError, ValueError) as erro:
        raise ErroFonteCurva(
            "O CSV do Tesouro contém um registro inválido."
        ) from erro
    if not pontos:
        raise ErroFonteCurva(
            "A fonte não retornou títulos prefixados sem cupom."
        )
    try:
        return manter_datas_recentes(pontos, max_datas=max_datas)
    except ValueError as erro:
        raise ErroFonteCurva(
            "O CSV do Tesouro contém pontos conflitantes."
        ) from erro


def _baixar_csv() -> bytes:
    resposta: requests.Response | None = None
    try:
        resposta = requests.get(
            CURVA_CSV_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SEGUNDOS,
            stream=True,
        )
        resposta.raise_for_status()
        partes: list[bytes] = []
        total = 0
        for parte in resposta.iter_content(chunk_size=64 * 1024):
            if not parte:
                continue
            total += len(parte)
            if total > MAX_BYTES:
                raise ErroFonteCurva(
                    "O CSV do Tesouro excedeu o limite de segurança."
                )
            partes.append(parte)
        return b"".join(partes)
    except ErroFonteCurva:
        raise
    except requests.RequestException as erro:
        raise ErroFonteCurva(
            "O Tesouro Transparente não respondeu agora."
        ) from erro
    finally:
        if resposta is not None:
            resposta.close()


def buscar_curva_prefixada() -> tuple[PontoCurva, ...]:
    return interpretar_csv(_baixar_csv())


def _ler_cache() -> dict:
    if not CACHE_PATH.exists():
        return {"registros": []}
    try:
        conteudo = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as erro:
        raise ErroCacheCurva(
            "O cache local da curva está ilegível."
        ) from erro
    if not isinstance(conteudo, dict) or not isinstance(
        conteudo.get("registros", []), list
    ):
        raise ErroCacheCurva(
            "O cache local da curva tem uma estrutura inválida."
        )
    return conteudo


def data_ultima_atualizacao_cache() -> date | None:
    valor = _ler_cache().get("atualizado_em")
    if valor is None:
        return None
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError) as erro:
        raise ErroCacheCurva(
            "A data de atualização do cache da curva é inválida."
        ) from erro


def carregar_cache() -> list[PontoCurva]:
    conteudo = _ler_cache()
    try:
        pontos = [
            PontoCurva(
                data_referencia=date.fromisoformat(
                    registro["data_referencia"]
                ),
                tipo_titulo=registro["tipo_titulo"],
                vencimento=date.fromisoformat(registro["vencimento"]),
                taxa_compra=float(registro["taxa_compra"]),
                taxa_venda=(
                    None
                    if registro["taxa_venda"] is None
                    else float(registro["taxa_venda"])
                ),
                pu_compra=(
                    None
                    if registro["pu_compra"] is None
                    else float(registro["pu_compra"])
                ),
                pu_venda=(
                    None
                    if registro["pu_venda"] is None
                    else float(registro["pu_venda"])
                ),
                fonte=registro["fonte"],
            )
            for registro in conteudo.get("registros", [])
        ]
        return list(
            manter_datas_recentes(pontos, max_datas=MAX_DATAS_CACHE)
        )
    except (KeyError, TypeError, ValueError) as erro:
        raise ErroCacheCurva(
            "O cache local da curva contém um registro inválido."
        ) from erro


def _registros_json(pontos: tuple[PontoCurva, ...]) -> list[dict]:
    return [
        {
            "data_referencia": ponto.data_referencia.isoformat(),
            "tipo_titulo": ponto.tipo_titulo,
            "vencimento": ponto.vencimento.isoformat(),
            "taxa_compra": ponto.taxa_compra,
            "taxa_venda": ponto.taxa_venda,
            "pu_compra": ponto.pu_compra,
            "pu_venda": ponto.pu_venda,
            "fonte": ponto.fonte,
        }
        for ponto in pontos
    ]


def salvar_cache(pontos: tuple[PontoCurva, ...]) -> bool:
    registros = _registros_json(
        manter_datas_recentes(list(pontos), max_datas=MAX_DATAS_CACHE)
    )
    existente = _ler_cache()
    if existente.get("registros", []) == registros:
        return False
    conteudo = {
        "atualizado_em": date.today().isoformat(),
        "fonte": CURVA_FONTE_URL,
        "licenca": CURVA_LICENCA,
        "registros": registros,
    }
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporario: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=CACHE_PATH.parent,
            prefix=".curva_cache_",
            suffix=".tmp",
            delete=False,
        ) as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
            arquivo.flush()
            os.fsync(arquivo.fileno())
            temporario = Path(arquivo.name)
        temporario.replace(CACHE_PATH)
    except OSError as erro:
        raise ErroCacheCurva(
            "Não foi possível salvar o cache local da curva."
        ) from erro
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)
    return True


def atualizar_e_obter_curva() -> tuple[PontoCurva, ...]:
    pontos = buscar_curva_prefixada()
    salvar_cache(pontos)
    return pontos
