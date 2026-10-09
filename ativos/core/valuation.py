"""Modelos puros e vetorizados de valor estimado para ações e FIIs."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from ativos.core.premissas import PremissasValuation

COLUNAS_AVALIACAO = (
    "valor_central",
    "faixa_baixa",
    "faixa_alta",
    "margem_seguranca",
    "n_modelos",
    "situacao_faixa",
)
COLUNAS_MODELOS_ACOES = (
    "modelo_graham",
    "modelo_bazin",
    "modelo_gordon",
    "modelo_multiplos_setor",
)
COLUNAS_MODELOS_FIIS = (
    "modelo_patrimonial",
    "modelo_renda_capitalizada",
)
LIMITE_P_L_MODELOS_VALOR = 25.0
LIMITE_P_VP_MODELOS_VALOR = 6.0

ALERTAS_DADOS_VALUATION = {
    "dy_dados_suspeitos",
    "escala_suspeita",
    "salto_preco",
    "pl_defasado",
}


def _numeros(quadro: pd.DataFrame, coluna: str) -> pd.Series:
    if coluna not in quadro:
        return pd.Series(np.nan, index=quadro.index, dtype=float)
    return pd.to_numeric(quadro[coluna], errors="coerce").astype(float)


def _alertas(valor: object) -> list[str]:
    if isinstance(valor, np.ndarray):
        return [str(item) for item in valor.tolist()]
    if isinstance(valor, (list, tuple, set)):
        return [str(item) for item in valor]
    return []


def consolidar_modelos(
    modelos: pd.DataFrame,
    preco: pd.Series | Sequence[float] | float,
    alertas: pd.Series | Sequence[object] | None = None,
) -> pd.DataFrame:
    """Consolida modelos aplicáveis em P25–P75, mediana e posição do preço."""
    valores = modelos.apply(pd.to_numeric, errors="coerce")
    n_modelos = valores.notna().sum(axis=1).astype(int)
    suficiente = n_modelos.ge(2)
    faixa_baixa = valores.quantile(0.25, axis=1, interpolation="linear").where(suficiente)
    faixa_alta = valores.quantile(0.75, axis=1, interpolation="linear").where(suficiente)
    valor_central = valores.median(axis=1, skipna=True).where(suficiente)

    if isinstance(preco, pd.Series):
        precos = pd.to_numeric(preco.reindex(valores.index), errors="coerce")
    elif np.isscalar(preco):
        precos = pd.Series(preco, index=valores.index, dtype=float)
    else:
        precos = pd.to_numeric(pd.Series(preco, index=valores.index), errors="coerce")
    margem = (valor_central / precos - 1).where(precos.gt(0) & suficiente)

    situacao = pd.Series(None, index=valores.index, dtype=object)
    situacao.loc[suficiente & precos.lt(faixa_baixa)] = "abaixo da faixa"
    situacao.loc[suficiente & precos.gt(faixa_alta)] = "acima da faixa"
    dentro = suficiente & precos.ge(faixa_baixa) & precos.le(faixa_alta)
    situacao.loc[dentro] = "dentro da faixa"

    minimo = valores.min(axis=1, skipna=True)
    maximo = valores.max(axis=1, skipna=True)
    dispersao = n_modelos.eq(2) & minimo.gt(0) & (maximo / minimo).gt(3)
    alertas_dados = pd.Series(False, index=valores.index)
    if alertas is not None:
        serie_alertas = (
            alertas.reindex(valores.index)
            if isinstance(alertas, pd.Series)
            else pd.Series(alertas, index=valores.index)
        )
        alertas_dados = serie_alertas.map(
            lambda itens: bool(ALERTAS_DADOS_VALUATION.intersection(_alertas(itens)))
        )
    return pd.DataFrame(
        {
            "valor_central": valor_central,
            "faixa_baixa": faixa_baixa,
            "faixa_alta": faixa_alta,
            "margem_seguranca": margem,
            "n_modelos": n_modelos,
            "situacao_faixa": situacao,
            "valuation_fragil": (dispersao | alertas_dados).astype(bool),
        },
        index=valores.index,
    )


def _estatisticas_pares(quadro: pd.DataFrame) -> pd.DataFrame:
    colunas = (
        "mediana_p_l_setor",
        "pares_p_l_setor",
        "mediana_p_vp_setor",
        "pares_p_vp_setor",
    )
    if quadro.empty or "cnpj" not in quadro:
        return pd.DataFrame(index=quadro.index, columns=colunas)
    empresas = quadro[quadro["cnpj"].notna()].copy()
    if empresas.empty:
        return pd.DataFrame(index=quadro.index, columns=colunas)
    empresas["_liquidez"] = _numeros(empresas, "liquidez_media_diaria")
    empresas = empresas.sort_values("_liquidez", ascending=False).drop_duplicates("cnpj")
    empresas["_financeira"] = empresas.get(
        "financeira", pd.Series(False, index=empresas.index)
    ).fillna(False).astype(bool)
    setor = empresas.get("setor", pd.Series(index=empresas.index, dtype=object))
    empresas["_grupo"] = setor.astype(object)
    sem_setor = empresas["_grupo"].isna() | empresas["_grupo"].astype(str).str.strip().eq("")
    empresas.loc[sem_setor, "_grupo"] = (
        "__SEM_SETOR__" + empresas.loc[sem_setor, "cnpj"].astype(str)
    )
    empresas.loc[empresas["_financeira"], "_grupo"] = "__FINANCEIRAS__"
    empresas["p_l"] = _numeros(empresas, "p_l")
    empresas["p_vp"] = _numeros(empresas, "p_vp")

    alvos = empresas[["cnpj", "_grupo"]].rename(columns={"cnpj": "cnpj_alvo"})
    pares = empresas[["cnpj", "_grupo", "p_l", "p_vp"]].rename(
        columns={"cnpj": "cnpj_par"}
    )
    cruzado = alvos.merge(pares, on="_grupo", how="left")
    cruzado = cruzado[cruzado["cnpj_alvo"].ne(cruzado["cnpj_par"])]
    base = pd.DataFrame(index=empresas["cnpj"].astype(str).unique())
    for metrica, nome_mediana, nome_contagem in (
        ("p_l", "mediana_p_l_setor", "pares_p_l_setor"),
        ("p_vp", "mediana_p_vp_setor", "pares_p_vp_setor"),
    ):
        validos = cruzado[cruzado[metrica].gt(0)]
        if validos.empty:
            base[nome_mediana] = np.nan
            base[nome_contagem] = 0
            continue
        agrupado = validos.groupby("cnpj_alvo")[metrica].agg(["median", "count"])
        base[nome_mediana] = agrupado["median"]
        base[nome_contagem] = agrupado["count"]
    base.index.name = "cnpj"

    resultado = pd.DataFrame(index=quadro.index)
    chaves = quadro["cnpj"].astype(str)
    for coluna in colunas:
        resultado[coluna] = chaves.map(base[coluna])
    resultado["pares_p_l_setor"] = resultado["pares_p_l_setor"].fillna(0).astype(int)
    resultado["pares_p_vp_setor"] = resultado["pares_p_vp_setor"].fillna(0).astype(int)
    return resultado


def calcular_valuation_acoes(
    quadro: pd.DataFrame,
    premissas: PremissasValuation,
) -> pd.DataFrame:
    """Calcula os quatro modelos de ações e a faixa sem alterar a base recebida."""
    resultado = quadro.copy()
    lpa = _numeros(resultado, "lpa")
    vpa = _numeros(resultado, "vpa")
    dpa = _numeros(resultado, "dpa")

    graham_valido = lpa.gt(0) & vpa.gt(0)
    produto_graham = (premissas.graham_mult * lpa * vpa).where(graham_valido)
    resultado["modelo_graham"] = np.sqrt(produto_graham)
    resultado["status_graham"] = np.select(
        [lpa.isna(), lpa.le(0), vpa.isna(), vpa.le(0)],
        [
            "não se aplica: LPA ausente",
            "não se aplica: LPA não positivo",
            "não se aplica: VPA ausente",
            "não se aplica: VPA não positivo",
        ],
        default="aplicável",
    )

    bazin_valido = dpa.gt(0) & (premissas.bazin_taxa > 0)
    resultado["modelo_bazin"] = (dpa / premissas.bazin_taxa).where(bazin_valido)
    resultado["status_bazin"] = np.select(
        [dpa.isna(), dpa.le(0), pd.Series(premissas.bazin_taxa <= 0, index=resultado.index)],
        [
            "não se aplica: DPA ausente",
            "não se aplica: DPA não positivo",
            "não se aplica: taxa mínima não positiva",
        ],
        default="aplicável",
    )

    diferenca = premissas.k - premissas.g
    gordon_valido = dpa.gt(0) & (diferenca >= 0.04)
    resultado["modelo_gordon"] = (
        dpa * (1 + premissas.g) / diferenca if diferenca != 0 else np.nan
    )
    resultado["modelo_gordon"] = _numeros(resultado, "modelo_gordon").where(
        gordon_valido
    )
    resultado["status_gordon"] = np.select(
        [dpa.isna(), dpa.le(0), pd.Series(diferenca < 0.04, index=resultado.index)],
        [
            "não se aplica: DPA ausente",
            "não se aplica: DPA não positivo",
            "não se aplica: diferença entre k e g abaixo de 4 p.p.",
        ],
        default="aplicável",
    )

    pares = _estatisticas_pares(resultado)
    resultado = pd.concat([resultado, pares], axis=1)
    parcela_lpa = (
        lpa * resultado["mediana_p_l_setor"]
    ).where(
        lpa.gt(0)
        & resultado["mediana_p_l_setor"].gt(0)
        & resultado["pares_p_l_setor"].ge(premissas.min_pares_setor)
    )
    parcela_vpa = (
        vpa * resultado["mediana_p_vp_setor"]
    ).where(
        vpa.gt(0)
        & resultado["mediana_p_vp_setor"].gt(0)
        & resultado["pares_p_vp_setor"].ge(premissas.min_pares_setor)
    )
    parcelas = pd.concat([parcela_lpa, parcela_vpa], axis=1)
    resultado["modelo_multiplos_setor"] = parcelas.mean(axis=1, skipna=True).where(
        parcelas.notna().any(axis=1)
    )
    resultado["status_multiplos_setor"] = np.where(
        resultado["modelo_multiplos_setor"].notna(),
        "aplicável",
        f"não se aplica: menos de {premissas.min_pares_setor} pares setoriais válidos",
    )

    modelos = resultado[list(COLUNAS_MODELOS_ACOES)]
    consolidados = consolidar_modelos(
        modelos,
        _numeros(resultado, "preco"),
        resultado["alertas"] if "alertas" in resultado else None,
    )
    for coluna in consolidados:
        resultado[coluna] = consolidados[coluna]
    # Graham, Bazin, Gordon e múltiplos medem valor e renda atuais: empresas com
    # múltiplos altos (WEGE3: P/L 35) ficam bem abaixo do preço sem que isso diga
    # algo sobre o crescimento que o mercado precifica. Sinaliza, não corrige.
    resultado["modelos_valor_limitados"] = (
        (_numeros(resultado, "p_l") > LIMITE_P_L_MODELOS_VALOR)
        | (_numeros(resultado, "p_vp") > LIMITE_P_VP_MODELOS_VALOR)
    ).fillna(False)
    return resultado


def calcular_valuation_fiis(
    quadro: pd.DataFrame,
    premissas: PremissasValuation,
) -> pd.DataFrame:
    """Calcula os modelos patrimonial e de renda e consolida a faixa dos FIIs."""
    resultado = quadro.copy()
    vp_cota = _numeros(resultado, "vp_cota")
    rendimento = _numeros(resultado, "rendimento_12m_cota")
    resultado["modelo_patrimonial"] = vp_cota.where(vp_cota.gt(0))
    resultado["status_patrimonial"] = np.select(
        [vp_cota.isna(), vp_cota.le(0)],
        ["não se aplica: VP/cota ausente", "não se aplica: VP/cota não positivo"],
        default="aplicável",
    )
    taxa = premissas.fii_taxa_exigida
    resultado["modelo_renda_capitalizada"] = (
        rendimento / taxa if taxa > 0 else np.nan
    )
    resultado["modelo_renda_capitalizada"] = _numeros(
        resultado, "modelo_renda_capitalizada"
    ).where(rendimento.gt(0) & (taxa > 0))
    resultado["status_renda_capitalizada"] = np.select(
        [rendimento.isna(), rendimento.le(0), pd.Series(taxa <= 0, index=resultado.index)],
        [
            "não se aplica: rendimento de 12 meses ausente",
            "não se aplica: rendimento de 12 meses não positivo",
            "não se aplica: taxa exigida não positiva",
        ],
        default="aplicável",
    )
    consolidados = consolidar_modelos(
        resultado[list(COLUNAS_MODELOS_FIIS)],
        _numeros(resultado, "preco"),
        resultado["alertas"] if "alertas" in resultado else None,
    )
    for coluna in consolidados:
        resultado[coluna] = consolidados[coluna]
    return resultado


def tabela_modelos_acao(
    linha: pd.Series | dict[str, Any],
    premissas: PremissasValuation,
) -> pd.DataFrame:
    """Explica valor, fórmula, premissas e status de cada modelo de ação."""
    registro = dict(linha)
    return pd.DataFrame(
        [
            {
                "Modelo": "Graham",
                "Valor": registro.get("modelo_graham"),
                "Fórmula": "raiz de (multiplicador × LPA × VPA)",
                "Premissas": f"multiplicador = {premissas.graham_mult:.2f}",
                "Status": registro.get("status_graham"),
            },
            {
                "Modelo": "Bazin",
                "Valor": registro.get("modelo_bazin"),
                "Fórmula": "DPA dividido pela taxa mínima",
                "Premissas": f"taxa mínima = {premissas.bazin_taxa:.2%}",
                "Status": registro.get("status_bazin"),
            },
            {
                "Modelo": "Gordon",
                "Valor": registro.get("modelo_gordon"),
                "Fórmula": "DPA × (1 + g) dividido por (k − g)",
                "Premissas": f"k = {premissas.k:.2%}; g = {premissas.g:.2%}",
                "Status": registro.get("status_gordon"),
            },
            {
                "Modelo": "Múltiplos do setor",
                "Valor": registro.get("modelo_multiplos_setor"),
                "Fórmula": "média das parcelas por P/L e P/VP setoriais aplicáveis",
                "Premissas": (
                    f"mínimo = {premissas.min_pares_setor} pares; "
                    f"pares P/L = {int(registro.get('pares_p_l_setor', 0) or 0)}; "
                    f"pares P/VP = {int(registro.get('pares_p_vp_setor', 0) or 0)}"
                ),
                "Status": registro.get("status_multiplos_setor"),
            },
        ]
    )


def tabela_modelos_fii(
    linha: pd.Series | dict[str, Any],
    premissas: PremissasValuation,
) -> pd.DataFrame:
    """Explica os dois modelos aplicáveis a fundos imobiliários."""
    registro = dict(linha)
    return pd.DataFrame(
        [
            {
                "Modelo": "Patrimonial",
                "Valor": registro.get("modelo_patrimonial"),
                "Fórmula": "valor patrimonial por cota",
                "Premissas": "último informe mensal disponível",
                "Status": registro.get("status_patrimonial"),
            },
            {
                "Modelo": "Renda capitalizada",
                "Valor": registro.get("modelo_renda_capitalizada"),
                "Fórmula": "rendimento de 12 meses por cota dividido pela taxa exigida",
                "Premissas": f"taxa exigida = {premissas.fii_taxa_exigida:.2%}",
                "Status": registro.get("status_renda_capitalizada"),
            },
        ]
    )


def sensibilidade_gordon(
    dpa: float,
    premissas: PremissasValuation,
    *,
    valores_k: Sequence[float] | None = None,
    valores_g: Sequence[float] | None = None,
) -> pd.DataFrame:
    """Grade k × g do modelo de Gordon; combinações frágeis permanecem vazias."""
    ks = list(valores_k or (premissas.k - 0.02, premissas.k, premissas.k + 0.02))
    gs = list(valores_g or (premissas.g - 0.01, premissas.g, premissas.g + 0.01))
    linhas: dict[str, list[float]] = {}
    dpa_numero = float(dpa) if pd.notna(dpa) else np.nan
    for k in ks:
        valores = []
        for g in gs:
            valores.append(
                dpa_numero * (1 + g) / (k - g)
                if dpa_numero > 0 and k - g >= 0.04
                else np.nan
            )
        linhas[f"k {k:.2%}"] = valores
    quadro = pd.DataFrame(linhas, index=[f"g {g:.2%}" for g in gs])
    quadro.index.name = "Crescimento"
    return quadro


def sensibilidade_taxa(
    valor_base: float,
    taxa_central: float,
    *,
    taxas: Sequence[float] | None = None,
) -> pd.DataFrame:
    """Sensibilidade de um valor capitalizado por taxa, usada por Bazin e FIIs."""
    taxas_usadas = list(taxas or (taxa_central - 0.02, taxa_central, taxa_central + 0.02))
    base = float(valor_base) if pd.notna(valor_base) else np.nan
    return pd.DataFrame(
        {
            "Taxa": taxas_usadas,
            "Valor": [base / taxa if base > 0 and taxa > 0 else np.nan for taxa in taxas_usadas],
        }
    )
