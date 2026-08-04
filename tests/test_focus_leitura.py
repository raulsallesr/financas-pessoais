import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import focus_leitura
from focus_leitura import ErroBuscaFocus, _chave_ordenacao_reuniao, _linha_para_leitura


def test_chave_ordenacao_reuniao_ordena_cronologicamente():
    reunioes = ["R5/2026", "R1/2027", "R4/2028", "R6/2026"]
    ordenadas = sorted(reunioes, key=_chave_ordenacao_reuniao)
    assert ordenadas == ["R5/2026", "R6/2026", "R1/2027", "R4/2028"]


def test_linha_para_leitura_converte_campos_da_api():
    linha = {
        "Indicador": "Selic",
        "Data": "2026-07-31",
        "Media": 14.0166,
        "Mediana": 14.0,
        "DesvioPadrao": 0.0685,
        "Minimo": 13.75,
        "Maximo": 14.25,
        "numeroRespondentes": 151,
    }
    leitura = _linha_para_leitura(linha, "R5/2026")
    assert leitura.indicador == "Selic"
    assert leitura.data_coleta == date(2026, 7, 31)
    assert leitura.mediana == 14.0


@patch("focus_leitura.requests.get")
def test_buscar_selic_proxima_reuniao_usa_menor_reuniao_da_data_mais_recente(mock_get):
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = {
        "value": [
            {
                "Indicador": "Selic", "Data": "2026-07-31", "Reuniao": "R6/2026",
                "Media": 13.9, "Mediana": 14.0, "DesvioPadrao": 0.1,
                "Minimo": 13.5, "Maximo": 14.25, "numeroRespondentes": 151, "baseCalculo": 0,
            },
            {
                "Indicador": "Selic", "Data": "2026-07-31", "Reuniao": "R5/2026",
                "Media": 14.0, "Mediana": 14.0, "DesvioPadrao": 0.07,
                "Minimo": 13.75, "Maximo": 14.25, "numeroRespondentes": 151, "baseCalculo": 0,
            },
            {
                "Indicador": "Selic", "Data": "2026-07-24", "Reuniao": "R5/2026",
                "Media": 13.8, "Mediana": 13.75, "DesvioPadrao": 0.1,
                "Minimo": 13.5, "Maximo": 14.0, "numeroRespondentes": 148, "baseCalculo": 0,
            },
        ]
    }
    leitura = focus_leitura.buscar_selic_proxima_reuniao()
    assert leitura.referencia == "R5/2026"
    assert leitura.data_coleta == date(2026, 7, 31)
    assert leitura.mediana == 14.0


@patch("focus_leitura.requests.get")
def test_buscar_selic_sem_linhas_levanta_erro(mock_get):
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = {"value": []}
    try:
        focus_leitura.buscar_selic_proxima_reuniao()
        assert False, "deveria ter levantado ErroBuscaFocus"
    except ErroBuscaFocus:
        pass


@patch("focus_leitura.requests.get")
def test_erro_de_rede_gera_erro_busca_focus(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("timeout")
    try:
        focus_leitura.buscar_selic_proxima_reuniao()
        assert False, "deveria ter levantado ErroBuscaFocus"
    except ErroBuscaFocus:
        pass


@patch("focus_leitura.requests.get")
def test_buscar_anual_codifica_indicador_acentuado_corretamente(mock_get):
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = {
        "value": [
            {
                "Indicador": "Dívida líquida do setor público", "Data": "2026-07-31",
                "Media": 69.968, "Mediana": 69.9, "DesvioPadrao": 1.1321,
                "Minimo": 66.0, "Maximo": 73.9, "numeroRespondentes": 58,
            },
        ]
    }
    leitura = focus_leitura.buscar_anual("Dívida líquida do setor público", 2026)

    url_chamada = mock_get.call_args.args[0]
    assert "+" not in url_chamada  # a API do BACEN rejeita "+" como espaço
    assert "%20" in url_chamada  # espaços sempre como %20
    assert "%C3%AD" in url_chamada  # "í" corretamente percent-encoded
    assert leitura.mediana == 69.9
    assert leitura.referencia == "2026"


def test_carregar_cache_sem_arquivo_retorna_lista_vazia(tmp_path, monkeypatch):
    monkeypatch.setattr(focus_leitura, "CACHE_PATH", tmp_path / "nao_existe.json")
    assert focus_leitura.carregar_cache() == []


def test_salvar_e_carregar_cache_ida_e_volta(tmp_path, monkeypatch):
    monkeypatch.setattr(focus_leitura, "CACHE_PATH", tmp_path / "focus_cache.json")
    linha = {
        "Indicador": "Selic", "Data": "2026-07-31", "Media": 14.0, "Mediana": 14.0,
        "DesvioPadrao": 0.07, "Minimo": 13.75, "Maximo": 14.25, "numeroRespondentes": 151,
    }
    leitura = _linha_para_leitura(linha, "R5/2026")
    focus_leitura.salvar_cache([leitura])
    recarregado = focus_leitura.carregar_cache()
    assert len(recarregado) == 1
    assert recarregado[0].mediana == 14.0
    assert recarregado[0].referencia == "R5/2026"
