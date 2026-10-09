"""Pipeline puro da busca de fundos imobiliários."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping

import numpy as np
import pandas as pd

from ativos.core.metricas_fiis import (
    COLUNAS_METRICAS_FII,
    agregar_imoveis,
    calcular_composicao,
    calcular_metricas_mensais,
    calcular_metricas_snapshot,
)

COLUNAS_FIIS = (
    "ticker",
    "nome",
    "cnpj",
    "segmento",
    "tipo",
    "gestao",
    *COLUNAS_METRICAS_FII,
    "meses_informe",
    "data_informe",
    "alertas",
)

PALAVRAS_GENERICAS_NOME_FII = {
    "CLASSE",
    "DE",
    "FII",
    "FUNDO",
    "IMOBILIARIO",
    "INVESTIMENTO",
    "LTDA",
    "RESP",
    "RL",
    "SA",
}


def _serie_alertas(valor: object) -> list[str]:
    if isinstance(valor, np.ndarray):
        return [str(item) for item in valor.tolist()]
    if isinstance(valor, (list, tuple)):
        return [str(item) for item in valor]
    return []


def selecionar_universo_fiis(
    cotacoes: pd.DataFrame,
    *,
    data_referencia: str | pd.Timestamp | None = None,
    liquidez_minima: float = 100_000,
    minimo_pregoes: int = 40,
) -> pd.DataFrame:
    """Seleciona FIIs líquidos e conserva preço, nome e ISIN da última cotação."""
    colunas = [
        "ticker",
        "nome_b3",
        "isin",
        "preco",
        "liquidez_media_diaria",
        "data_cotacao",
        "alertas",
    ]
    if cotacoes.empty:
        return pd.DataFrame(columns=colunas)
    quadro = cotacoes.copy()
    quadro["data"] = pd.to_datetime(quadro["data"], errors="coerce")
    limite = pd.Timestamp(data_referencia) if data_referencia is not None else quadro["data"].max()
    quadro = quadro[
        quadro["data"].le(limite)
        & quadro["codbdi"].eq("12")
        & quadro["especi"].fillna("").str.strip().str.upper().str.startswith("CI")
    ].copy()
    if quadro.empty:
        return pd.DataFrame(columns=colunas)
    datas = quadro["data"].dropna().drop_duplicates().sort_values().tail(63)
    janela = quadro[quadro["data"].isin(set(datas))].copy()
    janela["teve_negocio"] = pd.to_numeric(janela["totneg"], errors="coerce").gt(0)
    janela["volume"] = pd.to_numeric(janela["volume"], errors="coerce")
    liquidez = janela.groupby("ticker", as_index=False).agg(
        liquidez_media_diaria=("volume", "mean"),
        pregoes_com_negocio=("teve_negocio", "sum"),
    )
    ultimas = (
        quadro.sort_values(["ticker", "data"])
        .drop_duplicates("ticker", keep="last")
        .rename(columns={"nomres": "nome_b3", "data": "data_cotacao"})
    )
    universo = ultimas.merge(liquidez, on="ticker", how="left", validate="one_to_one")
    universo = universo[
        universo["liquidez_media_diaria"].ge(liquidez_minima)
        & universo["pregoes_com_negocio"].ge(minimo_pregoes)
    ].copy()
    universo["alertas"] = [[] for _ in range(len(universo))]
    return universo[colunas].reset_index(drop=True)


def selecionar_ultima_versao(quadro: pd.DataFrame) -> pd.DataFrame:
    """Mantém todas as linhas pertencentes à maior versão de cada fundo e mês."""
    if quadro.empty:
        return quadro.copy()
    resultado = quadro.copy()
    resultado["Data_Referencia"] = pd.to_datetime(
        resultado["Data_Referencia"], errors="coerce"
    )
    resultado["_versao_numero"] = pd.to_numeric(resultado["Versao"], errors="coerce")
    maior = resultado.groupby(
        ["CNPJ_Fundo_Classe", "Data_Referencia"], dropna=False
    )["_versao_numero"].transform("max")
    resultado = resultado[resultado["_versao_numero"].eq(maior)].copy()
    return resultado.drop(columns="_versao_numero")


def _isin(valor: object) -> str | None:
    if valor is None or pd.isna(valor):
        return None
    normalizado = str(valor).strip().upper()
    return normalizado or None


def _mapa_unico(quadro: pd.DataFrame, chave: str) -> dict[str, str]:
    pares = quadro.dropna(subset=[chave, "CNPJ_Fundo_Classe"])[
        [chave, "CNPJ_Fundo_Classe"]
    ].drop_duplicates()
    contagem = pares.groupby(chave)["CNPJ_Fundo_Classe"].nunique()
    unicos = set(contagem[contagem.eq(1)].index)
    return (
        pares[pares[chave].isin(unicos)]
        .drop_duplicates(chave, keep="last")
        .set_index(chave)["CNPJ_Fundo_Classe"]
        .to_dict()
    )


def _palavras_nome_fii(valor: object) -> set[str]:
    if valor is None or pd.isna(valor):
        return set()
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", str(valor))
        if not unicodedata.combining(caractere)
    ).upper()
    palavras = re.sub(r"[^A-Z0-9]+", " ", sem_acentos).split()
    return {palavra for palavra in palavras if palavra not in PALAVRAS_GENERICAS_NOME_FII}


def _candidatos_por_chave(quadro: pd.DataFrame, chave: str) -> dict[str, list[str]]:
    pares = quadro.dropna(subset=[chave, "CNPJ_Fundo_Classe"])[
        [chave, "CNPJ_Fundo_Classe"]
    ].drop_duplicates()
    return {
        str(valor): sorted(grupo["CNPJ_Fundo_Classe"].astype(str).unique().tolist())
        for valor, grupo in pares.groupby(chave, sort=True)
    }


def _desempatar_por_nome(
    candidatos: list[str],
    nome_pregao: object,
    nomes_por_cnpj: Mapping[str, object],
) -> tuple[str | None, str | None]:
    palavras_pregao = _palavras_nome_fii(nome_pregao)
    pontuacoes = {
        cnpj: len(palavras_pregao & _palavras_nome_fii(nomes_por_cnpj.get(cnpj)))
        for cnpj in candidatos
    }
    maior = max(pontuacoes.values(), default=0)
    if maior == 0:
        return None, "sem_palavra_em_comum"
    vencedores = [cnpj for cnpj, pontos in pontuacoes.items() if pontos == maior]
    if len(vencedores) != 1:
        return None, "empate_nome"
    return vencedores[0], None


def mapear_tickers_fiis(universo: pd.DataFrame, geral: pd.DataFrame) -> pd.DataFrame:
    """Liga ticker a classe por ISIN, com desempate nominal estrito em colisões."""
    resultado = universo.copy()
    if resultado.empty:
        resultado["cnpj"] = pd.Series(dtype=object)
        resultado["origem_cnpj"] = pd.Series(dtype=object)
        resultado["motivo_pendencia"] = pd.Series(dtype=object)
        return resultado
    cadastro = selecionar_ultima_versao(geral)
    if "Tipo_Fundo_Classe" in cadastro:
        cadastro = cadastro[
            cadastro["Tipo_Fundo_Classe"].fillna("").str.strip().str.casefold().eq("classe")
        ]
    cadastro = cadastro.copy()
    cadastro["_isin"] = cadastro["Codigo_ISIN"].map(_isin)
    cadastro["_raiz_isin"] = cadastro["_isin"].str[2:6]
    candidatos_exatos = _candidatos_por_chave(cadastro, "_isin")
    raizes = _mapa_unico(cadastro, "_raiz_isin")
    candidatos_raiz = _candidatos_por_chave(cadastro, "_raiz_isin")
    cadastro_recente = (
        cadastro.sort_values(["CNPJ_Fundo_Classe", "Data_Referencia"], kind="stable")
        .drop_duplicates("CNPJ_Fundo_Classe", keep="last")
        .set_index("CNPJ_Fundo_Classe")
    )
    nomes_por_cnpj = cadastro_recente["Nome_Fundo_Classe"].to_dict()

    cnpjs = []
    origens = []
    motivos = []
    nomes_pregao = resultado.get("nome_b3", resultado["ticker"])
    for valor, nome_pregao in zip(resultado["isin"], nomes_pregao, strict=True):
        codigo = _isin(valor)
        cnpj = None
        origem = None
        motivo = None
        if not codigo:
            motivo = "isin_ausente"
        else:
            candidatos = candidatos_exatos.get(codigo, [])
            if len(candidatos) == 1:
                cnpj = candidatos[0]
                origem = "isin"
            elif len(candidatos) > 1:
                cnpj, motivo = _desempatar_por_nome(
                    candidatos, nome_pregao, nomes_por_cnpj
                )
                origem = "isin_nome" if cnpj else None
            elif len(codigo) >= 6:
                raiz = codigo[2:6]
                cnpj = raizes.get(raiz)
                if cnpj:
                    origem = "raiz_isin"
                elif len(candidatos_raiz.get(raiz, [])) > 1:
                    motivo = "raiz_isin_ambigua"
                else:
                    motivo = "sem_informe_mensal"
            else:
                motivo = "sem_informe_mensal"
        cnpjs.append(cnpj)
        origens.append(origem)
        motivos.append(motivo)
    resultado["cnpj"] = cnpjs
    resultado["origem_cnpj"] = origens
    resultado["motivo_pendencia"] = motivos
    resultado["alertas"] = [
        _serie_alertas(alertas) + ([] if pd.notna(cnpj) else ["sem_cnpj"])
        for alertas, cnpj in zip(resultado["alertas"], resultado["cnpj"], strict=True)
    ]
    return resultado


def _diagnostico_mapeamento(mapeados: pd.DataFrame) -> dict[str, object]:
    pendentes = (
        mapeados.loc[mapeados["cnpj"].isna(), ["ticker", "motivo_pendencia"]]
        .sort_values("ticker", kind="stable")
        .to_dict(orient="records")
    )
    detalhes = [
        {"ticker": str(item["ticker"]), "motivo": str(item["motivo_pendencia"])}
        for item in pendentes
    ]
    resolvidos = (
        mapeados.loc[mapeados["origem_cnpj"].eq("isin_nome"), "ticker"]
        .astype(str)
        .sort_values(kind="stable")
        .tolist()
    )
    return {
        "pendencias_ticker": [item["ticker"] for item in detalhes],
        "pendencias_ticker_detalhes": detalhes,
        "tickers_resolvidos_por_desempate_nome": resolvidos,
    }


def mes_referencia_cobertura(complemento: pd.DataFrame) -> pd.Timestamp | pd.NaT:
    """Acha o mês mais recente cuja cobertura alcança 80% do pico observado."""
    if complemento.empty:
        return pd.NaT
    contagens = complemento.groupby("Data_Referencia")["CNPJ_Fundo_Classe"].nunique()
    if contagens.empty:
        return pd.NaT
    completas = contagens[contagens.ge(contagens.max() * 0.80)]
    return completas.index.max() if not completas.empty else contagens.index.max()


def _ultimo_por_fundo(quadro: pd.DataFrame) -> pd.DataFrame:
    if quadro.empty:
        return quadro.copy()
    return (
        quadro.sort_values(["CNPJ_Fundo_Classe", "Data_Referencia"])
        .drop_duplicates("CNPJ_Fundo_Classe", keep="last")
        .copy()
    )


def _meses_entre(mais_novo: pd.Timestamp, mais_antigo: pd.Timestamp) -> int:
    return (mais_novo.year - mais_antigo.year) * 12 + mais_novo.month - mais_antigo.month


def _preparar_quadro(
    quadro: pd.DataFrame,
    limite: pd.Timestamp,
    *,
    fundo_classe: bool = False,
) -> pd.DataFrame:
    resultado = selecionar_ultima_versao(quadro)
    if resultado.empty:
        return resultado
    resultado = resultado[resultado["Data_Referencia"].le(limite)].copy()
    if fundo_classe and "Tipo_Fundo_Classe" in resultado:
        resultado = resultado[
            resultado["Tipo_Fundo_Classe"].fillna("").str.strip().str.casefold().eq("classe")
        ]
    return resultado


def construir_tabela_fiis(
    cotacoes: pd.DataFrame,
    geral: pd.DataFrame,
    complemento: pd.DataFrame,
    ativo_passivo: pd.DataFrame,
    imovel: pd.DataFrame,
    *,
    data_referencia: str | pd.Timestamp,
    liquidez_minima: float = 100_000,
    minimo_pregoes: int = 40,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Monta uma linha por ticker elegível e devolve o diagnóstico do casamento."""
    limite = pd.Timestamp(data_referencia)
    universo = selecionar_universo_fiis(
        cotacoes,
        data_referencia=limite,
        liquidez_minima=liquidez_minima,
        minimo_pregoes=minimo_pregoes,
    )
    geral_limpo = _preparar_quadro(geral, limite, fundo_classe=True)
    mapeados = mapear_tickers_fiis(universo, geral_limpo)
    diagnostico = _diagnostico_mapeamento(mapeados)
    mapeados = mapeados[mapeados["cnpj"].notna()].copy()
    if mapeados.empty:
        return pd.DataFrame(columns=COLUNAS_FIIS), diagnostico

    complemento_limpo = _preparar_quadro(complemento, limite)
    ativo_limpo = _preparar_quadro(ativo_passivo, limite)
    imovel_limpo = _preparar_quadro(imovel, limite)
    mes_completo = mes_referencia_cobertura(complemento_limpo)

    geral_ultimo = _ultimo_por_fundo(geral_limpo)[
        [
            "CNPJ_Fundo_Classe",
            "Nome_Fundo_Classe",
            "Segmento_Atuacao",
            "Tipo_Gestao",
        ]
    ]
    complemento_ultimo = _ultimo_por_fundo(complemento_limpo).rename(
        columns={"Data_Referencia": "data_informe"}
    )
    ativo_ultimo = _ultimo_por_fundo(ativo_limpo).rename(
        columns={"Data_Referencia": "data_ativo_passivo"}
    )
    resultado = mapeados.merge(
        geral_ultimo,
        left_on="cnpj",
        right_on="CNPJ_Fundo_Classe",
        how="left",
        validate="many_to_one",
    ).drop(columns="CNPJ_Fundo_Classe")
    resultado = resultado.merge(
        complemento_ultimo,
        left_on="cnpj",
        right_on="CNPJ_Fundo_Classe",
        how="left",
        validate="many_to_one",
    ).drop(columns="CNPJ_Fundo_Classe")
    resultado = resultado.merge(
        ativo_ultimo,
        left_on="cnpj",
        right_on="CNPJ_Fundo_Classe",
        how="left",
        validate="many_to_one",
        suffixes=("", "_ativo"),
    ).drop(columns="CNPJ_Fundo_Classe")

    composicao = resultado.apply(calcular_composicao, axis=1, result_type="expand")
    snapshot = resultado.apply(calcular_metricas_snapshot, axis=1, result_type="expand")
    resultado = pd.concat([resultado, composicao, snapshot], axis=1)

    historicos = {
        cnpj: grupo for cnpj, grupo in complemento_limpo.groupby("CNPJ_Fundo_Classe")
    }
    mensais = pd.DataFrame(
        [
            calcular_metricas_mensais(historicos.get(cnpj, pd.DataFrame()), preco)
            for cnpj, preco in zip(resultado["cnpj"], resultado["preco"], strict=True)
        ],
        index=resultado.index,
    )
    resultado = pd.concat([resultado, mensais], axis=1)

    imoveis_por_fundo: Mapping[str, pd.DataFrame] = {
        cnpj: grupo for cnpj, grupo in imovel_limpo.groupby("CNPJ_Fundo_Classe")
    }
    agregados_imoveis = []
    for cnpj, tipo, pct_imoveis in zip(
        resultado["cnpj"], resultado["tipo"], resultado["pct_imoveis"], strict=True
    ):
        tem_imoveis = pd.notna(pct_imoveis) and pct_imoveis > 0 and tipo not in {
            "Papel",
            "Fundo de fundos",
        }
        agregados_imoveis.append(
            agregar_imoveis(imoveis_por_fundo.get(cnpj, pd.DataFrame()))
            if tem_imoveis
            else agregar_imoveis(pd.DataFrame())
        )
    resultado = pd.concat(
        [resultado, pd.DataFrame(agregados_imoveis, index=resultado.index)], axis=1
    )

    alertas_finais = []
    for linha in resultado.to_dict(orient="records"):
        alertas = _serie_alertas(linha.get("alertas"))
        data_informe = linha.get("data_informe")
        if (
            pd.notna(mes_completo)
            and pd.notna(data_informe)
            and _meses_entre(pd.Timestamp(mes_completo), pd.Timestamp(data_informe)) > 2
        ):
            alertas.append("pl_defasado")
        if linha.get("dy_parcial"):
            alertas.append("dy_parcial")
        if linha.get("fundo_novo"):
            alertas.append("fundo_novo")
        if linha.get("dy_dados_suspeitos"):
            alertas.append("dy_dados_suspeitos")
        p_vp = linha.get("p_vp")
        if pd.notna(p_vp) and (p_vp < 0.3 or p_vp > 3):
            alertas.append("p_vp_extremo")
        alertas_finais.append(sorted(set(alertas)))
    resultado["alertas"] = alertas_finais

    renomear = {
        "Nome_Fundo_Classe": "nome",
        "Segmento_Atuacao": "segmento",
        "Tipo_Gestao": "gestao",
        "Patrimonio_Liquido": "patrimonio_liquido",
        "Cotas_Emitidas": "cotas_emitidas",
        "Valor_Patrimonial_Cotas": "vp_cota",
        "Total_Numero_Cotistas": "cotistas",
        "Percentual_Despesas_Taxa_Administracao": "taxa_adm",
    }
    resultado = resultado.rename(columns=renomear)
    resultado["nome"] = resultado["nome"].fillna(resultado["nome_b3"])
    for coluna in COLUNAS_METRICAS_FII:
        if coluna in resultado:
            resultado[coluna] = pd.to_numeric(resultado[coluna], errors="coerce")
    for coluna in COLUNAS_FIIS:
        if coluna not in resultado:
            resultado[coluna] = np.nan
    return (
        resultado[list(COLUNAS_FIIS)]
        .sort_values("ticker", kind="stable")
        .reset_index(drop=True),
        diagnostico,
    )
