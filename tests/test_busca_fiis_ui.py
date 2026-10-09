import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from ativos.core.linguagem import textos_proibidos
from ativos.core.metricas_fiis import COLUNAS_METRICAS_FII
from ativos.ui import componentes_tabela, pagina_busca_fiis

APP_BUSCA_FIIS = Path(__file__).parent / "fixtures" / "app_busca_fiis.py"


def _quadro():
    linhas = []
    for indice, ticker in enumerate(("AAAA11", "BBBB11"), start=1):
        linha = {
            "ticker": ticker,
            "nome": f"Fundo {indice}",
            "cnpj": f"sintetico-{indice}",
            "segmento": "Logística" if indice == 1 else "Recebíveis",
            "tipo": "Tijolo" if indice == 1 else "Papel",
            "gestao": "Ativa",
            "meses_informe": 12,
            "data_informe": pd.Timestamp("2026-08-01"),
            "alertas": [] if indice == 1 else ["dy_parcial"],
        }
        linha.update({coluna: float(indice) for coluna in COLUNAS_METRICAS_FII})
        linha["p_vp"] = 0.8 + indice / 10
        linha["dy_12m"] = 0.07 + indice / 100
        linha["vacancia"] = 0.05 if indice == 1 else np.nan
        linha["liquidez_media_diaria"] = indice * 500_000.0
        linhas.append(linha)
    return pd.DataFrame(linhas)


def test_pagina_busca_fiis_carrega_parquet_e_mostra_metadados(tmp_path, monkeypatch):
    _quadro().to_parquet(tmp_path / "fiis.parquet", index=False)
    (tmp_path / "fiis_meta.json").write_text(
        json.dumps(
            {
                "data_cotacao": "2026-10-08",
                "gerado_em": "2026-10-09T12:00:00-03:00",
                "linhas": 2,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(tmp_path))
    pagina_busca_fiis.carregar_fiis.clear()
    pagina_busca_fiis.carregar_meta_fiis.clear()

    app = AppTest.from_file(str(APP_BUSCA_FIIS), default_timeout=20).run()

    assert not app.exception
    assert app.title[0].value == "Busca de FIIs"
    assert [metrica.value for metrica in app.metric] == [
        "2026-10-08",
        "2026-10-09 12:00:00",
        "2 de 2",
    ]
    assert app.dataframe[0].value["ticker"].tolist() == ["AAAA11", "BBBB11"]


def test_pagina_busca_fiis_sem_parquet_exibe_comando_claro(tmp_path, monkeypatch):
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(tmp_path))

    app = AppTest.from_file(str(APP_BUSCA_FIIS), default_timeout=20).run()

    assert not app.exception
    assert "--classe fiis" in app.info[0].value


def test_filtros_fii_excluem_nan_e_aplicam_tipo_segmento_alertas_e_liquidez():
    quadro = _quadro()
    resultado = pagina_busca_fiis.aplicar_filtros_fiis(
        quadro,
        tipos=["Tijolo"],
        segmentos=["Logística"],
        p_vp=(0.85, 1.0),
        dy_12m=(0.08, None),
        vacancia=(None, 0.10),
        liquidez_minima=400_000,
        ocultar_alertas=True,
    )

    assert resultado["ticker"].tolist() == ["AAAA11"]
    assert pagina_busca_fiis.aplicar_filtros_fiis(
        quadro, vacancia=(None, 0.10)
    )["ticker"].tolist() == ["AAAA11"]


def test_catalogo_textos_csv_e_formatacao_compartilhada_respeitam_contratos():
    assert set(pagina_busca_fiis.METRICAS_FII) == set(COLUNAS_METRICAS_FII)
    assert textos_proibidos(list(pagina_busca_fiis.TEXTOS_UI_FII)) == []
    assert pagina_busca_fiis.colunas_dos_grupos_fii(["Valuation"]) == ["vp_cota", "p_vp"]
    arvore = ast.parse(Path(pagina_busca_fiis.__file__).read_text(encoding="utf-8"))
    literais = [
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    ]
    assert textos_proibidos(literais) == []

    conteudo = componentes_tabela.exportar_csv(_quadro().iloc[:1]).decode("utf-8-sig")
    assert conteudo.startswith("ticker;nome;")
    assert "0,9" in conteudo
    assert componentes_tabela.formatar_comparacao(50_000, "inteiro") == "50.000"
