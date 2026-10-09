"""Composição pura da tabela de ações a partir dos quadros dos adapters."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from difflib import SequenceMatcher

import numpy as np
import pandas as pd

from ativos.core.metricas_acoes import COLUNAS_METRICAS, calcular_metricas_tabela
from ativos.core.normalizacao import (
    calcular_pl_controladores,
    calcular_ttm,
    calcular_valor_mercado,
    corrigir_quantidade_acoes,
    mascara_conta,
    parsear_acoes_por_unit,
    preferir_consolidado,
    selecionar_versoes,
    texto_normalizado,
)

CONTAS_FLUXO = {
    "receita": [(("3.01",), (r"RECEITA",))],
    "resultado_bruto": [(("3.03",), (r"RESULTADO BRUTO",))],
    "ebit": [
        (("3.05",), (r"RESULTADO ANTES DO RESULTADO FINANCEIRO E DOS TRIBUTOS",)),
    ],
    "lucro": [
        (
            ("3.11.01",),
            (r"ATRIBUIDO A(?:OS)? (?:SOCIOS|ACIONISTAS).*(?:CONTROLADORA|CONTROLADORES)",),
        ),
        (
            ("3.09.01",),
            (r"ATRIBUIDO A(?:OS)? (?:SOCIOS|ACIONISTAS).*(?:CONTROLADORA|CONTROLADORES)",),
        ),
        (
            ("3.11",),
            (
                r"LUCRO(?:/| OU )PREJUIZO(?: LIQUIDO)?(?: CONSOLIDADO)?(?: DO)? PERIODO",
                r"RESULTADO LIQUIDO",
            ),
        ),
        (
            ("3.09", "3.13"),
            (r"LUCRO(?:/| OU )PREJUIZO.*PERIODO", r"RESULTADO LIQUIDO"),
        ),
    ],
}

CONTAS_BPA = {
    "ativo_total": [(("1",), (r"ATIVO TOTAL",))],
    "ativo_circulante": [(("1.01",), (r"ATIVO CIRCULANTE",))],
    "caixa": [(("1.01.01",), (r"CAIXA", r"DISPONIBILIDADES"))],
    "aplicacoes_financeiras": [
        (("1.01.02",), (r"APLICACOES FINANCEIRAS", r"APLICACOES DE LIQUIDEZ")),
    ],
}

CONTAS_BPP = {
    "passivo_total": [(("2",), (r"PASSIVO TOTAL",))],
    "passivo_circulante": [(("2.01",), (r"PASSIVO CIRCULANTE",))],
    "passivo_nao_circulante": [
        (("2.02",), (r"PASSIVO NAO CIRCULANTE",)),
    ],
    "emprestimos_cp": [
        (("2.01.04",), (r"EMPRESTIMOS", r"FINANCIAMENTOS", r"DEBENTURES")),
    ],
    "emprestimos_lp": [
        (("2.02.01",), (r"EMPRESTIMOS", r"FINANCIAMENTOS", r"DEBENTURES")),
    ],
    "pl_consolidado": [
        (("2.03",), (r"PATRIMONIO LIQUIDO",)),
        (("2.05", "2.07", "2.08"), (r"PATRIMONIO LIQUIDO",)),
    ],
    "participacao_nao_controladores": [
        (
            ("2.03.09", "2.07.02", "2.08.09"),
            (r"(?:PARTICIPACAO|PATRIMONIO LIQUIDO ATRIBUIDO).*(?:NAO CONTROLADOR)",),
        ),
    ],
}


def _serie_alertas(valor: object) -> list[str]:
    if isinstance(valor, list):
        return list(valor)
    if isinstance(valor, tuple):
        return list(valor)
    if valor is None or (not isinstance(valor, (list, tuple)) and pd.isna(valor)):
        return []
    return [str(valor)]


def selecionar_universo(
    cotacoes: pd.DataFrame,
    *,
    data_referencia: str | pd.Timestamp | None = None,
    liquidez_minima: float = 100_000,
    minimo_pregoes: int = 40,
) -> pd.DataFrame:
    """Seleciona ações/units líquidas e calcula preço, ADTV e salto de preço."""
    if cotacoes.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "empresa_b3",
                "especi",
                "preco",
                "liquidez_media_diaria",
                "data_cotacao",
                "alertas",
            ]
        )
    quadro = cotacoes.copy()
    quadro["data"] = pd.to_datetime(quadro["data"], errors="coerce")
    limite = pd.Timestamp(data_referencia) if data_referencia is not None else quadro["data"].max()
    quadro = quadro[
        quadro["data"].le(limite)
        & quadro["codbdi"].eq("02")
        & quadro["especi"].fillna("").str.strip().str.upper().str.startswith(("ON", "PN", "UNT"))
    ].copy()
    if quadro.empty:
        return selecionar_universo(pd.DataFrame())

    datas = quadro["data"].dropna().drop_duplicates().sort_values()
    datas_63 = set(datas.tail(63))
    datas_252 = set(datas.tail(252))
    janela_63 = quadro[quadro["data"].isin(datas_63)].copy()
    janela_63["teve_negocio"] = pd.to_numeric(janela_63["totneg"], errors="coerce").gt(0)
    janela_63["volume"] = pd.to_numeric(janela_63["volume"], errors="coerce")
    liquidez = (
        janela_63.groupby("ticker", as_index=False)
        .agg(
            liquidez_media_diaria=("volume", "mean"),
            pregoes_com_negocio=("teve_negocio", "sum"),
        )
    )

    historico = quadro[quadro["data"].isin(datas_252)].sort_values(["ticker", "data"])
    historico["retorno"] = historico.groupby("ticker", sort=False)["preco"].pct_change(
        fill_method=None
    )
    tickers_com_salto = set(
        historico.loc[historico["retorno"].abs().gt(0.35), "ticker"].astype(str)
    )
    ultimas = (
        quadro.sort_values(["ticker", "data"])
        .drop_duplicates("ticker", keep="last")
        .rename(columns={"nomres": "empresa_b3", "data": "data_cotacao"})
    )
    universo = ultimas.merge(liquidez, on="ticker", how="left", validate="one_to_one")
    universo = universo[
        universo["liquidez_media_diaria"].ge(liquidez_minima)
        & universo["pregoes_com_negocio"].ge(minimo_pregoes)
    ].copy()
    universo["alertas"] = universo["ticker"].map(
        lambda ticker: ["salto_preco"] if ticker in tickers_com_salto else []
    )
    return universo[
        [
            "ticker",
            "empresa_b3",
            "especi",
            "preco",
            "liquidez_media_diaria",
            "data_cotacao",
            "alertas",
        ]
    ].reset_index(drop=True)


PREFIXOS_NOME_B3 = {
    "LOJAS MARISA": "MARISA LOJAS",
    "BTGP BANCO": "BANCO BTG PACTUAL",
    "SID NACIONAL": "CIA SIDERURGICA NACIONAL",
}


def _nome_chave(valor: object, *, expandir_prefixo_b3: bool = False) -> str:
    texto = texto_normalizado(valor)
    if expandir_prefixo_b3:
        for prefixo, substituto in PREFIXOS_NOME_B3.items():
            if texto == prefixo or texto.startswith(f"{prefixo} "):
                texto = f"{substituto}{texto[len(prefixo) :]}"
                break
    texto = re.sub(r"\b(S A|SA|LTDA|CIA|COMPANHIA|HOLDING|PARTICIPACOES)\b", " ", texto)
    return re.sub(r"[^A-Z0-9]", "", texto)


def _mapa_fca(fca: pd.DataFrame) -> pd.DataFrame:
    if fca.empty:
        return pd.DataFrame(columns=["ticker", "cnpj", "empresa_fca"])
    quadro = fca.copy()
    quadro["ticker"] = quadro["Codigo_Negociacao"].fillna("").str.upper().str.strip()
    quadro = quadro.assign(ticker=quadro["ticker"].str.split(r"[,;/\s]+", regex=True)).explode(
        "ticker"
    )
    ticker_valido = quadro["ticker"].str.fullmatch(r"[A-Z0-9]{4,10}", na=False) & quadro[
        "ticker"
    ].str.contains(r"\d$", regex=True, na=False)
    quadro = quadro[ticker_valido].copy()
    quadro["_data"] = pd.to_datetime(quadro.get("Data_Referencia"), errors="coerce")
    quadro["_versao"] = pd.to_numeric(quadro.get("Versao"), errors="coerce")
    quadro = quadro.sort_values(["_data", "_versao", "_ano_fca"], na_position="first")
    quadro = quadro.drop_duplicates("ticker", keep="last")
    return quadro.rename(
        columns={"CNPJ_Companhia": "cnpj", "Nome_Empresarial": "empresa_fca"}
    )[["ticker", "cnpj", "empresa_fca"]]


def _fallback_cadastro(nome_b3: object, cadastro: pd.DataFrame) -> str | None:
    chave = _nome_chave(nome_b3, expandir_prefixo_b3=True)
    if len(chave) < 4 or cadastro.empty:
        return None
    notas_por_cnpj: dict[str, float] = {}
    for registro in cadastro.itertuples(index=False):
        cnpj = getattr(registro, "CNPJ_CIA", None)
        if cnpj is None or pd.isna(cnpj):
            continue
        nomes = (
            _nome_chave(getattr(registro, "DENOM_COMERC", "")),
            _nome_chave(getattr(registro, "DENOM_SOCIAL", "")),
        )
        for nome in nomes:
            if not nome:
                continue
            nota = SequenceMatcher(None, chave, nome[: max(len(chave), 4)]).ratio()
            if nome == chave:
                nota = 1.0
            if nome.startswith(chave) or chave.startswith(nome):
                nota = max(nota, 0.9)
            notas_por_cnpj[str(cnpj)] = max(notas_por_cnpj.get(str(cnpj), 0.0), nota)
    ordenadas = sorted(notas_por_cnpj.items(), key=lambda item: item[1], reverse=True)
    if not ordenadas or ordenadas[0][1] < 0.82:
        return None
    if len(ordenadas) > 1 and ordenadas[1][1] >= ordenadas[0][1] - 0.05:
        return None
    return ordenadas[0][0]


def mapear_tickers(
    universo: pd.DataFrame,
    fca: pd.DataFrame,
    cadastro: pd.DataFrame,
) -> pd.DataFrame:
    """Liga ticker a CNPJ pelo FCA e, quando seguro, pelo nome cadastral."""
    resultado = universo.merge(_mapa_fca(fca), on="ticker", how="left", validate="one_to_one")
    resultado["origem_cnpj"] = np.where(resultado["cnpj"].notna(), "fca", None)
    faltantes = resultado["cnpj"].isna()
    if faltantes.any():
        resolvidos = resultado.loc[faltantes, "empresa_b3"].map(
            lambda nome: _fallback_cadastro(nome, cadastro)
        )
        resultado.loc[faltantes, "cnpj"] = resolvidos
        resultado.loc[faltantes & resultado["cnpj"].notna(), "origem_cnpj"] = "nome"
    resultado["alertas"] = [
        alertas + ([] if not pd.isna(cnpj) else ["sem_cnpj"])
        for alertas, cnpj in zip(
            resultado["alertas"].map(_serie_alertas), resultado["cnpj"], strict=True
        )
    ]
    return resultado


def _extrair_prioridade(
    quadro: pd.DataFrame,
    alternativas: Iterable[tuple[tuple[str, ...], tuple[str, ...]]],
    *,
    chaves: list[str],
    zero_como_ausente: bool = False,
) -> pd.DataFrame:
    partes = []
    for prioridade, (codigos, descricoes) in enumerate(alternativas):
        parte = quadro[mascara_conta(quadro, codigos, descricoes)].copy()
        parte["_prioridade_conta"] = prioridade
        partes.append(parte)
    if not partes:
        return quadro.iloc[0:0].copy()
    resultado = pd.concat(partes, ignore_index=True, sort=False)
    resultado["_sem_valor"] = resultado["valor"].isna()
    if zero_como_ausente:
        resultado["_sem_valor"] |= resultado["valor"].eq(0)
    return (
        resultado.sort_values(["_sem_valor", "_prioridade_conta"])
        .drop_duplicates(chaves, keep="first")
        .drop(columns=["_prioridade_conta", "_sem_valor"])
    )


def _preparar_relatorio(
    origem: tuple[pd.DataFrame, pd.DataFrame] | None,
    data_referencia: pd.Timestamp,
) -> pd.DataFrame:
    if origem is None:
        return pd.DataFrame()
    return preferir_consolidado(origem[0], origem[1], data_referencia)


def _preparar_dfc(
    origem: tuple[pd.DataFrame, ...] | None,
    data_referencia: pd.Timestamp,
) -> pd.DataFrame:
    """Prioriza DFC MI consolidada, MD consolidada e depois as individuais."""
    if origem is None:
        return pd.DataFrame()
    escolhidos: list[pd.DataFrame] = []
    documentos_usados: set[tuple[object, object]] = set()
    for quadro in origem:
        candidato = selecionar_versoes(quadro, data_referencia)
        if candidato.empty:
            continue
        chaves = list(zip(candidato["CNPJ_CIA"], candidato["DT_REFER"], strict=True))
        manter = [chave not in documentos_usados for chave in chaves]
        candidato = candidato.loc[manter].copy()
        if candidato.empty:
            continue
        documentos_usados.update(
            zip(candidato["CNPJ_CIA"], candidato["DT_REFER"], strict=True)
        )
        escolhidos.append(candidato)
    if not escolhidos:
        return pd.DataFrame()
    return pd.concat(escolhidos, ignore_index=True, sort=False)


def _fluxo_empresa(
    dfp: pd.DataFrame,
    itr: pd.DataFrame,
    nome: str,
) -> pd.DataFrame:
    alternativas = CONTAS_FLUXO[nome]
    chaves = ["CNPJ_CIA", "DT_REFER", "ORDEM_EXERC", "DT_INI_EXERC"]
    anual = _extrair_prioridade(
        dfp,
        alternativas,
        chaves=chaves,
        zero_como_ausente=nome == "lucro",
    )
    trimestral = _extrair_prioridade(
        itr,
        alternativas,
        chaves=chaves,
        zero_como_ausente=nome == "lucro",
    )
    anual = anual[
        anual["ORDEM_EXERC"].eq("ÚLTIMO")
        & anual["DT_INI_EXERC"].dt.month.eq(1)
        & anual["DT_INI_EXERC"].dt.day.eq(1)
    ].copy()
    if anual.empty:
        return pd.DataFrame(columns=["cnpj", f"{nome}_ttm"])
    anual = anual.sort_values(["CNPJ_CIA", "DT_REFER"])
    ultimo = anual.drop_duplicates("CNPJ_CIA", keep="last").copy()
    base = ultimo[["CNPJ_CIA", "DT_REFER", "valor"]].rename(
        columns={"CNPJ_CIA": "cnpj", "DT_REFER": "_dfp_data", "valor": "_dfp_valor"}
    )

    acumulado_atual = trimestral[
        trimestral["ORDEM_EXERC"].eq("ÚLTIMO")
        & trimestral["DT_INI_EXERC"].dt.month.eq(1)
        & trimestral["DT_INI_EXERC"].dt.day.eq(1)
    ].copy()
    acumulado_anterior = trimestral[
        trimestral["ORDEM_EXERC"].eq("PENÚLTIMO")
        & trimestral["DT_INI_EXERC"].dt.month.eq(1)
        & trimestral["DT_INI_EXERC"].dt.day.eq(1)
    ].copy()
    if not acumulado_atual.empty:
        acumulado = acumulado_atual.merge(
            acumulado_anterior[["CNPJ_CIA", "DT_REFER", "valor"]].rename(
                columns={"valor": "_itr_anterior"}
            ),
            on=["CNPJ_CIA", "DT_REFER"],
            how="left",
            validate="one_to_one",
        )
        acumulado = acumulado.rename(columns={"valor": "_itr_atual"})
        acumulado = acumulado.merge(
            base[["cnpj", "_dfp_data"]],
            left_on="CNPJ_CIA",
            right_on="cnpj",
            how="inner",
        )
        acumulado = acumulado[acumulado["DT_REFER"].gt(acumulado["_dfp_data"])]
        acumulado = acumulado.sort_values(["CNPJ_CIA", "DT_REFER"]).drop_duplicates(
            "CNPJ_CIA", keep="last"
        )
        base = base.merge(
            acumulado[["CNPJ_CIA", "_itr_atual", "_itr_anterior"]],
            left_on="cnpj",
            right_on="CNPJ_CIA",
            how="left",
        ).drop(columns="CNPJ_CIA")
    else:
        base["_itr_atual"] = np.nan
        base["_itr_anterior"] = np.nan
    base[f"{nome}_ttm"] = [
        calcular_ttm(dfp_valor, itr_atual, itr_anterior)
        for dfp_valor, itr_atual, itr_anterior in zip(
            base["_dfp_valor"], base["_itr_atual"], base["_itr_anterior"], strict=True
        )
    ]

    if nome in {"receita", "lucro"}:
        historico = anual[["CNPJ_CIA", "DT_REFER", "valor"]].copy()
        historico["ano"] = historico["DT_REFER"].dt.year
        atual = base[["cnpj", "_dfp_data", "_dfp_valor"]].copy()
        atual["ano_5a"] = atual["_dfp_data"].dt.year - 5
        atual = atual.merge(
            historico[["CNPJ_CIA", "ano", "valor"]],
            left_on=["cnpj", "ano_5a"],
            right_on=["CNPJ_CIA", "ano"],
            how="left",
        )
        base[f"{nome}_dfp_atual"] = atual["_dfp_valor"].to_numpy()
        base[f"{nome}_dfp_5a"] = atual["valor"].to_numpy()
    colunas = ["cnpj", f"{nome}_ttm"]
    colunas += [
        coluna
        for coluna in (f"{nome}_dfp_atual", f"{nome}_dfp_5a")
        if coluna in base
    ]
    return base[colunas]


def _documentos_balanco(
    bpa: pd.DataFrame,
    bpp: pd.DataFrame,
) -> pd.DataFrame:
    chaves = ["CNPJ_CIA", "DT_REFER", "ORDEM_EXERC"]

    def extrair(
        quadro: pd.DataFrame,
        contas: Mapping[str, list],
        sufixo: str,
    ) -> pd.DataFrame:
        if quadro.empty:
            return pd.DataFrame(
                columns=[
                    "CNPJ_CIA",
                    "DT_REFER",
                    f"data_entrega_{sufixo}",
                    f"empresa_cvm_{sufixo}",
                    *contas,
                ]
            )
        quadro = quadro[quadro["ORDEM_EXERC"].eq("ÚLTIMO")].copy()
        documentos = (
            quadro.sort_values("DT_RECEB")
            .groupby(["CNPJ_CIA", "DT_REFER"], as_index=False)
            .agg(data_entrega=("DT_RECEB", "max"), empresa_cvm=("DENOM_CIA", "last"))
        )
        for nome, alternativas in contas.items():
            linhas = _extrair_prioridade(quadro, alternativas, chaves=chaves)
            valores = linhas[["CNPJ_CIA", "DT_REFER", "valor"]].rename(
                columns={"valor": nome}
            )
            documentos = documentos.merge(
                valores,
                on=["CNPJ_CIA", "DT_REFER"],
                how="left",
                validate="one_to_one",
            )
        return documentos.rename(
            columns={
                "data_entrega": f"data_entrega_{sufixo}",
                "empresa_cvm": f"empresa_cvm_{sufixo}",
            }
        )

    ativos = extrair(bpa, CONTAS_BPA, "bpa")
    passivos = extrair(bpp, CONTAS_BPP, "bpp")
    documentos = ativos.merge(
        passivos,
        on=["CNPJ_CIA", "DT_REFER"],
        how="outer",
        suffixes=("_bpa", "_bpp"),
        validate="one_to_one",
    )
    documentos["data_entrega"] = documentos.get("data_entrega_bpa").combine_first(
        documentos.get("data_entrega_bpp")
    )
    documentos["empresa_cvm"] = documentos.get("empresa_cvm_bpa").combine_first(
        documentos.get("empresa_cvm_bpp")
    )
    return documentos.drop(
        columns=[
            coluna
            for coluna in (
                "data_entrega_bpa",
                "data_entrega_bpp",
                "empresa_cvm_bpa",
                "empresa_cvm_bpp",
            )
            if coluna in documentos
        ]
    )


def _balanco_empresas(
    dfp: Mapping[str, tuple[pd.DataFrame, pd.DataFrame]],
    itr: Mapping[str, tuple[pd.DataFrame, pd.DataFrame]],
    referencia: pd.Timestamp,
) -> pd.DataFrame:
    documentos = []
    for origem in (dfp, itr):
        bpa = _preparar_relatorio(origem.get("BPA"), referencia)
        bpp = _preparar_relatorio(origem.get("BPP"), referencia)
        documentos.append(_documentos_balanco(bpa, bpp))
    balancos = pd.concat(documentos, ignore_index=True, sort=False)
    if balancos.empty:
        return pd.DataFrame(columns=["cnpj", "data_balanco", "data_entrega"])
    balancos["DT_REFER"] = pd.to_datetime(balancos["DT_REFER"], errors="coerce")
    balancos["data_entrega"] = pd.to_datetime(balancos["data_entrega"], errors="coerce")
    balancos = balancos.sort_values(["CNPJ_CIA", "DT_REFER", "data_entrega"])
    balancos = balancos.drop_duplicates("CNPJ_CIA", keep="last")
    balancos["pl_controladores"] = [
        calcular_pl_controladores(pl, participacao)
        for pl, participacao in zip(
            balancos.get("pl_consolidado"),
            balancos.get("participacao_nao_controladores"),
            strict=True,
        )
    ]
    return balancos.rename(columns={"CNPJ_CIA": "cnpj", "DT_REFER": "data_balanco"})


def _linhas_proventos_dfc(quadro: pd.DataFrame) -> pd.DataFrame:
    if quadro.empty:
        return pd.DataFrame(
            {
                "CNPJ_CIA": pd.Series(dtype=str),
                "DT_REFER": pd.Series(dtype="datetime64[ns]"),
                "ORDEM_EXERC": pd.Series(dtype=str),
                "DT_INI_EXERC": pd.Series(dtype="datetime64[ns]"),
                "valor": pd.Series(dtype=float),
            }
        )
    descricao = quadro["descricao_normalizada"]
    pagamento = descricao.str.contains(
        r"DIVIDEND|JCP|JUROS (?:SOBRE|S/O?)\s*.*CAPITAL",
        regex=True,
        na=False,
    )
    exclusao = descricao.str.contains(
        r"NAO CONTROLADOR|RECEBID|RECEB",
        regex=True,
        na=False,
    )
    linhas = quadro[
        quadro["CD_CONTA"].astype(str).str.startswith("6.03") & pagamento & ~exclusao
    ].copy()
    linhas["valor"] = linhas["valor"].abs()
    chaves = ["CNPJ_CIA", "DT_REFER", "ORDEM_EXERC", "DT_INI_EXERC"]
    return linhas.groupby(chaves, as_index=False, dropna=False)["valor"].sum(min_count=1)


def _proventos_dfc_empresas(dfp: pd.DataFrame, itr: pd.DataFrame) -> pd.DataFrame:
    anual = _linhas_proventos_dfc(dfp)
    trimestral = _linhas_proventos_dfc(itr)
    if anual.empty:
        return pd.DataFrame(columns=["cnpj", "proventos", "alertas_contabeis"])
    anual = anual[
        anual["ORDEM_EXERC"].eq("ÚLTIMO")
        & anual["DT_INI_EXERC"].dt.month.eq(1)
        & anual["DT_INI_EXERC"].dt.day.eq(1)
    ].copy()
    ultimo = (
        anual.sort_values(["CNPJ_CIA", "DT_REFER"])
        .drop_duplicates("CNPJ_CIA", keep="last")
        .rename(
            columns={
                "CNPJ_CIA": "cnpj",
                "DT_REFER": "_dfp_data",
                "valor": "_dfp_valor",
            }
        )
    )
    base = ultimo[["cnpj", "_dfp_data", "_dfp_valor"]].copy()
    acumulado_atual = trimestral[
        trimestral["ORDEM_EXERC"].eq("ÚLTIMO")
        & trimestral["DT_INI_EXERC"].dt.month.eq(1)
        & trimestral["DT_INI_EXERC"].dt.day.eq(1)
    ].copy()
    acumulado_anterior = trimestral[
        trimestral["ORDEM_EXERC"].eq("PENÚLTIMO")
        & trimestral["DT_INI_EXERC"].dt.month.eq(1)
        & trimestral["DT_INI_EXERC"].dt.day.eq(1)
    ].copy()
    if not acumulado_atual.empty:
        acumulado = acumulado_atual.merge(
            acumulado_anterior[["CNPJ_CIA", "DT_REFER", "valor"]].rename(
                columns={"valor": "_itr_anterior"}
            ),
            on=["CNPJ_CIA", "DT_REFER"],
            how="left",
            validate="one_to_one",
        ).rename(columns={"valor": "_itr_atual"})
        acumulado = acumulado.merge(
            base[["cnpj", "_dfp_data"]],
            left_on="CNPJ_CIA",
            right_on="cnpj",
            how="inner",
        )
        acumulado = (
            acumulado[acumulado["DT_REFER"].gt(acumulado["_dfp_data"])]
            .sort_values(["CNPJ_CIA", "DT_REFER"])
            .drop_duplicates("CNPJ_CIA", keep="last")
        )
        base = base.merge(
            acumulado[["CNPJ_CIA", "_itr_atual", "_itr_anterior"]],
            left_on="cnpj",
            right_on="CNPJ_CIA",
            how="left",
        ).drop(columns="CNPJ_CIA")
    else:
        base["_itr_atual"] = np.nan
        base["_itr_anterior"] = np.nan
    base["proventos"] = [
        calcular_ttm(dfp_valor, itr_atual, itr_anterior)
        for dfp_valor, itr_atual, itr_anterior in zip(
            base["_dfp_valor"], base["_itr_atual"], base["_itr_anterior"], strict=True
        )
    ]
    base.loc[base["proventos"].lt(0), "proventos"] = np.nan
    base["alertas_contabeis"] = [[] for _ in range(len(base))]
    return base[["cnpj", "proventos", "alertas_contabeis"]]


def _proventos_dva_empresas(dva: pd.DataFrame) -> pd.DataFrame:
    if dva.empty:
        return pd.DataFrame(columns=["cnpj", "proventos", "alertas_contabeis"])
    quadro = dva[dva["ORDEM_EXERC"].eq("ÚLTIMO")].copy()
    quadro = quadro[
        mascara_conta(
            quadro,
            ("7.08.04.01", "7.08.04.02"),
            (r"JUROS.*CAPITAL PROPRIO", r"DIVIDENDOS"),
        )
    ]
    somas = (
        quadro.groupby(["CNPJ_CIA", "DT_REFER"], as_index=False)["valor"]
        .sum(min_count=1)
        .sort_values(["CNPJ_CIA", "DT_REFER"])
        .drop_duplicates("CNPJ_CIA", keep="last")
        .rename(columns={"CNPJ_CIA": "cnpj", "valor": "proventos"})
    )
    somas.loc[somas["proventos"].lt(0), "proventos"] = np.nan
    somas["alertas_contabeis"] = [["dy_dva"] for _ in range(len(somas))]
    return somas[["cnpj", "proventos", "alertas_contabeis"]]


def _proventos_empresas(
    dfc_dfp: pd.DataFrame,
    dfc_itr: pd.DataFrame,
    dva_dfp: pd.DataFrame,
) -> pd.DataFrame:
    por_dfc = _proventos_dfc_empresas(dfc_dfp, dfc_itr)
    por_dva = _proventos_dva_empresas(dva_dfp)
    if not por_dfc.empty:
        por_dva = por_dva[~por_dva["cnpj"].isin(por_dfc["cnpj"])]
    return pd.concat([por_dfc, por_dva], ignore_index=True, sort=False)


def _capital_empresas(
    dfp: pd.DataFrame,
    itr: pd.DataFrame,
    referencia: pd.Timestamp,
) -> pd.DataFrame:
    capital = pd.concat(
        [selecionar_versoes(dfp, referencia), selecionar_versoes(itr, referencia)],
        ignore_index=True,
        sort=False,
    )
    if capital.empty:
        return pd.DataFrame(columns=["cnpj", "quantidade_on", "quantidade_pn"])

    def numero(coluna: str) -> pd.Series:
        if coluna not in capital:
            return pd.Series(np.nan, index=capital.index)
        return pd.to_numeric(capital[coluna], errors="coerce")

    capital["quantidade_on"] = numero("QT_ACAO_ORDIN_CAP_INTEGR") - numero(
        "QT_ACAO_ORDIN_TESOURO"
    ).fillna(0)
    capital["quantidade_pn"] = numero("QT_ACAO_PREF_CAP_INTEGR") - numero(
        "QT_ACAO_PREF_TESOURO"
    ).fillna(0)
    capital = capital.sort_values(["CNPJ_CIA", "DT_REFER", "DT_RECEB"]).drop_duplicates(
        "CNPJ_CIA", keep="last"
    )
    return capital.rename(columns={"CNPJ_CIA": "cnpj"})[
        ["cnpj", "quantidade_on", "quantidade_pn"]
    ]


def construir_base_contabil(
    dfp: Mapping[str, tuple[pd.DataFrame, ...] | pd.DataFrame],
    itr: Mapping[str, tuple[pd.DataFrame, ...] | pd.DataFrame],
    data_referencia: str | pd.Timestamp,
) -> pd.DataFrame:
    """Produz uma linha point-in-time por companhia, antes das cotações."""
    referencia = pd.Timestamp(data_referencia)
    dfp_rel = {chave: valor for chave, valor in dfp.items() if chave != "CAPITAL"}
    itr_rel = {chave: valor for chave, valor in itr.items() if chave != "CAPITAL"}
    dre_dfp = _preparar_relatorio(dfp_rel.get("DRE"), referencia)
    dre_itr = _preparar_relatorio(itr_rel.get("DRE"), referencia)
    fluxos = [_fluxo_empresa(dre_dfp, dre_itr, nome) for nome in CONTAS_FLUXO]
    base = fluxos[0]
    for fluxo in fluxos[1:]:
        base = base.merge(fluxo, on="cnpj", how="outer", validate="one_to_one")
    balanco = _balanco_empresas(dfp_rel, itr_rel, referencia)
    base = base.merge(balanco, on="cnpj", how="outer", validate="one_to_one")
    dva = _preparar_relatorio(dfp_rel.get("DVA"), referencia)
    dfc_dfp = _preparar_dfc(dfp_rel.get("DFC"), referencia)
    dfc_itr = _preparar_dfc(itr_rel.get("DFC"), referencia)
    base = base.merge(
        _proventos_empresas(dfc_dfp, dfc_itr, dva),
        on="cnpj",
        how="outer",
        validate="one_to_one",
    )
    return base


def _classe_ticker(ticker: str) -> str | None:
    casamento = re.search(r"(\d{1,2})$", ticker)
    if not casamento:
        return None
    codigo = int(casamento.group(1))
    if codigo == 3:
        return "ON"
    if codigo in {4, 5, 6}:
        return "PN"
    if codigo == 11:
        return "UNT"
    return None


def _composicoes_unit(fca: pd.DataFrame) -> pd.DataFrame:
    colunas = ["cnpj", "acoes_por_unit"]
    necessarias = {"CNPJ_Companhia", "Codigo_Negociacao", "Composicao_BDR_Unit"}
    if fca.empty or not necessarias.issubset(fca.columns):
        return pd.DataFrame(columns=colunas)
    quadro = fca.copy()
    quadro["ticker"] = quadro["Codigo_Negociacao"].fillna("").str.upper().str.strip()
    quadro = quadro[quadro["ticker"].str.endswith("11")].copy()
    quadro["acoes_por_unit"] = quadro["Composicao_BDR_Unit"].map(parsear_acoes_por_unit)
    quadro = quadro[quadro["acoes_por_unit"].notna()].copy()
    if quadro.empty:
        return pd.DataFrame(columns=colunas)
    quadro["_data"] = pd.to_datetime(quadro.get("Data_Referencia"), errors="coerce")
    quadro["_versao"] = pd.to_numeric(quadro.get("Versao"), errors="coerce")
    quadro["_ano_fca"] = pd.to_numeric(quadro.get("_ano_fca"), errors="coerce")
    quadro = quadro.sort_values(["_data", "_versao", "_ano_fca"], na_position="first")
    return quadro.drop_duplicates("CNPJ_Companhia", keep="last").rename(
        columns={"CNPJ_Companhia": "cnpj"}
    )[colunas]


def _capital_e_mercado(
    tickers: pd.DataFrame,
    capital: pd.DataFrame,
    contabil: pd.DataFrame,
    composicoes_unit: pd.DataFrame,
) -> pd.DataFrame:
    cotacoes = tickers[tickers["cnpj"].notna()].copy()
    cotacoes["classe"] = cotacoes["ticker"].map(_classe_ticker)
    precos: dict[str, dict[str, float]] = {}
    for cnpj, grupo in cotacoes.groupby("cnpj"):
        por_liquidez = grupo.sort_values("liquidez_media_diaria", ascending=False)
        registro: dict[str, float] = {}
        for classe in ("ON", "PN", "UNT"):
            candidatos = por_liquidez[por_liquidez["classe"].eq(classe)]
            registro[f"preco_{classe.lower()}"] = (
                float(candidatos.iloc[0]["preco"]) if not candidatos.empty else np.nan
            )
        referencias = por_liquidez[por_liquidez["classe"].isin(["ON", "PN"])]
        registro["preco_referencia"] = (
            float(referencias.iloc[0]["preco"])
            if not referencias.empty
            else registro["preco_unt"]
        )
        precos[str(cnpj)] = registro

    capital_indexado = capital.set_index("cnpj") if not capital.empty else pd.DataFrame()
    contabil_indexado = contabil.set_index("cnpj") if not contabil.empty else pd.DataFrame()
    units_indexadas = (
        composicoes_unit.set_index("cnpj") if not composicoes_unit.empty else pd.DataFrame()
    )
    linhas = []
    for cnpj, registro_precos in precos.items():
        if not capital_indexado.empty and cnpj in capital_indexado.index:
            registro_capital = capital_indexado.loc[cnpj]
            quantidade_on = registro_capital["quantidade_on"]
            quantidade_pn = registro_capital["quantidade_pn"]
        else:
            quantidade_on = quantidade_pn = np.nan
        alertas_mercado: list[str] = []
        sem_preco_classes = pd.isna(registro_precos["preco_on"]) and pd.isna(
            registro_precos["preco_pn"]
        )
        if sem_preco_classes and not units_indexadas.empty and cnpj in units_indexadas.index:
            acoes_por_unit = float(units_indexadas.loc[cnpj, "acoes_por_unit"])
            preco_unit = registro_precos["preco_unt"]
            if acoes_por_unit > 0 and not pd.isna(preco_unit):
                preco_equivalente = float(preco_unit) / acoes_por_unit
                registro_precos["preco_on"] = preco_equivalente
                registro_precos["preco_pn"] = preco_equivalente
                registro_precos["preco_referencia"] = preco_equivalente
                alertas_mercado.append("mcap_por_unit")
        pl = (
            contabil_indexado.loc[cnpj, "pl_controladores"]
            if not contabil_indexado.empty and cnpj in contabil_indexado.index
            else np.nan
        )
        on, pn, alertas = corrigir_quantidade_acoes(
            quantidade_on,
            quantidade_pn,
            pl,
            registro_precos["preco_referencia"],
        )
        alertas = sorted(set(alertas + alertas_mercado))
        valor_mercado = calcular_valor_mercado(
            on,
            pn,
            registro_precos["preco_on"],
            registro_precos["preco_pn"],
        )
        if "escala_suspeita" in alertas:
            valor_mercado = np.nan
        linhas.append(
            {
                "cnpj": cnpj,
                "acoes_on": on,
                "acoes_pn": pn,
                "acoes_total": on + pn if on + pn > 0 else np.nan,
                "valor_mercado": valor_mercado,
                "alertas_capital": alertas,
            }
        )
    return pd.DataFrame(linhas)


def _cadastro_empresas(cadastro: pd.DataFrame) -> pd.DataFrame:
    if cadastro.empty:
        return pd.DataFrame(columns=["cnpj", "empresa_cadastro", "setor"])
    colunas = ["CNPJ_CIA", "DENOM_COMERC", "DENOM_SOCIAL", "SETOR_ATIV"]
    quadro = cadastro[[coluna for coluna in colunas if coluna in cadastro]].copy()
    quadro["empresa_cadastro"] = quadro.get("DENOM_COMERC").replace("", np.nan).combine_first(
        quadro.get("DENOM_SOCIAL")
    )
    return quadro.rename(columns={"CNPJ_CIA": "cnpj", "SETOR_ATIV": "setor"})[
        ["cnpj", "empresa_cadastro", "setor"]
    ].drop_duplicates("cnpj", keep="last")


def construir_tabela_acoes(
    cotacoes: pd.DataFrame,
    fca: pd.DataFrame,
    cadastro: pd.DataFrame,
    dfp: Mapping[str, tuple[pd.DataFrame, ...] | pd.DataFrame],
    itr: Mapping[str, tuple[pd.DataFrame, ...] | pd.DataFrame],
    *,
    data_referencia: str | pd.Timestamp,
    liquidez_minima: float = 100_000,
    minimo_pregoes: int = 40,
) -> pd.DataFrame:
    """Monta a saída final, uma linha por ticker elegível."""
    universo = selecionar_universo(
        cotacoes,
        data_referencia=data_referencia,
        liquidez_minima=liquidez_minima,
        minimo_pregoes=minimo_pregoes,
    )
    tickers = mapear_tickers(universo, fca, cadastro)
    contabil = construir_base_contabil(dfp, itr, data_referencia)
    capital = _capital_empresas(
        dfp.get("CAPITAL", pd.DataFrame()),
        itr.get("CAPITAL", pd.DataFrame()),
        pd.Timestamp(data_referencia),
    )
    mercado = _capital_e_mercado(tickers, capital, contabil, _composicoes_unit(fca))
    resultado = tickers.merge(contabil, on="cnpj", how="left", validate="many_to_one")
    resultado = resultado.merge(mercado, on="cnpj", how="left", validate="many_to_one")
    resultado = resultado.merge(
        _cadastro_empresas(cadastro), on="cnpj", how="left", validate="many_to_one"
    )
    resultado["empresa"] = (
        resultado.get("empresa_cadastro")
        .combine_first(resultado.get("empresa_fca"))
        .combine_first(resultado.get("empresa_cvm"))
        .combine_first(resultado["empresa_b3"])
    )
    setor_normalizado = resultado["setor"].map(texto_normalizado)
    setor_financeiro = setor_normalizado.str.contains(
        r"BANCOS|SEGURADORAS|INTERMEDIACAO FINANCEIRA",
        regex=True,
        na=False,
    )
    sem_ativo_circulante = resultado["ativo_total"].notna() & resultado[
        "ativo_circulante"
    ].isna()
    resultado["financeira"] = setor_financeiro | sem_ativo_circulante
    resultado["alertas"] = [
        sorted(
            set(
                _serie_alertas(originais)
                + _serie_alertas(capital_alertas)
                + _serie_alertas(contabeis)
            )
        )
        for originais, capital_alertas, contabeis in zip(
            resultado["alertas"],
            resultado.get("alertas_capital"),
            resultado.get("alertas_contabeis"),
            strict=True,
        )
    ]
    resultado = calcular_metricas_tabela(resultado)
    colunas = [
        "ticker",
        "empresa",
        "cnpj",
        "origem_cnpj",
        "setor",
        "financeira",
        "data_balanco",
        "data_entrega",
        "alertas",
        *COLUNAS_METRICAS,
    ]
    for coluna in colunas:
        if coluna not in resultado:
            resultado[coluna] = np.nan
    return resultado[colunas].sort_values("ticker", kind="stable").reset_index(drop=True)
