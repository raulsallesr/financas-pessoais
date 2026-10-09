import json
import sys

import pandas as pd
import pytest

from scripts import atualizar_ativos


def _tabela_final():
    return pd.DataFrame(
        [
            {
                "ticker": "AAA3",
                "p_l": 10.0,
                "dy": 0.05,
                "origem_cnpj": "nome",
                "alertas": [],
            },
            {
                "ticker": "BBB3",
                "p_l": None,
                "dy": None,
                "origem_cnpj": None,
                "alertas": ["sem_cnpj"],
            },
        ]
    )


def test_executar_orquestra_cache_grava_atomico_e_gera_metadados(tmp_path, monkeypatch):
    bruto = tmp_path / "raw"
    derivado = tmp_path / "derived"
    bruto.mkdir()
    for nome in (
        "COTAHIST_A2025.ZIP",
        "COTAHIST_A2026.ZIP",
        "fca_cia_aberta_2025.zip",
        "fca_cia_aberta_2026.zip",
    ):
        (bruto / nome).write_bytes(b"sintetico")

    def ler_cotahist(ano, **kwargs):
        assert kwargs["apenas_acoes"]
        return pd.DataFrame(
            [
                {
                    "data": pd.Timestamp(f"{ano}-10-08"),
                    "codbdi": "02",
                    "ticker": "AAA3",
                }
            ]
        )

    monkeypatch.setattr(atualizar_ativos.b3_cotahist, "ler_cotahist", ler_cotahist)
    monkeypatch.setattr(
        atualizar_ativos.cvm,
        "ler_fca",
        lambda ano, **kwargs: pd.DataFrame([{"ano": ano}]),
    )
    monkeypatch.setattr(atualizar_ativos.cvm, "ler_cadastro", lambda **kwargs: pd.DataFrame())
    monkeypatch.setattr(
        atualizar_ativos,
        "_carregar_demonstracoes",
        lambda *args: ({}, {}),
    )
    monkeypatch.setattr(
        atualizar_ativos,
        "construir_tabela_acoes",
        lambda *args, **kwargs: _tabela_final(),
    )

    tabela, meta = atualizar_ativos.executar(
        data_referencia="2026-10-08",
        liquidez_minima=123_000,
        pasta_bruta=bruto,
        pasta_derivada=derivado,
    )

    assert tabela["ticker"].tolist() == ["AAA3", "BBB3"]
    assert meta["linhas"] == 2
    assert meta["cobertura_p_l"] == 0.5
    assert meta["cobertura_dy"] == 0.5
    assert meta["pendencias_ticker"] == ["BBB3"]
    assert meta["tickers_resolvidos_por_nome"] == ["AAA3"]
    assert meta["schema_version"] == 2
    assert pd.read_parquet(derivado / "acoes.parquet")["ticker"].tolist() == ["AAA3", "BBB3"]
    assert json.loads((derivado / "acoes_meta.json").read_text(encoding="utf-8")) == meta


def test_executar_falha_sem_cotahist(tmp_path):
    with pytest.raises(FileNotFoundError, match="COTAHIST"):
        atualizar_ativos.executar(pasta_bruta=tmp_path, pasta_derivada=tmp_path / "out")


def test_leitores_internos_filtram_contas_e_selecionam_anos(monkeypatch, tmp_path):
    chamadas = []

    def ler_relatorio(tipo, ano, relatorio, *, consolidado, **kwargs):
        chamadas.append((tipo, ano, relatorio, consolidado))
        return pd.DataFrame(
            [
                {"CD_CONTA": next(iter(atualizar_ativos.CODIGOS_RELATORIO[relatorio]))},
                {"CD_CONTA": "fora"},
            ]
        )

    monkeypatch.setattr(atualizar_ativos.cvm, "ler_relatorio", ler_relatorio)
    con, ind = atualizar_ativos._ler_relatorios(
        "dfp", [2024, 2025], "DRE", pasta=tmp_path
    )

    assert len(con) == len(ind) == 2
    assert set(con["CD_CONTA"]) <= atualizar_ativos.CODIGOS_RELATORIO["DRE"]
    assert len(chamadas) == 4


def test_leitor_dfc_entrega_prioridade_mi_con_md_con_mi_ind_md_ind(monkeypatch, tmp_path):
    def ler_relatorios(tipo, anos, relatorio, *, pasta):
        assert tipo == "dfp"
        assert anos == [2025]
        assert pasta == tmp_path
        return (
            pd.DataFrame({"origem": [f"{relatorio}_con"]}),
            pd.DataFrame({"origem": [f"{relatorio}_ind"]}),
        )

    monkeypatch.setattr(atualizar_ativos, "_ler_relatorios", ler_relatorios)

    resultado = atualizar_ativos._ler_dfc("dfp", [2025], pasta=tmp_path)

    assert [quadro.loc[0, "origem"] for quadro in resultado] == [
        "DFC_MI_con",
        "DFC_MD_con",
        "DFC_MI_ind",
        "DFC_MD_ind",
    ]


def test_carregamento_escolhe_historico_dre_e_dois_anos_de_balanco(monkeypatch, tmp_path):
    for ano in range(2020, 2026):
        (tmp_path / f"dfp_cia_aberta_{ano}.zip").write_bytes(b"")
    for ano in (2025, 2026):
        (tmp_path / f"itr_cia_aberta_{ano}.zip").write_bytes(b"")
    chamadas = []

    def ler_relatorios(tipo, anos, relatorio, *, pasta):
        chamadas.append((tipo, tuple(anos), relatorio))
        vazio = pd.DataFrame()
        return vazio, vazio

    monkeypatch.setattr(atualizar_ativos, "_ler_relatorios", ler_relatorios)
    monkeypatch.setattr(
        atualizar_ativos,
        "_ler_capital",
        lambda tipo, anos, pasta: pd.DataFrame({"tipo": [tipo], "anos": [tuple(anos)]}),
    )

    dfp, itr = atualizar_ativos._carregar_demonstracoes(
        tmp_path, pd.Timestamp("2026-10-08")
    )

    assert ("dfp", tuple(range(2020, 2026)), "DRE") in chamadas
    assert ("dfp", (2024, 2025), "BPA") in chamadas
    assert ("itr", (2025, 2026), "DRE") in chamadas
    assert dfp["CAPITAL"].loc[0, "anos"] == (2024, 2025)
    assert itr["CAPITAL"].loc[0, "anos"] == (2025, 2026)


def test_resumo_e_main_imprimem_contrato(monkeypatch, capsys):
    meta = {
        "linhas": 2,
        "cobertura_p_l": 0.5,
        "cobertura_dy": 0.5,
        "pendencias_ticker": ["BBB3"],
    }
    monkeypatch.setattr(atualizar_ativos, "executar", lambda **kwargs: (_tabela_final(), meta))
    monkeypatch.setattr(
        sys,
        "argv",
        ["atualizar_ativos", "--data", "2026-10-08", "--liquidez-minima", "123000"],
    )

    atualizar_ativos.main()

    saida = capsys.readouterr().out
    assert "Universo: 2 tickers" in saida
    assert "Cobertura de P/L: 50.0%" in saida
    assert "Cobertura de DY: 50.0%" in saida
    assert "Pendências de ticker: BBB3" in saida
