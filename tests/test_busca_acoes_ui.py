import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from ativos.core.linguagem import textos_proibidos
from ativos.core.metricas_acoes import COLUNAS_METRICAS
from ativos.core.presets import MARGEM_CALCULADA
from ativos.core.valuation import COLUNAS_AVALIACAO
from ativos.ui import pagina_busca

APP_BUSCA = Path(__file__).parent / "fixtures" / "app_busca.py"


def _quadro():
    linhas = []
    for indice, ticker in enumerate(("AAA3", "BBB3"), start=1):
        linha = {
            "ticker": ticker,
            "empresa": f"Empresa {indice}",
            "cnpj": f"sintetico-{indice}",
            "setor": "Indústria" if indice == 1 else "Bancos",
            "financeira": indice == 2,
            "data_balanco": pd.Timestamp("2026-06-30"),
            "data_entrega": pd.Timestamp("2026-08-01"),
            "alertas": [] if indice == 1 else ["salto_preco"],
        }
        linha.update({coluna: float(indice) for coluna in COLUNAS_METRICAS})
        linha["liquidez_media_diaria"] = indice * 100_000.0
        linhas.append(linha)
    return pd.DataFrame(linhas)


def test_pagina_busca_carrega_parquet_sintetico_e_mostra_metadados(tmp_path, monkeypatch):
    _quadro().to_parquet(tmp_path / "acoes.parquet", index=False)
    (tmp_path / "acoes_meta.json").write_text(
        json.dumps(
            {
                "data_cotacao": "2026-10-08",
                "gerado_em": "2026-10-09T10:00:00-03:00",
                "linhas": 2,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(tmp_path))
    pagina_busca.carregar_acoes.clear()
    pagina_busca.carregar_meta.clear()

    app = AppTest.from_file(str(APP_BUSCA), default_timeout=20).run()

    assert not app.exception
    assert app.title[0].value == "Busca avançada"
    assert [metrica.value for metrica in app.metric][-3:] == [
        "2026-10-08",
        "2026-10-09 10:00:00",
        "2 de 2",
    ]
    assert app.dataframe[0].value["ticker"].tolist() == ["AAA3", "BBB3"]
    assert set(COLUNAS_AVALIACAO).issubset(app.dataframe[0].value.columns)
    assert "Premissas" in [expander.label for expander in app.expander]

    app.selectbox[0].select(MARGEM_CALCULADA).run()
    assert app.dataframe[0].value["ticker"].tolist() == ["AAA3", "BBB3"]


def test_pagina_busca_sem_parquet_exibe_comando_claro(tmp_path, monkeypatch):
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(tmp_path))

    app = AppTest.from_file(str(APP_BUSCA), default_timeout=20).run()

    assert not app.exception
    assert "python -m scripts.atualizar_ativos" in app.info[0].value


def test_filtros_excluem_nan_quando_indicador_e_exigido():
    quadro = _quadro()
    quadro.loc[1, "p_l"] = np.nan

    resultado = pagina_busca.aplicar_filtros(
        quadro,
        setores=["Indústria", "Bancos"],
        liquidez_minima=50_000,
        faixas={"p_l": (0, 10)},
    )

    assert resultado["ticker"].tolist() == ["AAA3"]


def test_filtros_ocultam_financeiras_alertas_e_csv_usa_contrato_pt_br():
    resultado = pagina_busca.aplicar_filtros(
        _quadro(),
        excluir_financeiras=True,
        ocultar_alertas=True,
    )
    conteudo = pagina_busca.exportar_csv(resultado).decode("utf-8-sig")

    assert resultado["ticker"].tolist() == ["AAA3"]
    assert conteudo.startswith("ticker;empresa;")
    assert "1,0" in conteudo


def test_catalogo_e_todos_os_textos_da_tela_respeitam_guardrail():
    assert set(pagina_busca.METRICAS) == set(COLUNAS_METRICAS) | set(COLUNAS_AVALIACAO)
    assert textos_proibidos(list(pagina_busca.TEXTOS_UI)) == []
    assert pagina_busca.colunas_dos_grupos(["Crescimento"]) == [
        "cagr_receitas_5a",
        "cagr_lucros_5a",
    ]
    arvore = ast.parse(Path(pagina_busca.__file__).read_text(encoding="utf-8"))
    literais = [
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str)
    ]
    assert textos_proibidos(literais) == []


def test_formatacao_do_comparador_cobre_moeda_percentual_abreviado_e_vazio():
    assert pagina_busca._formatar_comparacao(np.nan, "multiplo") == "—"
    assert pagina_busca._formatar_comparacao(0.125, "percentual") == "12,50%"
    assert pagina_busca._formatar_comparacao(1234.5, "moeda") == "R$ 1.234,50"
    assert pagina_busca._formatar_comparacao(2_000_000, "reais_abreviado") == "R$ 2,00 M"
    assert pagina_busca._formatar_comparacao(2.5, "multiplo") == "2,50"
