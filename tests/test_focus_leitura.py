import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import focus_leitura
from focus_leitura import (
    ErroBuscaFocus,
    ErroCacheFocus,
    _amostrar_uma_leitura_por_semana,
    _chave_ordenacao_reuniao,
    _linha_para_leitura,
)


def _linha(indicador, data_coleta, mediana=5.0, **campos):
    return {
        "Indicador": indicador,
        "Data": data_coleta,
        "Media": mediana,
        "Mediana": mediana,
        "DesvioPadrao": 0.1,
        "Minimo": mediana - 0.2,
        "Maximo": mediana + 0.2,
        "numeroRespondentes": 100,
        **campos,
    }


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
    assert focus_leitura.data_ultima_atualizacao_cache() == date.today()
    assert not list(tmp_path.glob(".focus_cache_*.tmp"))


def test_cache_invalido_gera_erro_controlado(tmp_path, monkeypatch):
    caminho = tmp_path / "focus_cache.json"
    caminho.write_text("{incompleto", encoding="utf-8")
    monkeypatch.setattr(focus_leitura, "CACHE_PATH", caminho)

    try:
        focus_leitura.carregar_cache()
        assert False, "deveria ter levantado ErroCacheFocus"
    except ErroCacheFocus:
        pass


def test_amostra_mantem_apenas_a_coleta_mais_recente_de_cada_semana():
    linhas = [
        _linha("IPCA", "2026-07-27", 5.1),
        _linha("IPCA", "2026-07-31", 5.0),
        _linha("IPCA", "2026-08-03", 4.9),
        _linha("IPCA", "2026-08-04", 4.8),
    ]
    amostra = _amostrar_uma_leitura_por_semana(linhas, "2026", 12)

    assert [leitura.data_coleta for leitura in amostra] == [
        date(2026, 7, 31),
        date(2026, 8, 4),
    ]


def test_buscar_historico_recente_traz_semanas_para_todos_indicadores():
    selic_atual = _linha_para_leitura(
        _linha("Selic", "2026-08-04", 14.0),
        "R5/2026",
    )

    def resposta(endpoint, params):
        filtro = params["$filter"]
        if endpoint == "ExpectativasMercadoSelic":
            return [
                _linha("Selic", "2026-07-24", 13.75, Reuniao="R5/2026"),
                _linha("Selic", "2026-07-31", 14.0, Reuniao="R5/2026"),
                _linha("Selic", "2026-08-04", 14.0, Reuniao="R5/2026"),
            ]
        indicador = next(
            item
            for item in focus_leitura.INDICADORES_ANUAIS
            if f"Indicador eq '{item}'" in filtro
        )
        return [
            _linha(indicador, "2026-07-24", 4.8),
            _linha(indicador, "2026-07-31", 4.9),
            _linha(indicador, "2026-08-04", 5.0),
        ]

    with (
        patch.object(
            focus_leitura,
            "buscar_selic_proxima_reuniao",
            return_value=selic_atual,
        ),
        patch.object(focus_leitura, "_get", side_effect=resposta),
    ):
        historico = focus_leitura.buscar_historico_recente(
            2026,
            max_semanas=3,
        )

    assert len(historico) == 18
    assert {
        leitura.indicador for leitura in historico
    } == {"Selic", *focus_leitura.INDICADORES_ANUAIS}


def test_atualizacao_faz_backfill_quando_cache_ainda_nao_tem_historico():
    leitura = _linha_para_leitura(
        _linha("IPCA", "2026-08-04", 5.0),
        "2026",
    )
    with (
        patch.object(focus_leitura, "carregar_cache", return_value=[]),
        patch.object(
            focus_leitura,
            "buscar_historico_recente",
            return_value=[leitura],
        ) as buscar,
        patch.object(focus_leitura, "salvar_cache") as salvar,
    ):
        resultado = focus_leitura.atualizar_e_obter_historico()

    assert resultado == [leitura]
    buscar.assert_called_once_with()
    salvar.assert_called_once_with([leitura])


def test_atualizacao_retorna_historico_sem_duplicatas():
    leitura = _linha_para_leitura(
        _linha("IPCA", "2026-08-04", 5.0),
        "2026",
    )
    historico = [leitura]
    with (
        patch.object(
            focus_leitura,
            "carregar_cache",
            return_value=historico,
        ),
        patch.object(
            focus_leitura,
            "historico_precisa_backfill",
            return_value=False,
        ),
        patch.object(
            focus_leitura,
            "buscar_leituras_atuais",
            return_value=[leitura],
        ),
        patch.object(focus_leitura, "salvar_cache"),
    ):
        resultado = focus_leitura.atualizar_e_obter_historico()

    assert resultado == [leitura]
