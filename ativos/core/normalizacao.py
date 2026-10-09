"""Regras puras de normalização das demonstrações e do capital social."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from datetime import date

import numpy as np
import pandas as pd


def texto_normalizado(valor: object) -> str:
    """Normaliza texto para comparações de fonte, sem alterar o texto exibido."""
    if valor is None or pd.isna(valor):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return re.sub(r"\s+", " ", texto).strip().upper()


def normalizar_demonstracao(quadro: pd.DataFrame) -> pd.DataFrame:
    """Converte datas/números e aplica a escala monetária declarada pela CVM."""
    resultado = quadro.copy()
    for coluna in ("DT_REFER", "DT_RECEB", "DT_INI_EXERC", "DT_FIM_EXERC"):
        if coluna in resultado:
            resultado[coluna] = pd.to_datetime(resultado[coluna], errors="coerce")
    if "VERSAO" in resultado:
        resultado["VERSAO"] = pd.to_numeric(resultado["VERSAO"], errors="coerce")
    if "VL_CONTA" in resultado:
        valor = pd.to_numeric(resultado["VL_CONTA"], errors="coerce")
        if "ESCALA_MOEDA" in resultado:
            escala = resultado["ESCALA_MOEDA"].map(texto_normalizado).eq("MIL")
            valor = valor * np.where(escala, 1000.0, 1.0)
        resultado["valor"] = valor
    if "DS_CONTA" in resultado:
        resultado["descricao_normalizada"] = resultado["DS_CONTA"].map(texto_normalizado)
    return resultado


def selecionar_versoes(
    quadro: pd.DataFrame,
    data_referencia: date | pd.Timestamp,
) -> pd.DataFrame:
    """Aplica point-in-time e mantém a maior versão de cada documento."""
    if quadro.empty:
        return quadro.copy()
    resultado = normalizar_demonstracao(quadro)
    referencia = pd.Timestamp(data_referencia)
    if "DT_RECEB" in resultado:
        resultado = resultado[resultado["DT_RECEB"].le(referencia)].copy()
    if resultado.empty or "VERSAO" not in resultado:
        return resultado
    chaves = [coluna for coluna in ("CNPJ_CIA", "DT_REFER") if coluna in resultado]
    maior = resultado.groupby(chaves, dropna=False)["VERSAO"].transform("max")
    return resultado[resultado["VERSAO"].eq(maior)].copy()


def preferir_consolidado(
    consolidado: pd.DataFrame,
    individual: pd.DataFrame,
    data_referencia: date | pd.Timestamp,
) -> pd.DataFrame:
    """Usa o relatório consolidado por documento e recorre ao individual na ausência."""
    con = selecionar_versoes(consolidado, data_referencia)
    ind = selecionar_versoes(individual, data_referencia)
    if con.empty:
        return ind
    if ind.empty:
        return con
    chaves = ["CNPJ_CIA", "DT_REFER"]
    documentos_consolidados = con[chaves].drop_duplicates().assign(_tem_consolidado=True)
    ind = ind.merge(documentos_consolidados, on=chaves, how="left")
    ind = ind[ind["_tem_consolidado"].isna()].drop(columns="_tem_consolidado")
    return pd.concat([con, ind], ignore_index=True, sort=False)


def mascara_conta(
    quadro: pd.DataFrame,
    codigos: Iterable[str],
    descricoes: Iterable[str],
) -> pd.Series:
    """Exige simultaneamente código permitido e descrição compatível."""
    codigos = tuple(str(codigo) for codigo in codigos)
    padrao = "|".join(f"(?:{descricao})" for descricao in descricoes)
    codigo_ok = quadro["CD_CONTA"].astype(str).isin(codigos)
    descricao = quadro.get("descricao_normalizada")
    if descricao is None:
        descricao = quadro["DS_CONTA"].map(texto_normalizado)
    return codigo_ok & descricao.str.contains(padrao, regex=True, na=False)


def calcular_pl_controladores(
    pl_consolidado: float | int | None,
    participacao_nao_controladores: float | int | None,
) -> float:
    """Calcula o PL atribuível aos controladores sem transformar ausência em zero."""
    if pl_consolidado is None or pd.isna(pl_consolidado):
        return np.nan
    participacao = 0.0 if pd.isna(participacao_nao_controladores) else float(
        participacao_nao_controladores
    )
    return float(pl_consolidado) - participacao


def calcular_ttm(
    valor_dfp: float | int | None,
    acumulado_atual: float | int | None,
    acumulado_anterior: float | int | None,
) -> float:
    """Aplica DFP + acumulado corrente - acumulado comparável anterior."""
    if valor_dfp is None or pd.isna(valor_dfp):
        return np.nan
    if pd.isna(acumulado_atual) or pd.isna(acumulado_anterior):
        return float(valor_dfp)
    return float(valor_dfp) + float(acumulado_atual) - float(acumulado_anterior)


def corrigir_quantidade_acoes(
    quantidade_on: float | int | None,
    quantidade_pn: float | int | None,
    patrimonio_liquido: float | int | None,
    preco_referencia: float | int | None,
) -> tuple[float, float, list[str]]:
    """Corrige composição informada em milhar e sinaliza escalas ainda implausíveis."""
    on = 0.0 if pd.isna(quantidade_on) else float(quantidade_on)
    pn = 0.0 if pd.isna(quantidade_pn) else float(quantidade_pn)
    alertas: list[str] = []
    total = on + pn
    if (
        total > 0
        and not pd.isna(patrimonio_liquido)
        and not pd.isna(preco_referencia)
        and float(preco_referencia) > 0
        and float(patrimonio_liquido) / total > 50 * float(preco_referencia)
    ):
        on *= 1000
        pn *= 1000
        total *= 1000
        alertas.append("qtd_em_milhar")
    if (
        total > 0
        and not pd.isna(patrimonio_liquido)
        and not pd.isna(preco_referencia)
        and float(preco_referencia) > 0
        and (
            float(patrimonio_liquido) / total < float(preco_referencia) / 40
            or float(patrimonio_liquido) / total > 40 * float(preco_referencia)
        )
    ):
        alertas.append("escala_suspeita")
    return on, pn, alertas


def parsear_acoes_por_unit(composicao: object) -> int | None:
    """Extrai o total de ações de descrições FCA como ``1 ON e 4 PN``."""
    texto = texto_normalizado(composicao)
    if not texto:
        return None
    padrao = re.compile(
        r"(\d+)\s*(?:(?:ACAO|ACOES)\s+)?"
        r"(?:ON\b|PN\b|ORDINARIAS?\b|PREFERENCI(?:AL|AIS)\b)"
    )
    quantidades = [int(valor) for valor in padrao.findall(texto)]
    total = sum(quantidades)
    return total if total > 0 else None


def calcular_valor_mercado(
    quantidade_on: float | int | None,
    quantidade_pn: float | int | None,
    preco_on: float | int | None,
    preco_pn: float | int | None,
) -> float:
    """Soma apenas as classes ON/PN; units não entram como uma terceira classe."""
    on = 0.0 if pd.isna(quantidade_on) else float(quantidade_on)
    pn = 0.0 if pd.isna(quantidade_pn) else float(quantidade_pn)
    if on + pn <= 0:
        return np.nan
    preco_on_valido = None if pd.isna(preco_on) else float(preco_on)
    preco_pn_valido = None if pd.isna(preco_pn) else float(preco_pn)
    if preco_on_valido is None:
        preco_on_valido = preco_pn_valido
    if preco_pn_valido is None:
        preco_pn_valido = preco_on_valido
    if preco_on_valido is None or preco_pn_valido is None:
        return np.nan
    return on * preco_on_valido + pn * preco_pn_valido
