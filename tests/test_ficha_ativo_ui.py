import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from ativos.core.linguagem import textos_proibidos
from ativos.ui import pagina_ficha, premissas_valuation

APP_FICHA = Path(__file__).parent / "fixtures" / "app_ficha.py"


def _acoes():
    return pd.DataFrame(
        [
            {
                "ticker": "AAA3",
                "empresa": "Empresa A",
                "cnpj": "acao-a",
                "setor": "Indústria",
                "financeira": False,
                "preco": 10.0,
                "lpa": 2.0,
                "vpa": 10.0,
                "dpa": 0.60,
                "p_l": 5.0,
                "p_vp": 1.0,
                "dy": 0.06,
                "roe": 0.20,
                "margem_liquida": 0.10,
                "div_liq_ebit": 1.5,
                "liquidez_media_diaria": 1_000_000.0,
                "alertas": [],
            },
            {
                "ticker": "NOFA3",
                "empresa": "Sem faixa S.A.",
                "cnpj": "acao-sem",
                "setor": "Indústria",
                "financeira": False,
                "preco": 5.0,
                "lpa": np.nan,
                "vpa": np.nan,
                "dpa": np.nan,
                "p_l": np.nan,
                "p_vp": np.nan,
                "dy": np.nan,
                "roe": np.nan,
                "margem_liquida": np.nan,
                "div_liq_ebit": np.nan,
                "liquidez_media_diaria": 500_000.0,
                "alertas": ["salto_preco"],
            },
        ]
    )


def _fiis():
    return pd.DataFrame(
        [
            {
                "ticker": "FIIX11",
                "nome": "Fundo X",
                "cnpj": "fii-x",
                "segmento": "Logística",
                "tipo": "Tijolo",
                "preco": 90.0,
                "vp_cota": 100.0,
                "rendimento_12m_cota": 12.0,
                "p_vp": 0.90,
                "dy_12m": 12 / 90,
                "vacancia": 0.05,
                "cotistas": 50_000,
                "alertas": [],
            }
        ]
    )


def _gravar_derivados(pasta: Path):
    _acoes().to_parquet(pasta / "acoes.parquet", index=False)
    _fiis().to_parquet(pasta / "fiis.parquet", index=False)
    metadado = {"data_cotacao": "2026-10-08"}
    (pasta / "acoes_meta.json").write_text(json.dumps(metadado), encoding="utf-8")
    (pasta / "fiis_meta.json").write_text(json.dumps(metadado), encoding="utf-8")


def test_ficha_mostra_acao_fii_e_ativo_sem_faixa(tmp_path, monkeypatch):
    _gravar_derivados(tmp_path)
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(tmp_path))
    pagina_ficha._carregar_parquet.clear()
    pagina_ficha._carregar_meta.clear()

    app = AppTest.from_file(str(APP_FICHA), default_timeout=20).run()

    assert not app.exception
    assert app.title[0].value == "Ficha do ativo"
    assert "AAA3" in app.header[0].value
    assert app.metric[-1].value == "3"
    assert app.dataframe[0].value["Modelo"].tolist() == [
        "Graham",
        "Bazin",
        "Gordon",
        "Múltiplos do setor",
    ]

    app.selectbox[0].select("fii::FIIX11").run()
    assert not app.exception
    assert "FIIX11" in app.header[0].value
    assert app.dataframe[0].value["Modelo"].tolist() == [
        "Patrimonial",
        "Renda capitalizada",
    ]

    app.selectbox[0].select("acao::NOFA3").run()
    assert not app.exception
    assert any("menos de dois modelos" in mensagem.value for mensagem in app.info)


def test_ficha_sem_derivados_exibe_comando(tmp_path, monkeypatch):
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(tmp_path))

    app = AppTest.from_file(str(APP_FICHA), default_timeout=20).run()

    assert not app.exception
    assert "--classe todos" in app.info[0].value


def test_comparacao_setorial_usa_empresas_distintas_e_percentil():
    acoes = _acoes()
    linha = acoes.iloc[0]

    comparacao = pagina_ficha.indicadores_setor(acoes, linha, classe="acao")

    assert comparacao["Indicador"].tolist() == [
        "P/L",
        "P/VP",
        "DY",
        "ROE",
        "Margem líquida",
        "Dívida líquida/EBIT",
    ]
    assert comparacao.loc[0, "Ativo"] == "5,00"


def test_textos_da_ficha_e_do_painel_respeitam_guardrail():
    assert textos_proibidos(list(pagina_ficha.TEXTOS_UI_FICHA)) == []
    for modulo in (pagina_ficha, premissas_valuation):
        arvore = ast.parse(Path(modulo.__file__).read_text(encoding="utf-8"))
        literais = [
            no.value
            for no in ast.walk(arvore)
            if isinstance(no, ast.Constant) and isinstance(no.value, str)
        ]
        assert textos_proibidos(literais) == []
