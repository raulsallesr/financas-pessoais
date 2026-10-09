"""Leitura e aquisição idempotente dos arquivos abertos da CVM."""

from __future__ import annotations

import os
from collections.abc import Iterable
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pandas as pd
import requests

from ativos.paths import cache_bruto_dir

CVM_DADOS_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA"
FII_DADOS_URL = "https://dados.cvm.gov.br/dados/FII/DOC"
TIPOS_DOCUMENTO = {"dfp", "itr", "fca"}
TIPOS_INFORME_FII = {"mensal": "INF_MENSAL", "trimestral": "INF_TRIMESTRAL"}
RELATORIOS = {
    "DRE",
    "BPA",
    "BPP",
    "DFC_MI",
    "DFC_MD",
    "DVA",
    "composicao_capital",
}


def _hoje(valor: date | None) -> date:
    return valor or date.today()


def deve_baixar(caminho: Path, ano: int, *, hoje: date | None = None) -> bool:
    """Decide a atualização: ano encerrado congela; corrente expira em um dia."""
    if not caminho.exists():
        return True
    referencia = _hoje(hoje)
    if ano < referencia.year:
        return False
    modificado = datetime.fromtimestamp(caminho.stat().st_mtime).date()
    return referencia - modificado > timedelta(days=1)


def baixar_arquivo(
    url: str,
    destino: Path,
    *,
    ano: int,
    hoje: date | None = None,
    cliente: Any = requests,
) -> Path:
    """Baixa ``url`` de modo atômico se a política de atualização exigir."""
    destino = Path(destino)
    if not deve_baixar(destino, ano, hoje=hoje):
        return destino

    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_name(f".{destino.name}.part")
    try:
        resposta = cliente.get(url, stream=True, timeout=(10, 120))
        resposta.raise_for_status()
        with temporario.open("wb") as arquivo:
            for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                if bloco:
                    arquivo.write(bloco)
        os.replace(temporario, destino)
    finally:
        temporario.unlink(missing_ok=True)
    return destino


def baixar_documento(
    tipo: str,
    ano: int,
    *,
    pasta: Path | None = None,
    hoje: date | None = None,
    cliente: Any = requests,
) -> Path:
    """Baixa um ZIP anual DFP, ITR ou FCA para o cache bruto."""
    tipo = tipo.lower()
    if tipo not in TIPOS_DOCUMENTO:
        raise ValueError(f"Tipo CVM desconhecido: {tipo}")
    nome = f"{tipo}_cia_aberta_{ano}.zip"
    url = f"{CVM_DADOS_URL}/DOC/{tipo.upper()}/DADOS/{nome}"
    return baixar_arquivo(
        url,
        (pasta or cache_bruto_dir()) / nome,
        ano=ano,
        hoje=hoje,
        cliente=cliente,
    )


def baixar_cadastro(
    *,
    pasta: Path | None = None,
    hoje: date | None = None,
    cliente: Any = requests,
) -> Path:
    """Baixa o cadastro corrente; ele segue a mesma validade diária."""
    referencia = _hoje(hoje)
    nome = "cad_cia_aberta.csv"
    url = f"{CVM_DADOS_URL}/CAD/DADOS/{nome}"
    return baixar_arquivo(
        url,
        (pasta or cache_bruto_dir()) / nome,
        ano=referencia.year,
        hoje=referencia,
        cliente=cliente,
    )


def baixar_informe_fii(
    tipo: str,
    ano: int,
    *,
    pasta: Path | None = None,
    hoje: date | None = None,
    cliente: Any = requests,
) -> Path:
    """Baixa um ZIP anual de informes mensais ou trimestrais de FII."""
    tipo = tipo.lower()
    try:
        documento = TIPOS_INFORME_FII[tipo]
    except KeyError as erro:
        raise ValueError(f"Tipo de informe FII desconhecido: {tipo}") from erro
    nome = f"inf_{tipo}_fii_{ano}.zip"
    url = f"{FII_DADOS_URL}/{documento}/DADOS/{nome}"
    return baixar_arquivo(
        url,
        (pasta or cache_bruto_dir()) / nome,
        ano=ano,
        hoje=hoje,
        cliente=cliente,
    )


def _ler_csv_zip(
    caminho: Path,
    membro: str,
    *,
    colunas: Iterable[str] | None = None,
) -> pd.DataFrame:
    with ZipFile(caminho) as arquivo_zip, arquivo_zip.open(membro) as arquivo:
        return pd.read_csv(
            arquivo,
            sep=";",
            encoding="latin1",
            dtype=str,
            usecols=list(colunas) if colunas is not None else None,
            low_memory=False,
        )


def _nome_membro(arquivo_zip: ZipFile, esperado: str) -> str:
    por_nome = {Path(nome).name.lower(): nome for nome in arquivo_zip.namelist()}
    try:
        return por_nome[esperado.lower()]
    except KeyError as erro:
        raise FileNotFoundError(f"{esperado} não existe em {arquivo_zip.filename}") from erro


def ler_cabecalho(
    tipo: str,
    ano: int,
    *,
    pasta: Path | None = None,
) -> pd.DataFrame:
    """Lê o cabeçalho anual, inclusive ``DT_RECEB`` para point-in-time."""
    tipo = tipo.lower()
    caminho = (pasta or cache_bruto_dir()) / f"{tipo}_cia_aberta_{ano}.zip"
    esperado = f"{tipo}_cia_aberta_{ano}.csv"
    with ZipFile(caminho) as arquivo_zip:
        membro = _nome_membro(arquivo_zip, esperado)
    return _ler_csv_zip(caminho, membro)


def ler_relatorio(
    tipo: str,
    ano: int,
    relatorio: str,
    *,
    consolidado: bool | None = True,
    pasta: Path | None = None,
    colunas: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Lê um relatório DFP/ITR e anexa a data de entrega do documento."""
    tipo = tipo.lower()
    relatorio = (
        relatorio.upper()
        if relatorio.lower() != "composicao_capital"
        else relatorio.lower()
    )
    if tipo not in {"dfp", "itr"}:
        raise ValueError("Relatórios contábeis existem apenas em DFP ou ITR")
    if relatorio not in RELATORIOS:
        raise ValueError(f"Relatório CVM desconhecido: {relatorio}")
    if relatorio == "composicao_capital":
        sufixo = relatorio
    else:
        if consolidado is None:
            raise ValueError("Informe consolidado=True ou False")
        sufixo = f"{relatorio}_{'con' if consolidado else 'ind'}"

    pasta = pasta or cache_bruto_dir()
    caminho = pasta / f"{tipo}_cia_aberta_{ano}.zip"
    esperado = f"{tipo}_cia_aberta_{sufixo}_{ano}.csv"
    with ZipFile(caminho) as arquivo_zip:
        membro = _nome_membro(arquivo_zip, esperado)
    quadro = _ler_csv_zip(caminho, membro, colunas=colunas)
    cabecalho = ler_cabecalho(tipo, ano, pasta=pasta)
    chaves = ["CNPJ_CIA", "DT_REFER", "VERSAO"]
    entrega = cabecalho[chaves + ["DT_RECEB"]].drop_duplicates(chaves, keep="last")
    quadro = quadro.merge(entrega, on=chaves, how="left", validate="many_to_one")
    quadro["_consolidado"] = relatorio == "composicao_capital" or bool(consolidado)
    quadro["_tipo_documento"] = tipo.upper()
    return quadro


def ler_fca(ano: int, *, pasta: Path | None = None) -> pd.DataFrame:
    """Lê a ponte ticker-CNPJ do formulário cadastral anual."""
    pasta = pasta or cache_bruto_dir()
    caminho = pasta / f"fca_cia_aberta_{ano}.zip"
    esperado = f"fca_cia_aberta_valor_mobiliario_{ano}.csv"
    with ZipFile(caminho) as arquivo_zip:
        membro = _nome_membro(arquivo_zip, esperado)
    quadro = _ler_csv_zip(caminho, membro)
    quadro["_ano_fca"] = ano
    return quadro


def ler_cadastro(*, pasta: Path | None = None) -> pd.DataFrame:
    """Lê o cadastro de companhias abertas sem inferência de tipos."""
    caminho = (pasta or cache_bruto_dir()) / "cad_cia_aberta.csv"
    return pd.read_csv(
        caminho,
        sep=";",
        encoding="latin1",
        dtype=str,
        low_memory=False,
    )


def ler_informe_fii(
    tipo: str,
    ano: int,
    quadro: str,
    *,
    pasta: Path | None = None,
    colunas: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Lê um quadro de informe FII anual sem inferir tipos."""
    tipo = tipo.lower()
    if tipo not in TIPOS_INFORME_FII:
        raise ValueError(f"Tipo de informe FII desconhecido: {tipo}")
    caminho = (pasta or cache_bruto_dir()) / f"inf_{tipo}_fii_{ano}.zip"
    esperado = f"inf_{tipo}_fii_{quadro}_{ano}.csv"
    with ZipFile(caminho) as arquivo_zip:
        membro = _nome_membro(arquivo_zip, esperado)
    return _ler_csv_zip(caminho, membro, colunas=colunas)
