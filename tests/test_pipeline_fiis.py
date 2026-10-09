import pandas as pd
import pytest

from ativos.core.pipeline_fiis import (
    COLUNAS_FIIS,
    construir_tabela_fiis,
    mapear_tickers_fiis,
    mes_referencia_cobertura,
    selecionar_ultima_versao,
    selecionar_universo_fiis,
)


def _cotacao(ticker, isin, *, codbdi="12", especi="CI ER", volume=200_000):
    return {
        "data": pd.Timestamp("2026-10-08"),
        "codbdi": codbdi,
        "ticker": ticker,
        "nomres": ticker,
        "especi": especi,
        "preco": 90.0,
        "totneg": 10,
        "volume": volume,
        "isin": isin,
    }


def _geral(cnpj, isin, *, data="2026-01-01", versao="1", nome=None):
    return {
        "Tipo_Fundo_Classe": "Classe",
        "CNPJ_Fundo_Classe": cnpj,
        "Data_Referencia": data,
        "Versao": versao,
        "Nome_Fundo_Classe": nome or f"Fundo {cnpj}",
        "Codigo_ISIN": isin,
        "Segmento_Atuacao": "Logística",
        "Tipo_Gestao": "Ativa",
    }


def test_universo_fii_exige_codigo_especie_liquidez_e_pregoes():
    cotacoes = pd.DataFrame(
        [
            _cotacao("OKAY11", "BROKAYCTF001"),
            _cotacao("ACAO3", "BRACAOACNOR0", codbdi="02", especi="ON NM"),
            _cotacao("DIRE11", "BRDIRECTF001", especi="DIR"),
            _cotacao("SEML11", "BRSEMLCTF001", volume=10),
        ]
    )

    universo = selecionar_universo_fiis(
        cotacoes, liquidez_minima=100_000, minimo_pregoes=1
    )

    assert universo["ticker"].tolist() == ["OKAY11"]
    assert universo.loc[0, "isin"] == "BROKAYCTF001"


def test_versao_mais_alta_preserva_todas_as_linhas_do_mes():
    quadro = pd.DataFrame(
        [
            {
                "CNPJ_Fundo_Classe": "A",
                "Data_Referencia": "2026-06-30",
                "Versao": "1",
                "item": "antigo",
            },
            {
                "CNPJ_Fundo_Classe": "A",
                "Data_Referencia": "2026-06-30",
                "Versao": "2",
                "item": "imovel-a",
            },
            {
                "CNPJ_Fundo_Classe": "A",
                "Data_Referencia": "2026-06-30",
                "Versao": "2",
                "item": "imovel-b",
            },
        ]
    )

    resultado = selecionar_ultima_versao(quadro)

    assert resultado["item"].tolist() == ["imovel-a", "imovel-b"]


def test_ticker_cnpj_usa_isin_exato_fallback_unico_e_rejeita_raiz_ambigua():
    universo = pd.DataFrame(
        [
            {"ticker": "AAAA11", "isin": "BRAAAACTF001", "alertas": []},
            {"ticker": "BBBB11", "isin": "BRBBBBCTF999", "alertas": []},
            {"ticker": "CCCC11", "isin": "BRCCCCCTF999", "alertas": []},
        ]
    )
    geral = pd.DataFrame(
        [
            _geral("A", "BRAAAACTF001"),
            _geral("B", "BRBBBBCTF001"),
            _geral("C1", "BRCCCCCTF001"),
            _geral("C2", "BRCCCCCTF002"),
        ]
    )

    resultado = mapear_tickers_fiis(universo, geral).set_index("ticker")

    assert resultado.loc["AAAA11", "cnpj"] == "A"
    assert resultado.loc["AAAA11", "origem_cnpj"] == "isin"
    assert resultado.loc["BBBB11", "cnpj"] == "B"
    assert resultado.loc["BBBB11", "origem_cnpj"] == "raiz_isin"
    assert pd.isna(resultado.loc["CCCC11", "cnpj"])
    assert resultado.loc["CCCC11", "motivo_pendencia"] == "raiz_isin_ambigua"
    assert resultado.loc["CCCC11", "alertas"] == ["sem_cnpj"]


def test_ticker_cnpj_golden_desempata_xpml11_e_trxf11_pelo_nome():
    universo = pd.DataFrame(
        [
            {
                "ticker": "XPML11",
                "nome_b3": "XP MALLS",
                "isin": "BRXPMLCTF000",
                "alertas": [],
            },
            {
                "ticker": "TRXF11",
                "nome_b3": "TRX REAL",
                "isin": "BRTRXFCTF003",
                "alertas": [],
            },
        ]
    )
    geral = pd.DataFrame(
        [
            _geral(
                "28.757.546/0001-00",
                "BRXPMLCTF000",
                data="2025-01-01",
                nome="NOME ANTIGO SEM RELACAO",
            ),
            _geral(
                "28.757.546/0001-00",
                "BRXPMLCTF000",
                data="2026-01-01",
                nome="XP MALLS FUNDO DE INVESTIMENTO IMOBILIARIO",
            ),
            _geral(
                "07.583.627/0001-61",
                "BRXPMLCTF000",
                data="2026-01-01",
                nome="PENINSULA FII RL",
            ),
            _geral(
                "28.548.288/0001-52",
                "BRTRXFCTF003",
                nome="TRX REAL ESTATE FII",
            ),
            _geral(
                "63.134.454/0001-75",
                "BRTRXFCTF003",
                nome="LIQUIDEZ PROJETOS GD FUNDO DE INVESTIMENTO",
            ),
        ]
    )

    resultado = mapear_tickers_fiis(universo, geral).set_index("ticker")

    assert resultado.loc["XPML11", "cnpj"] == "28.757.546/0001-00"
    assert resultado.loc["TRXF11", "cnpj"] == "28.548.288/0001-52"
    assert resultado.loc["XPML11", "origem_cnpj"] == "isin_nome"
    assert resultado.loc["TRXF11", "origem_cnpj"] == "isin_nome"
    assert pd.isna(resultado.loc["XPML11", "motivo_pendencia"])


def test_ticker_cnpj_golden_empate_de_nome_continua_pendente():
    universo = pd.DataFrame(
        [
            {
                "ticker": "ALFA11",
                "nome_b3": "ALFA",
                "isin": "BRALFACTF001",
                "alertas": [],
            }
        ]
    )
    geral = pd.DataFrame(
        [
            _geral("A", "BRALFACTF001", nome="ALFA SHOPPING FII"),
            _geral("B", "BRALFACTF001", nome="ALFA RECEBIVEIS FII"),
        ]
    )

    resultado = mapear_tickers_fiis(universo, geral).iloc[0]

    assert pd.isna(resultado["cnpj"])
    assert resultado["motivo_pendencia"] == "empate_nome"
    assert resultado["alertas"] == ["sem_cnpj"]


def test_ticker_cnpj_golden_sem_palavra_em_comum_continua_pendente():
    universo = pd.DataFrame(
        [
            {
                "ticker": "ZERO11",
                "nome_b3": "OMEGA",
                "isin": "BRZEROCTF001",
                "alertas": [],
            }
        ]
    )
    geral = pd.DataFrame(
        [
            _geral("A", "BRZEROCTF001", nome="ALFA SHOPPING FII"),
            _geral("B", "BRZEROCTF001", nome="BETA RECEBIVEIS FII"),
        ]
    )

    resultado = mapear_tickers_fiis(universo, geral).iloc[0]

    assert pd.isna(resultado["cnpj"])
    assert resultado["motivo_pendencia"] == "sem_palavra_em_comum"
    assert resultado["alertas"] == ["sem_cnpj"]


def test_mes_de_cobertura_ignora_carga_recente_com_menos_de_oitenta_por_cento():
    quadro = pd.DataFrame(
        [
            *(
                {"CNPJ_Fundo_Classe": str(i), "Data_Referencia": pd.Timestamp("2026-07-01")}
                for i in range(5)
            ),
            {"CNPJ_Fundo_Classe": "0", "Data_Referencia": pd.Timestamp("2026-08-01")},
        ]
    )

    assert mes_referencia_cobertura(quadro) == pd.Timestamp("2026-07-01")


def test_pipeline_fii_golden_integra_versao_defasagem_composicao_e_imoveis():
    cnpj = "00.000.000/0001-00"
    cotacoes = pd.DataFrame([_cotacao("AAAA11", "BRAAAACTF001")])
    geral = pd.DataFrame([_geral(cnpj, "BRAAAACTF001")])
    meses = pd.date_range("2025-02-01", periods=12, freq="MS")
    complemento = pd.DataFrame(
        [
            {
                "CNPJ_Fundo_Classe": cnpj,
                "Data_Referencia": data,
                "Versao": "2" if data == meses[-1] else "1",
                "Total_Numero_Cotistas": "60000",
                "Valor_Ativo": "1000000",
                "Patrimonio_Liquido": "900000",
                "Cotas_Emitidas": "10000",
                "Valor_Patrimonial_Cotas": "100",
                "Percentual_Despesas_Taxa_Administracao": "0.001",
                "Percentual_Rentabilidade_Efetiva_Mes": "0.01",
                "Percentual_Dividend_Yield_Mes": (
                    "-0.058778" if data == meses[3] else "0.01"
                ),
            }
            for data in meses
        ]
        + [
            {
                "CNPJ_Fundo_Classe": cnpj,
                "Data_Referencia": meses[-1],
                "Versao": "1",
                "Valor_Patrimonial_Cotas": "80",
                "Percentual_Rentabilidade_Efetiva_Mes": "0.50",
                "Percentual_Dividend_Yield_Mes": "0.50",
            }
        ]
        + [
            {
                "CNPJ_Fundo_Classe": f"extra-{i}",
                "Data_Referencia": "2026-04-01",
                "Versao": "1",
                "Valor_Patrimonial_Cotas": "100",
                "Percentual_Rentabilidade_Efetiva_Mes": "0.01",
                "Percentual_Dividend_Yield_Mes": "0.01",
            }
            for i in range(4)
        ]
    )
    ativo_passivo = pd.DataFrame(
        [
            {
                "CNPJ_Fundo_Classe": cnpj,
                "Data_Referencia": "2026-01-01",
                "Versao": "1",
                "Total_Investido": "1000",
                "Direitos_Bens_Imoveis": "600",
                "Total_Passivo": "150000",
            }
        ]
    )
    imovel = pd.DataFrame(
        [
            {
                "CNPJ_Fundo_Classe": cnpj,
                "Data_Referencia": "2026-06-30",
                "Versao": "1",
                "Nome_Imovel": "A",
                "Percentual_Vacancia": "0.10",
                "Percentual_Inadimplencia": "0.02",
                "Percentual_Imovel_Total_Investido": "0.60",
            },
            {
                "CNPJ_Fundo_Classe": cnpj,
                "Data_Referencia": "2026-06-30",
                "Versao": "1",
                "Nome_Imovel": "B",
                "Percentual_Vacancia": "0.20",
                "Percentual_Inadimplencia": "0.04",
                "Percentual_Imovel_Total_Investido": "0.40",
            },
        ]
    )

    tabela, diagnostico = construir_tabela_fiis(
        cotacoes,
        geral,
        complemento,
        ativo_passivo,
        imovel,
        data_referencia="2026-10-08",
        minimo_pregoes=1,
    )

    linha = tabela.iloc[0]
    assert list(tabela) == list(COLUNAS_FIIS)
    assert diagnostico == {
        "pendencias_ticker": [],
        "pendencias_ticker_detalhes": [],
        "tickers_resolvidos_por_desempate_nome": [],
    }
    assert linha["tipo"] == "Tijolo"
    assert linha["p_vp"] == pytest.approx(0.90)
    assert linha["dy_12m"] == pytest.approx(12 / 90)
    assert linha["rentab_12m"] == pytest.approx(1.01**12 - 1)
    assert linha["vacancia"] == pytest.approx(0.14)
    assert linha["passivo_ativo"] == pytest.approx(0.15)
    assert linha["valor_mercado"] == pytest.approx(900_000)
    assert linha["alertas"] == ["dy_dados_suspeitos", "dy_parcial", "pl_defasado"]
