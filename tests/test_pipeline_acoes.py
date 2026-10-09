import pandas as pd
import pytest

from ativos.core.pipeline_acoes import construir_tabela_acoes, selecionar_universo

CNPJ = "00.000.000/0001-00"


def _conta(
    data,
    codigo,
    descricao,
    valor,
    *,
    ordem="ÚLTIMO",
    inicio=None,
    entrega="2026-03-01",
):
    return {
        "CNPJ_CIA": CNPJ,
        "DT_REFER": data,
        "VERSAO": "1",
        "DENOM_CIA": "ACME S.A.",
        "ESCALA_MOEDA": "REAL",
        "ORDEM_EXERC": ordem,
        "DT_INI_EXERC": inicio,
        "DT_FIM_EXERC": data,
        "CD_CONTA": codigo,
        "DS_CONTA": descricao,
        "VL_CONTA": str(valor),
        "DT_RECEB": entrega,
        "_consolidado": True,
    }


def _par(consolidado):
    return consolidado, consolidado.iloc[0:0].copy()


def _demonstracoes():
    dre_dfp = pd.DataFrame(
        [
            _conta("2020-12-31", "3.01", "Receita", 500, inicio="2020-01-01"),
            _conta(
                "2020-12-31",
                "3.11.01",
                "Atribuído a Sócios da Empresa Controladora",
                50,
                inicio="2020-01-01",
            ),
            _conta("2025-12-31", "3.01", "Receita", 1_000, inicio="2025-01-01"),
            _conta("2025-12-31", "3.03", "Resultado Bruto", 400, inicio="2025-01-01"),
            _conta(
                "2025-12-31",
                "3.05",
                "Resultado Antes do Resultado Financeiro e dos Tributos",
                200,
                inicio="2025-01-01",
            ),
            _conta(
                "2025-12-31",
                "3.11.01",
                "Atribuído a Sócios da Empresa Controladora",
                100,
                inicio="2025-01-01",
            ),
        ]
    )
    dre_itr = pd.DataFrame(
        [
            _conta("2026-06-30", "3.01", "Receita", 300, inicio="2026-01-01"),
            _conta(
                "2026-06-30", "3.01", "Receita", 200, ordem="PENÚLTIMO", inicio="2025-01-01"
            ),
            _conta("2026-06-30", "3.03", "Resultado Bruto", 120, inicio="2026-01-01"),
            _conta(
                "2026-06-30",
                "3.03",
                "Resultado Bruto",
                80,
                ordem="PENÚLTIMO",
                inicio="2025-01-01",
            ),
            _conta(
                "2026-06-30",
                "3.05",
                "Resultado Antes do Resultado Financeiro e dos Tributos",
                60,
                inicio="2026-01-01",
            ),
            _conta(
                "2026-06-30",
                "3.05",
                "Resultado Antes do Resultado Financeiro e dos Tributos",
                40,
                ordem="PENÚLTIMO",
                inicio="2025-01-01",
            ),
            _conta(
                "2026-06-30",
                "3.11.01",
                "Atribuído a Sócios da Empresa Controladora",
                30,
                inicio="2026-01-01",
            ),
            _conta(
                "2026-06-30",
                "3.11.01",
                "Atribuído a Sócios da Empresa Controladora",
                20,
                ordem="PENÚLTIMO",
                inicio="2025-01-01",
            ),
        ]
    )
    bpa = pd.DataFrame(
        [
            _conta("2026-06-30", "1", "Ativo Total", 50_000),
            _conta("2026-06-30", "1.01", "Ativo Circulante", 20_000),
            _conta("2026-06-30", "1.01.01", "Caixa e equivalentes", 2_000),
            _conta("2026-06-30", "1.01.02", "Aplicações Financeiras", 1_000),
        ]
    )
    bpp = pd.DataFrame(
        [
            _conta("2026-06-30", "2", "Passivo Total", 50_000),
            _conta("2026-06-30", "2.01", "Passivo Circulante", 10_000),
            _conta("2026-06-30", "2.02", "Passivo Não Circulante", 10_000),
            _conta("2026-06-30", "2.01.04", "Empréstimos", 2_000),
            _conta("2026-06-30", "2.02.01", "Empréstimos", 4_000),
            _conta("2026-06-30", "2.03", "Patrimônio Líquido Consolidado", 30_000),
            _conta(
                "2026-06-30",
                "2.03.09",
                "Participação dos Acionistas Não Controladores",
                1_000,
            ),
        ]
    )
    dva = pd.DataFrame(
        [
            _conta("2025-12-31", "7.08.04.01", "Juros sobre o Capital Próprio", 200),
            _conta("2025-12-31", "7.08.04.02", "Dividendos", 300),
        ]
    )
    capital = pd.DataFrame(
        [
            {
                "CNPJ_CIA": CNPJ,
                "DT_REFER": "2026-06-30",
                "VERSAO": "1",
                "DT_RECEB": "2026-08-01",
                "QT_ACAO_ORDIN_CAP_INTEGR": "1000",
                "QT_ACAO_PREF_CAP_INTEGR": "2000",
                "QT_ACAO_ORDIN_TESOURO": "0",
                "QT_ACAO_PREF_TESOURO": "0",
            }
        ]
    )
    vazio_bpa = bpa.iloc[0:0].copy()
    vazio_bpp = bpp.iloc[0:0].copy()
    vazio_dva = dva.iloc[0:0].copy()
    return (
        {
            "DRE": _par(dre_dfp),
            "BPA": _par(vazio_bpa),
            "BPP": _par(vazio_bpp),
            "DVA": _par(dva),
            "CAPITAL": capital.iloc[0:0].copy(),
        },
        {
            "DRE": _par(dre_itr),
            "BPA": _par(bpa),
            "BPP": _par(bpp),
            "DVA": _par(vazio_dva),
            "CAPITAL": capital,
        },
    )


def _cotacoes():
    linhas = []
    for data, precos in [
        ("2026-10-07", {"ACME3": 10, "ACME4": 20, "ACME11": 40}),
        ("2026-10-08", {"ACME3": 15, "ACME4": 20, "ACME11": 40}),
    ]:
        for ticker, preco in precos.items():
            linhas.append(
                {
                    "data": pd.Timestamp(data),
                    "codbdi": "02",
                    "ticker": ticker,
                    "nomres": "ACME",
                    "especi": (
                        "UNT"
                        if ticker.endswith("11")
                        else ("ON" if ticker.endswith("3") else "PN")
                    ),
                    "preco": preco,
                    "totneg": 10,
                    "volume": 200_000,
                }
            )
    return pd.DataFrame(linhas)


def test_pipeline_normaliza_ttm_pl_units_e_metricas_por_empresa():
    dfp, itr = _demonstracoes()
    fca = pd.DataFrame(
        [
            {
                "Codigo_Negociacao": ticker,
                "CNPJ_Companhia": CNPJ,
                "Nome_Empresarial": "ACME S.A.",
                "Data_Referencia": "2026-01-01",
                "Versao": "1",
                "_ano_fca": 2026,
            }
            for ticker in ("ACME3", "ACME4", "ACME11")
        ]
    )
    cadastro = pd.DataFrame(
        [
            {
                "CNPJ_CIA": CNPJ,
                "DENOM_COMERC": "ACME",
                "DENOM_SOCIAL": "ACME S.A.",
                "SETOR_ATIV": "Indústria",
            }
        ]
    )

    tabela = construir_tabela_acoes(
        _cotacoes(),
        fca,
        cadastro,
        dfp,
        itr,
        data_referencia="2026-10-08",
        liquidez_minima=100_000,
        minimo_pregoes=1,
    )

    assert tabela["ticker"].tolist() == ["ACME11", "ACME3", "ACME4"]
    assert tabela["valor_mercado"].tolist() == [55_000, 55_000, 55_000]
    assert tabela["p_l"].tolist() == pytest.approx([500, 500, 500])
    assert tabela["vpa"].tolist() == pytest.approx([29_000 / 3_000] * 3)
    assert tabela["data_balanco"].dt.date.astype(str).tolist() == ["2026-06-30"] * 3
    assert "salto_preco" in tabela.loc[tabela["ticker"].eq("ACME3"), "alertas"].iloc[0]
    assert "alertas" in tabela
    assert tabela.alertas.map(type).eq(list).all()
    assert not tabela["financeira"].any()


def test_universo_exclui_bdr_fii_e_ticker_sem_quarenta_pregoes():
    cotacoes = _cotacoes()
    cotacoes.loc[cotacoes["ticker"].eq("ACME4"), "codbdi"] = "14"

    universo = selecionar_universo(
        cotacoes,
        data_referencia="2026-10-08",
        liquidez_minima=0,
        minimo_pregoes=3,
    )

    assert universo.empty
