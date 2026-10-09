"""Caminhos locais do módulo Ativos.

Os dados públicos brutos e derivados ficam fora do repositório. As funções,
em vez de constantes avaliadas no import, permitem que testes e operadores
troquem os diretórios por variáveis de ambiente sem recarregar o módulo.
"""

from __future__ import annotations

import os
from pathlib import Path


def cache_bruto_dir() -> Path:
    """Retorna a pasta dos arquivos oficiais ainda não transformados."""
    configurado = os.getenv("LASTRO_CACHE_DIR")
    if configurado:
        return Path(configurado).expanduser()
    return Path.home() / ".cache" / "lastro" / "raw"


def dados_derivados_dir() -> Path:
    """Retorna a pasta dos Parquets e metadados produzidos pelo pipeline."""
    configurado = os.getenv("LASTRO_DADOS_DIR")
    if configurado:
        return Path(configurado).expanduser()
    return Path.home() / ".cache" / "lastro" / "derived"


def caminho_acoes() -> Path:
    return dados_derivados_dir() / "acoes.parquet"


def caminho_meta_acoes() -> Path:
    return dados_derivados_dir() / "acoes_meta.json"


def caminho_fiis() -> Path:
    return dados_derivados_dir() / "fiis.parquet"


def caminho_meta_fiis() -> Path:
    return dados_derivados_dir() / "fiis_meta.json"
