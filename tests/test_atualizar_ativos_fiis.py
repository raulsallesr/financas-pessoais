import json
import sys

import pandas as pd

from scripts import atualizar_ativos


def _tabela_fiis():
    return pd.DataFrame(
        [
            {
                "ticker": "AAAA11",
                "cnpj": "00.000.000/0001-00",
                "tipo": "Tijolo",
                "p_vp": 0.9,
                "dy_12m": 0.10,
                "rendimento_12m_cota": 9.0,
                "vacancia": 0.05,
                "alertas": ["dy_dados_suspeitos"],
            },
            {
                "ticker": "BBBB11",
                "cnpj": "11.111.111/0001-11",
                "tipo": "Papel",
                "p_vp": None,
                "dy_12m": None,
                "rendimento_12m_cota": None,
                "vacancia": None,
                "alertas": [],
            },
        ]
    )


def test_executar_fiis_orquestra_cache_persistencia_e_metadados(tmp_path, monkeypatch):
    bruto = tmp_path / "raw"
    derivado = tmp_path / "derived"
    bruto.mkdir()
    (bruto / "COTAHIST_A2026.ZIP").write_bytes(b"sintetico")
    cotacoes = pd.DataFrame(
        [
            {
                "data": pd.Timestamp("2026-10-08"),
                "ticker": "AAAA11",
                "codbdi": "12",
            }
        ]
    )

    def ler_cotahist(ano, **kwargs):
        assert ano == 2026
        assert kwargs["apenas_fiis"]
        return cotacoes

    monkeypatch.setattr(atualizar_ativos.b3_cotahist, "ler_cotahist", ler_cotahist)
    monkeypatch.setattr(
        atualizar_ativos,
        "_carregar_informes_fii",
        lambda *args: (pd.DataFrame(),) * 4,
    )
    monkeypatch.setattr(
        atualizar_ativos,
        "construir_tabela_fiis",
        lambda *args, **kwargs: (
            _tabela_fiis(),
            {
                "pendencias_ticker": ["PEND11"],
                "pendencias_ticker_detalhes": [
                    {"ticker": "PEND11", "motivo": "empate_nome"}
                ],
                "tickers_resolvidos_por_desempate_nome": ["NOME11"],
            },
        ),
    )

    tabela, meta = atualizar_ativos.executar(
        classe="fiis",
        data_referencia="2026-10-08",
        pasta_bruta=bruto,
        pasta_derivada=derivado,
        minimo_pregoes=1,
    )

    assert tabela["ticker"].tolist() == ["AAAA11", "BBBB11"]
    assert meta["schema_version"] == 3
    assert meta["cobertura_p_vp"] == 0.5
    assert meta["cobertura_dy_12m"] == 0.5
    assert meta["cobertura_rendimento_12m_cota"] == 0.5
    assert meta["cobertura_vacancia"] == 0.5
    assert meta["fundos_com_alerta_dy_dados_suspeitos"] == 1
    assert meta["pendencias_ticker"] == ["PEND11"]
    assert meta["pendencias_ticker_detalhes"] == [
        {"ticker": "PEND11", "motivo": "empate_nome"}
    ]
    assert meta["tickers_resolvidos_por_desempate_nome"] == ["NOME11"]
    assert meta["contagem_por_tipo"] == {"Papel": 1, "Tijolo": 1}
    assert pd.read_parquet(derivado / "fiis.parquet")["ticker"].tolist() == [
        "AAAA11",
        "BBBB11",
    ]
    assert json.loads((derivado / "fiis_meta.json").read_text(encoding="utf-8")) == meta


def test_carregador_de_informes_fii_usa_dois_anos_e_quatro_quadros(tmp_path, monkeypatch):
    for tipo in ("mensal", "trimestral"):
        for ano in (2025, 2026):
            (tmp_path / f"inf_{tipo}_fii_{ano}.zip").write_bytes(b"")
    chamadas = []

    def ler(tipo, ano, quadro, **kwargs):
        chamadas.append((tipo, ano, quadro))
        return pd.DataFrame({"origem": [f"{tipo}-{ano}-{quadro}"]})

    monkeypatch.setattr(atualizar_ativos.cvm, "ler_informe_fii", ler)

    geral, complemento, ativo, imovel = atualizar_ativos._carregar_informes_fii(
        tmp_path, pd.Timestamp("2026-10-08")
    )

    assert len(geral) == len(complemento) == len(ativo) == len(imovel) == 2
    assert ("mensal", 2025, "geral") in chamadas
    assert ("trimestral", 2026, "imovel") in chamadas


def test_executar_todos_dispara_as_duas_classes(monkeypatch):
    monkeypatch.setattr(
        atualizar_ativos,
        "_executar_acoes",
        lambda **kwargs: (pd.DataFrame(), {"classe": "acoes"}),
    )
    monkeypatch.setattr(
        atualizar_ativos,
        "_executar_fiis",
        lambda **kwargs: (pd.DataFrame(), {"classe": "fiis"}),
    )

    resultado = atualizar_ativos.executar(classe="todos")

    assert resultado["acoes"][1]["classe"] == "acoes"
    assert resultado["fiis"][1]["classe"] == "fiis"


def test_resumo_e_cli_da_classe_fiis(monkeypatch, capsys):
    meta = {
        "linhas": 2,
        "cobertura_p_vp": 0.5,
        "cobertura_dy_12m": 0.5,
        "cobertura_rendimento_12m_cota": 0.5,
        "cobertura_vacancia": 0.5,
        "fundos_com_alerta_dy_dados_suspeitos": 1,
        "pendencias_ticker": ["PEND11"],
        "contagem_por_tipo": {"Papel": 1, "Tijolo": 1},
    }
    monkeypatch.setattr(
        atualizar_ativos, "executar", lambda **kwargs: (_tabela_fiis(), meta)
    )
    monkeypatch.setattr(sys, "argv", ["atualizar_ativos", "--classe", "fiis"])

    atualizar_ativos.main()

    saida = capsys.readouterr().out
    assert "Universo: 2 FIIs" in saida
    assert "Cobertura de P/VP: 50.0%" in saida
    assert "Pendências de ticker: PEND11" in saida
    assert "Fundos com DY/rentabilidade suspeitos: 1" in saida
    assert "Papel: 1" in saida
