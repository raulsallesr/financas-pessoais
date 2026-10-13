"""Sincroniza os derivados públicos do módulo Ativos a partir da release fixa.

Uso:
    python -m scripts.sincronizar_dados [--repo dono/nome] [--forcar] [--sem-rede]

O download usa somente a biblioteca padrão. Pandas e PyArrow, já exigidos pelo
pipeline, são usados apenas para validar os Parquets antes da substituição.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa

from ativos.paths import dados_derivados_dir
from scripts.atualizar_ativos import SCHEMA_VERSION_ACOES, SCHEMA_VERSION_FIIS

RELEASE_TAG = "dados-ativos"
DEFAULT_REPOSITORY = "raulsallesr/financas-pessoais"
NETWORK_TIMEOUT = 30
USER_AGENT = "lastro-sincronizar-dados"
ASSETS = (
    "acoes.parquet",
    "acoes_meta.json",
    "fiis.parquet",
    "fiis_meta.json",
)
SCHEMAS_SUPORTADOS = {
    "acoes_meta.json": SCHEMA_VERSION_ACOES,
    "fiis_meta.json": SCHEMA_VERSION_FIIS,
}
COLUNAS_MINIMAS = {"ticker", "preco"}
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class ErroSincronizacao(RuntimeError):
    """Falha esperada que deve chegar à CLI sem traceback."""


def _normalizar_repositorio(value: str) -> str | None:
    value = value.strip().removesuffix(".git").strip("/")
    if REPOSITORY_PATTERN.fullmatch(value):
        return value
    return None


def _repositorio_da_origem() -> str | None:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode or not result.stdout.strip():
        return None
    origin = result.stdout.strip()
    if origin.startswith("git@github.com:"):
        return _normalizar_repositorio(origin.split(":", maxsplit=1)[1])
    parsed = urllib.parse.urlparse(origin)
    if parsed.hostname and parsed.hostname.lower() == "github.com":
        return _normalizar_repositorio(parsed.path)
    return None


def resolver_repositorio(repo: str | None) -> str:
    """Resolve o repositório explícito, o remote origin ou o fallback público."""
    if repo is not None:
        normalizado = _normalizar_repositorio(repo)
        if normalizado is None:
            raise ErroSincronizacao("--repo deve usar o formato dono/nome")
        return normalizado
    return _repositorio_da_origem() or DEFAULT_REPOSITORY


def _request(url: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )


def _ler_url(url: str, *, cliente: Any, rotulo: str) -> bytes:
    try:
        with cliente.urlopen(_request(url), timeout=NETWORK_TIMEOUT) as response:
            conteudo = response.read()
    except urllib.error.HTTPError as exc:
        raise ErroSincronizacao(f"{rotulo}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        detalhe = getattr(exc, "reason", exc)
        raise ErroSincronizacao(f"{rotulo}: falha de rede ({detalhe})") from exc
    if not isinstance(conteudo, bytes):
        raise ErroSincronizacao(f"{rotulo}: resposta HTTP inválida")
    return conteudo


def _carregar_release(repo: str, *, cliente: Any) -> dict[str, str]:
    url = f"https://api.github.com/repos/{repo}/releases/tags/{RELEASE_TAG}"
    try:
        conteudo = _ler_url(url, cliente=cliente, rotulo="consulta da release")
    except ErroSincronizacao as exc:
        if "HTTP 404" in str(exc):
            raise ErroSincronizacao(
                f"a release '{RELEASE_TAG}' não existe em {repo}"
            ) from exc
        raise
    try:
        payload = json.loads(conteudo.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ErroSincronizacao("a API do GitHub devolveu uma release inválida") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("assets"), list):
        raise ErroSincronizacao("a API do GitHub devolveu uma release sem lista de assets")
    encontrados: dict[str, str] = {}
    for asset in payload["assets"]:
        if not isinstance(asset, dict):
            continue
        name = asset.get("name")
        url_download = asset.get("browser_download_url")
        if isinstance(name, str) and isinstance(url_download, str):
            encontrados.setdefault(name, url_download)
    ausentes = [name for name in ASSETS if name not in encontrados]
    if ausentes:
        raise ErroSincronizacao(
            "a release não contém todos os assets obrigatórios: " + ", ".join(ausentes)
        )
    return {name: encontrados[name] for name in ASSETS}


def _gravar_download(url: str, destino: Path, *, cliente: Any, rotulo: str) -> None:
    conteudo = _ler_url(url, cliente=cliente, rotulo=rotulo)
    try:
        destino.write_bytes(conteudo)
    except OSError as exc:
        raise ErroSincronizacao(f"não foi possível gravar {destino.name}: {exc}") from exc


def _validar_meta(path: Path, *, esperado: int) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ErroSincronizacao(f"{path.name} não é um JSON válido") from exc
    if not isinstance(payload, dict):
        raise ErroSincronizacao(f"{path.name} deve conter um objeto JSON")
    if "schema_version" not in payload:
        raise ErroSincronizacao(f"{path.name} não contém schema_version")
    if payload["schema_version"] != esperado:
        raise ErroSincronizacao(
            f"{path.name} usa esquema não suportado: {payload['schema_version']} "
            f"(esperado: {esperado})"
        )
    data_cotacao = payload.get("data_cotacao")
    if not isinstance(data_cotacao, str):
        raise ErroSincronizacao(f"{path.name} não contém data_cotacao")
    try:
        date.fromisoformat(data_cotacao)
    except ValueError as exc:
        raise ErroSincronizacao(f"{path.name} contém data_cotacao inválida") from exc
    return payload


def _parse_gerado_em(value: Any, *, arquivo: str) -> datetime:
    if not isinstance(value, str):
        raise ErroSincronizacao(f"{arquivo} não contém gerado_em")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ErroSincronizacao(f"{arquivo} contém gerado_em inválido") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _gerado_em_local(path: Path) -> datetime | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        value = payload.get("gerado_em") if isinstance(payload, dict) else None
        return _parse_gerado_em(value, arquivo=path.name)
    except (OSError, UnicodeError, json.JSONDecodeError, ErroSincronizacao):
        return None


def _validar_parquet(path: Path) -> tuple[pd.DataFrame, int]:
    try:
        frame = pd.read_parquet(path)
    except (OSError, ValueError, TypeError, pa.ArrowException) as exc:
        raise ErroSincronizacao(f"{path.name} está corrompido ou ilegível") from exc
    ausentes = sorted(COLUNAS_MINIMAS - set(frame.columns))
    if ausentes:
        raise ErroSincronizacao(
            f"{path.name} não contém as colunas mínimas: {', '.join(ausentes)}"
        )
    return frame, len(frame)


def _validar_lote(pasta: Path) -> tuple[dict[str, Any], dict[str, Any], int, int]:
    acoes_meta = _validar_meta(
        pasta / "acoes_meta.json", esperado=SCHEMAS_SUPORTADOS["acoes_meta.json"]
    )
    fiis_meta = _validar_meta(
        pasta / "fiis_meta.json", esperado=SCHEMAS_SUPORTADOS["fiis_meta.json"]
    )
    _parse_gerado_em(acoes_meta.get("gerado_em"), arquivo="acoes_meta.json")
    _parse_gerado_em(fiis_meta.get("gerado_em"), arquivo="fiis_meta.json")
    _, linhas_acoes = _validar_parquet(pasta / "acoes.parquet")
    _, linhas_fiis = _validar_parquet(pasta / "fiis.parquet")
    return acoes_meta, fiis_meta, linhas_acoes, linhas_fiis


def _instalar_lote(pasta_temporaria: Path, destino: Path) -> None:
    try:
        destino.mkdir(parents=True, exist_ok=True)
        for name in ASSETS:
            os.replace(pasta_temporaria / name, destino / name)
    except OSError as exc:
        raise ErroSincronizacao(f"não foi possível substituir os dados locais: {exc}") from exc


@contextmanager
def _pasta_temporaria_ao_lado(destino: Path) -> Iterator[Path]:
    """Cria staging vizinho sem o ACL restritivo do tempfile no Python 3.13/Windows."""
    staging = destino.parent / f".{destino.name}-sincronizar-{uuid.uuid4().hex}"
    try:
        staging.mkdir()
    except OSError as exc:
        raise ErroSincronizacao(f"não foi possível criar a pasta temporária: {exc}") from exc
    try:
        yield staging
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _resumo(
    acoes_meta: dict[str, Any],
    fiis_meta: dict[str, Any],
    linhas_acoes: int,
    linhas_fiis: int,
) -> str:
    return (
        "Dados sincronizados. "
        f"Cotação: ações {acoes_meta['data_cotacao']}; FIIs {fiis_meta['data_cotacao']}. "
        f"Gerado em: ações {acoes_meta['gerado_em']}; FIIs {fiis_meta['gerado_em']}. "
        f"Linhas: ações {linhas_acoes}; FIIs {linhas_fiis}."
    )


def executar(
    *,
    repo: str | None = None,
    forcar: bool = False,
    sem_rede: bool = False,
    pasta_derivada: Path | None = None,
    cliente: Any = urllib.request,
    saida: Callable[[str], None] = print,
) -> bool:
    """Sincroniza o lote; retorna ``True`` quando instalou novos arquivos."""
    if sem_rede:
        raise ErroSincronizacao(
            "rede desativada por --sem-rede; nenhum arquivo local foi alterado"
        )
    repository = resolver_repositorio(repo)
    assets = _carregar_release(repository, cliente=cliente)
    destino = Path(pasta_derivada) if pasta_derivada is not None else dados_derivados_dir()
    destino.parent.mkdir(parents=True, exist_ok=True)
    with _pasta_temporaria_ao_lado(destino) as staging:
        _gravar_download(
            assets["acoes_meta.json"],
            staging / "acoes_meta.json",
            cliente=cliente,
            rotulo="download de acoes_meta.json",
        )
        remoto_meta = _validar_meta(
            staging / "acoes_meta.json",
            esperado=SCHEMAS_SUPORTADOS["acoes_meta.json"],
        )
        remoto_gerado = _parse_gerado_em(
            remoto_meta.get("gerado_em"), arquivo="acoes_meta.json"
        )
        local_gerado = _gerado_em_local(destino / "acoes_meta.json")
        if not forcar and local_gerado is not None and local_gerado >= remoto_gerado:
            saida(
                "Dados locais já estão iguais ou mais novos que a release "
                f"(local: {local_gerado.isoformat()}; release: {remoto_gerado.isoformat()}). "
                "Nenhum download adicional foi necessário."
            )
            return False
        for name in ASSETS:
            if name == "acoes_meta.json":
                continue
            _gravar_download(
                assets[name],
                staging / name,
                cliente=cliente,
                rotulo=f"download de {name}",
            )
        acoes_meta, fiis_meta, linhas_acoes, linhas_fiis = _validar_lote(staging)
        _instalar_lote(staging, destino)
    saida(_resumo(acoes_meta, fiis_meta, linhas_acoes, linhas_fiis))
    return True


def main(argv: list[str] | None = None, *, cliente: Any = urllib.request) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="repositório público no formato dono/nome")
    parser.add_argument("--forcar", action="store_true", help="baixa mesmo se o local for atual")
    parser.add_argument("--sem-rede", action="store_true", help="não acessa a rede")
    args = parser.parse_args(argv)
    try:
        executar(
            repo=args.repo,
            forcar=args.forcar,
            sem_rede=args.sem_rede,
            cliente=cliente,
        )
    except ErroSincronizacao as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - invocação do módulo
    sys.exit(main())
