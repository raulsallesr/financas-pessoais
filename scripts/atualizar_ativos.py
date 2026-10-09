"""Gera tabelas derivadas de ações e FIIs a partir do cache oficial local.

Uso:
    python -m scripts.atualizar_ativos --classe todos --liquidez-minima 100000
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from ativos.adapters import b3_cotahist, cvm
from ativos.core.pipeline_acoes import construir_tabela_acoes
from ativos.core.pipeline_fiis import construir_tabela_fiis
from ativos.paths import cache_bruto_dir, dados_derivados_dir

SCHEMA_VERSION_ACOES = 2
SCHEMA_VERSION_FIIS = 2
# Compatibilidade com consumidores e testes da primeira fatia vertical.
SCHEMA_VERSION = SCHEMA_VERSION_ACOES

COLUNAS_DEMONSTRACAO = [
    "CNPJ_CIA",
    "DT_REFER",
    "VERSAO",
    "DENOM_CIA",
    "ESCALA_MOEDA",
    "ORDEM_EXERC",
    "DT_INI_EXERC",
    "DT_FIM_EXERC",
    "CD_CONTA",
    "DS_CONTA",
    "VL_CONTA",
]
COLUNAS_BALANCO = [coluna for coluna in COLUNAS_DEMONSTRACAO if coluna != "DT_INI_EXERC"]
COLUNAS_CAPITAL = [
    "CNPJ_CIA",
    "DT_REFER",
    "VERSAO",
    "DENOM_CIA",
    "QT_ACAO_ORDIN_CAP_INTEGR",
    "QT_ACAO_PREF_CAP_INTEGR",
    "QT_ACAO_TOTAL_CAP_INTEGR",
    "QT_ACAO_ORDIN_TESOURO",
    "QT_ACAO_PREF_TESOURO",
    "QT_ACAO_TOTAL_TESOURO",
]
CODIGOS_RELATORIO = {
    "DRE": {"3.01", "3.03", "3.05", "3.09", "3.09.01", "3.11", "3.11.01", "3.13"},
    "BPA": {"1", "1.01", "1.01.01", "1.01.02"},
    "BPP": {
        "2",
        "2.01",
        "2.02",
        "2.01.04",
        "2.02.01",
        "2.03",
        "2.03.09",
        "2.05",
        "2.07",
        "2.07.02",
        "2.08",
        "2.08.09",
    },
    "DFC_MI": {"6.03"},
    "DFC_MD": {"6.03"},
    "DVA": {"7.08.04.01", "7.08.04.02"},
}


def _anos_disponiveis(pasta: Path, padrao: str) -> list[int]:
    expressao = re.compile(padrao, re.IGNORECASE)
    anos = []
    for caminho in pasta.iterdir():
        casamento = expressao.fullmatch(caminho.name)
        if casamento:
            anos.append(int(casamento.group(1)))
    return sorted(set(anos))


def _ler_relatorios(
    tipo: str,
    anos: list[int],
    relatorio: str,
    *,
    pasta: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    colunas = (
        COLUNAS_DEMONSTRACAO
        if relatorio in {"DRE", "DFC_MI", "DFC_MD", "DVA"}
        else COLUNAS_BALANCO
    )
    por_origem: dict[bool, list[pd.DataFrame]] = {True: [], False: []}
    for ano in anos:
        for consolidado in (True, False):
            quadro = cvm.ler_relatorio(
                tipo,
                ano,
                relatorio,
                consolidado=consolidado,
                pasta=pasta,
                colunas=colunas,
            )
            if relatorio.startswith("DFC_"):
                quadro = quadro[quadro["CD_CONTA"].astype(str).str.startswith("6.03")]
            else:
                quadro = quadro[quadro["CD_CONTA"].isin(CODIGOS_RELATORIO[relatorio])]
            por_origem[consolidado].append(quadro)
    vazia = pd.DataFrame(columns=colunas + ["DT_RECEB"])
    return tuple(
        pd.concat(por_origem[consolidado], ignore_index=True, sort=False)
        if por_origem[consolidado]
        else vazia.copy()
        for consolidado in (True, False)
    )


def _ler_dfc(
    tipo: str,
    anos: list[int],
    *,
    pasta: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    mi_con, mi_ind = _ler_relatorios(tipo, anos, "DFC_MI", pasta=pasta)
    md_con, md_ind = _ler_relatorios(tipo, anos, "DFC_MD", pasta=pasta)
    return mi_con, md_con, mi_ind, md_ind


def _ler_capital(tipo: str, anos: list[int], pasta: Path) -> pd.DataFrame:
    quadros = [
        cvm.ler_relatorio(
            tipo,
            ano,
            "composicao_capital",
            consolidado=None,
            pasta=pasta,
            colunas=COLUNAS_CAPITAL,
        )
        for ano in anos
    ]
    return pd.concat(quadros, ignore_index=True, sort=False) if quadros else pd.DataFrame()


def _carregar_demonstracoes(
    pasta: Path,
    data_referencia: pd.Timestamp,
) -> tuple[dict[str, object], dict[str, object]]:
    anos_dfp = [
        ano
        for ano in _anos_disponiveis(pasta, r"dfp_cia_aberta_(\d{4})\.zip")
        if ano <= data_referencia.year
    ]
    anos_itr = [
        ano
        for ano in _anos_disponiveis(pasta, r"itr_cia_aberta_(\d{4})\.zip")
        if ano <= data_referencia.year
    ]
    if not anos_dfp:
        raise FileNotFoundError("Nenhum DFP anual foi encontrado no cache bruto")
    anos_balanco_dfp = anos_dfp[-2:]
    anos_itr = anos_itr[-2:]
    dfp: dict[str, object] = {
        "DRE": _ler_relatorios("dfp", anos_dfp, "DRE", pasta=pasta),
        "BPA": _ler_relatorios("dfp", anos_balanco_dfp, "BPA", pasta=pasta),
        "BPP": _ler_relatorios("dfp", anos_balanco_dfp, "BPP", pasta=pasta),
        "DFC": _ler_dfc("dfp", anos_balanco_dfp, pasta=pasta),
        "DVA": _ler_relatorios("dfp", anos_balanco_dfp, "DVA", pasta=pasta),
        "CAPITAL": _ler_capital("dfp", anos_balanco_dfp, pasta),
    }
    itr: dict[str, object] = {
        "DRE": _ler_relatorios("itr", anos_itr, "DRE", pasta=pasta),
        "BPA": _ler_relatorios("itr", anos_itr, "BPA", pasta=pasta),
        "BPP": _ler_relatorios("itr", anos_itr, "BPP", pasta=pasta),
        "DFC": _ler_dfc("itr", anos_itr, pasta=pasta),
        "DVA": _ler_relatorios("itr", anos_itr, "DVA", pasta=pasta),
        "CAPITAL": _ler_capital("itr", anos_itr, pasta),
    }
    return dfp, itr


def _gravar_atomico(caminho: Path, gravar) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(f".{caminho.name}.part")
    try:
        gravar(temporario)
        os.replace(temporario, caminho)
    finally:
        temporario.unlink(missing_ok=True)


def _executar_acoes(
    *,
    data_referencia: str | None = None,
    liquidez_minima: float = 100_000,
    pasta_bruta: Path | None = None,
    pasta_derivada: Path | None = None,
    minimo_pregoes: int = 40,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Executa o pipeline local, persiste Parquet/JSON e devolve os resultados."""
    pasta_bruta = Path(pasta_bruta or cache_bruto_dir())
    pasta_derivada = Path(pasta_derivada or dados_derivados_dir())
    anos_cotahist = _anos_disponiveis(pasta_bruta, r"COTAHIST_A(\d{4})\.ZIP")
    if not anos_cotahist:
        raise FileNotFoundError("Nenhum COTAHIST anual foi encontrado no cache bruto")
    if data_referencia is not None:
        limite = pd.Timestamp(data_referencia)
        anos_cotahist = [ano for ano in anos_cotahist if ano <= limite.year]
    anos_cotahist = anos_cotahist[-2:]
    cotacoes = pd.concat(
        [
            b3_cotahist.ler_cotahist(ano, pasta=pasta_bruta, apenas_acoes=True)
            for ano in anos_cotahist
        ],
        ignore_index=True,
        sort=False,
    )
    limite = pd.Timestamp(data_referencia) if data_referencia else cotacoes["data"].max()
    cotacoes = cotacoes[cotacoes["data"].le(limite)].copy()
    if cotacoes.empty:
        raise ValueError(f"Não há cotação disponível até {limite.date().isoformat()}")

    anos_fca = [
        ano
        for ano in _anos_disponiveis(pasta_bruta, r"fca_cia_aberta_(\d{4})\.zip")
        if ano <= limite.year
    ][-2:]
    fca = pd.concat(
        [cvm.ler_fca(ano, pasta=pasta_bruta) for ano in anos_fca],
        ignore_index=True,
        sort=False,
    )
    cadastro = cvm.ler_cadastro(pasta=pasta_bruta)
    dfp, itr = _carregar_demonstracoes(pasta_bruta, limite)
    tabela = construir_tabela_acoes(
        cotacoes,
        fca,
        cadastro,
        dfp,
        itr,
        data_referencia=limite,
        liquidez_minima=liquidez_minima,
        minimo_pregoes=minimo_pregoes,
    )
    pendencias = tabela.loc[
        tabela["alertas"].map(lambda alertas: "sem_cnpj" in alertas), "ticker"
    ].tolist()
    cobertura_pl = float(tabela["p_l"].notna().mean()) if len(tabela) else 0.0
    cobertura_dy = float(tabela["dy"].notna().mean()) if len(tabela) else 0.0
    resolvidos_por_nome = tabela.loc[
        tabela["origem_cnpj"].eq("nome"), "ticker"
    ].tolist()
    meta = {
        "schema_version": SCHEMA_VERSION_ACOES,
        "data_cotacao": cotacoes["data"].max().date().isoformat(),
        "gerado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "linhas": len(tabela),
        "liquidez_minima": liquidez_minima,
        "cobertura_p_l": cobertura_pl,
        "cobertura_dy": cobertura_dy,
        "pendencias_ticker": pendencias,
        "tickers_resolvidos_por_nome": resolvidos_por_nome,
    }
    caminho_parquet = pasta_derivada / "acoes.parquet"
    caminho_meta = pasta_derivada / "acoes_meta.json"
    _gravar_atomico(caminho_parquet, lambda caminho: tabela.to_parquet(caminho, index=False))
    _gravar_atomico(
        caminho_meta,
        lambda caminho: caminho.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        ),
    )
    return tabela, meta


def _concatenar_informes(
    tipo: str,
    anos: list[int],
    quadro: str,
    *,
    pasta: Path,
) -> pd.DataFrame:
    partes = [
        cvm.ler_informe_fii(tipo, ano, quadro, pasta=pasta)
        for ano in anos
    ]
    return pd.concat(partes, ignore_index=True, sort=False) if partes else pd.DataFrame()


def _carregar_informes_fii(
    pasta: Path,
    data_referencia: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    anos_mensais = [
        ano
        for ano in _anos_disponiveis(pasta, r"inf_mensal_fii_(\d{4})\.zip")
        if ano <= data_referencia.year
    ]
    anos_trimestrais = [
        ano
        for ano in _anos_disponiveis(pasta, r"inf_trimestral_fii_(\d{4})\.zip")
        if ano <= data_referencia.year
    ]
    if not anos_mensais:
        raise FileNotFoundError("Nenhum informe mensal de FII foi encontrado no cache bruto")
    if not anos_trimestrais:
        raise FileNotFoundError("Nenhum informe trimestral de FII foi encontrado no cache bruto")
    anos_mensais = anos_mensais[-2:]
    anos_trimestrais = anos_trimestrais[-2:]
    return (
        _concatenar_informes("mensal", anos_mensais, "geral", pasta=pasta),
        _concatenar_informes("mensal", anos_mensais, "complemento", pasta=pasta),
        _concatenar_informes("mensal", anos_mensais, "ativo_passivo", pasta=pasta),
        _concatenar_informes("trimestral", anos_trimestrais, "imovel", pasta=pasta),
    )


def _executar_fiis(
    *,
    data_referencia: str | None = None,
    liquidez_minima: float = 100_000,
    pasta_bruta: Path | None = None,
    pasta_derivada: Path | None = None,
    minimo_pregoes: int = 40,
) -> tuple[pd.DataFrame, dict[str, object]]:
    pasta_bruta = Path(pasta_bruta or cache_bruto_dir())
    pasta_derivada = Path(pasta_derivada or dados_derivados_dir())
    anos_cotahist = _anos_disponiveis(pasta_bruta, r"COTAHIST_A(\d{4})\.ZIP")
    if not anos_cotahist:
        raise FileNotFoundError("Nenhum COTAHIST anual foi encontrado no cache bruto")
    if data_referencia is not None:
        limite_inicial = pd.Timestamp(data_referencia)
        anos_cotahist = [ano for ano in anos_cotahist if ano <= limite_inicial.year]
    cotacoes = pd.concat(
        [
            b3_cotahist.ler_cotahist(ano, pasta=pasta_bruta, apenas_fiis=True)
            for ano in anos_cotahist[-2:]
        ],
        ignore_index=True,
        sort=False,
    )
    if cotacoes.empty:
        raise ValueError("Não há cotações de FII no cache bruto")
    limite = pd.Timestamp(data_referencia) if data_referencia else cotacoes["data"].max()
    cotacoes = cotacoes[cotacoes["data"].le(limite)].copy()
    if cotacoes.empty:
        raise ValueError(f"Não há cotação de FII disponível até {limite.date().isoformat()}")
    geral, complemento, ativo_passivo, imovel = _carregar_informes_fii(
        pasta_bruta, limite
    )
    tabela, diagnostico = construir_tabela_fiis(
        cotacoes,
        geral,
        complemento,
        ativo_passivo,
        imovel,
        data_referencia=limite,
        liquidez_minima=liquidez_minima,
        minimo_pregoes=minimo_pregoes,
    )
    cobertura_p_vp = float(tabela["p_vp"].notna().mean()) if len(tabela) else 0.0
    cobertura_dy = float(tabela["dy_12m"].notna().mean()) if len(tabela) else 0.0
    cobertura_vacancia = float(tabela["vacancia"].notna().mean()) if len(tabela) else 0.0
    contagem_tipo = {
        str(tipo): int(contagem)
        for tipo, contagem in tabela["tipo"].value_counts(dropna=False).sort_index().items()
    }
    fundos_dy_suspeito = int(
        tabela["alertas"].map(lambda alertas: "dy_dados_suspeitos" in alertas).sum()
    )
    meta = {
        "schema_version": SCHEMA_VERSION_FIIS,
        "data_cotacao": cotacoes["data"].max().date().isoformat(),
        "gerado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "linhas": len(tabela),
        "liquidez_minima": liquidez_minima,
        "cobertura_p_vp": cobertura_p_vp,
        "cobertura_dy_12m": cobertura_dy,
        "cobertura_vacancia": cobertura_vacancia,
        "fundos_com_alerta_dy_dados_suspeitos": fundos_dy_suspeito,
        **diagnostico,
        "contagem_por_tipo": contagem_tipo,
    }
    _gravar_atomico(
        pasta_derivada / "fiis.parquet",
        lambda caminho: tabela.to_parquet(caminho, index=False),
    )
    _gravar_atomico(
        pasta_derivada / "fiis_meta.json",
        lambda caminho: caminho.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        ),
    )
    return tabela, meta


def executar(
    *,
    classe: str = "acoes",
    data_referencia: str | None = None,
    liquidez_minima: float = 100_000,
    pasta_bruta: Path | None = None,
    pasta_derivada: Path | None = None,
    minimo_pregoes: int = 40,
) -> tuple[pd.DataFrame, dict[str, object]] | dict[
    str, tuple[pd.DataFrame, dict[str, object]]
]:
    """Executa uma classe ou ambas; a omissão na API preserva o contrato de ações."""
    argumentos = {
        "data_referencia": data_referencia,
        "liquidez_minima": liquidez_minima,
        "pasta_bruta": pasta_bruta,
        "pasta_derivada": pasta_derivada,
        "minimo_pregoes": minimo_pregoes,
    }
    if classe == "acoes":
        return _executar_acoes(**argumentos)
    if classe == "fiis":
        return _executar_fiis(**argumentos)
    if classe == "todos":
        return {
            "acoes": _executar_acoes(**argumentos),
            "fiis": _executar_fiis(**argumentos),
        }
    raise ValueError(f"Classe desconhecida: {classe}")


def _formatar_resumo(meta: dict[str, object]) -> str:
    pendencias = meta["pendencias_ticker"]
    lista = ", ".join(pendencias) if pendencias else "nenhuma"
    cobertura = float(meta["cobertura_p_l"]) * 100
    cobertura_dy = float(meta["cobertura_dy"]) * 100
    return (
        f"Universo: {meta['linhas']} tickers\n"
        f"Cobertura de P/L: {cobertura:.1f}%\n"
        f"Cobertura de DY: {cobertura_dy:.1f}%\n"
        f"Pendências de ticker: {lista}"
    )


def _formatar_resumo_fiis(meta: dict[str, object]) -> str:
    pendencias = meta["pendencias_ticker"]
    lista = ", ".join(pendencias) if pendencias else "nenhuma"
    tipos = ", ".join(
        f"{tipo}: {contagem}" for tipo, contagem in meta["contagem_por_tipo"].items()
    )
    return (
        f"Universo: {meta['linhas']} FIIs\n"
        f"Cobertura de P/VP: {float(meta['cobertura_p_vp']) * 100:.1f}%\n"
        f"Cobertura de DY 12m: {float(meta['cobertura_dy_12m']) * 100:.1f}%\n"
        f"Cobertura de vacância: {float(meta['cobertura_vacancia']) * 100:.1f}%\n"
        "Fundos com DY/rentabilidade suspeitos: "
        f"{meta['fundos_com_alerta_dy_dados_suspeitos']}\n"
        f"Pendências de ticker: {lista}\n"
        f"Contagem por tipo: {tipos or 'nenhuma'}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", dest="data_referencia", help="Data limite AAAA-MM-DD")
    parser.add_argument("--liquidez-minima", type=float, default=100_000)
    parser.add_argument("--classe", choices=("acoes", "fiis", "todos"), default="todos")
    argumentos = parser.parse_args()
    resultado = executar(
        classe=argumentos.classe,
        data_referencia=argumentos.data_referencia,
        liquidez_minima=argumentos.liquidez_minima,
    )
    if isinstance(resultado, tuple):
        _, meta = resultado
        formatador = _formatar_resumo_fiis if argumentos.classe == "fiis" else _formatar_resumo
        print(formatador(meta))
        return
    for indice, classe in enumerate(("acoes", "fiis")):
        if indice:
            print()
        print(f"[{classe.upper()}]")
        _, meta = resultado[classe]
        print(_formatar_resumo(meta) if classe == "acoes" else _formatar_resumo_fiis(meta))


if __name__ == "__main__":  # pragma: no cover - invocação do módulo
    main()
