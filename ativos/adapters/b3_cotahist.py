"""Parser posicional e aquisição do COTAHIST anual da B3."""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pandas as pd
import requests

from ativos.paths import cache_bruto_dir

B3_COTAHIST_URL = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{ano}.ZIP"


def deve_baixar(caminho: Path, ano: int, *, hoje: date | None = None) -> bool:
    referencia = hoje or date.today()
    if not caminho.exists():
        return True
    if ano < referencia.year:
        return False
    modificado = datetime.fromtimestamp(caminho.stat().st_mtime).date()
    return referencia - modificado > timedelta(days=1)


def baixar_cotahist(
    ano: int,
    *,
    pasta: Path | None = None,
    hoje: date | None = None,
    cliente: Any = requests,
) -> Path:
    """Baixa o histórico anual com substituição atômica e cache idempotente."""
    destino = (pasta or cache_bruto_dir()) / f"COTAHIST_A{ano}.ZIP"
    if not deve_baixar(destino, ano, hoje=hoje):
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_name(f".{destino.name}.part")
    try:
        resposta = cliente.get(
            B3_COTAHIST_URL.format(ano=ano),
            stream=True,
            timeout=(10, 180),
        )
        resposta.raise_for_status()
        with temporario.open("wb") as arquivo:
            for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                if bloco:
                    arquivo.write(bloco)
        os.replace(temporario, destino)
    finally:
        temporario.unlink(missing_ok=True)
    return destino


def _inteiro(campo: str) -> int:
    campo = campo.strip()
    return int(campo) if campo else 0


def parse_linha_cotahist(linha: str) -> dict[str, object] | None:
    """Converte um registro de 245 caracteres; cabeçalho e rodapé retornam ``None``."""
    if len(linha) < 242:
        return None
    tipreg = linha[0:2]
    tpmerc = linha[24:27]
    if tipreg != "01" or tpmerc != "010":
        return None
    fator_cotacao = _inteiro(linha[210:217])
    if fator_cotacao <= 0:
        fator_cotacao = 1
    preco_centavos = _inteiro(linha[108:121])
    return {
        "data": pd.to_datetime(linha[2:10], format="%Y%m%d", errors="coerce"),
        "codbdi": linha[10:12].strip(),
        "ticker": linha[12:24].strip().upper(),
        "tpmerc": tpmerc,
        "nomres": linha[27:39].strip(),
        "especi": linha[39:49].strip(),
        "preco": preco_centavos / 100 / fator_cotacao,
        "totneg": _inteiro(linha[147:152]),
        "volume": _inteiro(linha[170:188]) / 100,
        "fatcot": fator_cotacao,
        "isin": linha[230:242].strip(),
    }


def iterar_cotahist(caminho: Path) -> Iterator[dict[str, object]]:
    """Itera registros de mercado à vista sem materializar o ZIP inteiro."""
    with ZipFile(caminho) as arquivo_zip:
        membros = [nome for nome in arquivo_zip.namelist() if nome.upper().endswith(".TXT")]
        if not membros:
            raise FileNotFoundError(f"Nenhum TXT encontrado em {caminho}")
        with arquivo_zip.open(membros[0]) as arquivo:
            for linha_bytes in arquivo:
                registro = parse_linha_cotahist(linha_bytes.decode("latin1").rstrip("\r\n"))
                if registro is not None:
                    yield registro


def ler_cotahist(
    ano: int,
    *,
    pasta: Path | None = None,
    apenas_acoes: bool = False,
    apenas_fiis: bool = False,
) -> pd.DataFrame:
    """Lê um ano do COTAHIST; filtros por classe reduzem memória no pipeline."""
    if apenas_acoes and apenas_fiis:
        raise ValueError("Escolha apenas uma classe de ativo")
    caminho = (pasta or cache_bruto_dir()) / f"COTAHIST_A{ano}.ZIP"
    registros = iterar_cotahist(caminho)
    if apenas_acoes:
        registros = (registro for registro in registros if registro["codbdi"] == "02")
    if apenas_fiis:
        registros = (
            registro
            for registro in registros
            if registro["codbdi"] == "12"
            and str(registro["especi"]).strip().upper().startswith("CI")
        )
    return pd.DataFrame.from_records(registros)
