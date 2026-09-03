import json
import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.adapters import curva_fontes
from focuslens.adapters.curva_fontes import ErroCacheCurva, ErroFonteCurva
from focuslens.core.curva_data import PontoCurva

CABECALHO = (
    "Tipo Titulo;Data Vencimento;Data Base;Taxa Compra Manha;"
    "Taxa Venda Manha;PU Compra Manha;PU Venda Manha;PU Base Manha\n"
)


def _csv(*linhas: str) -> bytes:
    return (CABECALHO + "\n".join(linhas) + "\n").encode("utf-8")


def _ponto() -> PontoCurva:
    return PontoCurva(
        data_referencia=date(2026, 8, 26),
        tipo_titulo="Tesouro Prefixado",
        vencimento=date(2029, 1, 1),
        taxa_compra=14.06,
        taxa_venda=14.18,
        pu_compra=736.83,
        pu_venda=734.64,
        fonte="Tesouro Transparente",
    )


def test_interpretacao_filtra_prefixado_sem_cupom_e_converte_pt_br():
    conteudo = _csv(
        "Tesouro Selic;01/03/2029;26/08/2026;0,03;0,04;"
        "19.739,02;19.723,85;19.723,85",
        "Tesouro Prefixado;01/01/2029;26/08/2026;14,06;14,18;"
        "736,83;734,64;734,64",
        "Tesouro Prefixado com Juros Semestrais;01/01/2035;"
        "26/08/2026;14,30;14,42;700,00;699,00;699,00",
    )

    pontos = curva_fontes.interpretar_csv(conteudo)

    assert len(pontos) == 1
    assert pontos[0] == _ponto()


def test_interpretacao_falha_fechada_quando_schema_muda():
    with pytest.raises(ErroFonteCurva, match="estrutura"):
        curva_fontes.interpretar_csv(b"coluna;outra\n1;2\n")


def test_interpretacao_rejeita_pontos_conflitantes():
    conteudo = _csv(
        "Tesouro Prefixado;01/01/2029;26/08/2026;"
        "14,06;14,18;736,83;734,64;734,64",
        "Tesouro Prefixado;01/01/2029;26/08/2026;"
        "14,20;14,32;730,00;728,00;728,00",
    )

    with pytest.raises(ErroFonteCurva, match="conflitantes"):
        curva_fontes.interpretar_csv(conteudo)


@patch("focuslens.adapters.curva_fontes.requests.get")
def test_busca_limita_download_e_interpreta_resposta(mock_get):
    resposta = mock_get.return_value
    resposta.raise_for_status.return_value = None
    resposta.iter_content.return_value = [
        _csv(
            "Tesouro Prefixado;01/01/2029;26/08/2026;"
            "14,06;14,18;736,83;734,64;734,64"
        )
    ]

    pontos = curva_fontes.buscar_curva_prefixada()

    assert pontos == (_ponto(),)
    assert mock_get.call_args.kwargs["stream"] is True
    resposta.close.assert_called_once_with()


@patch("focuslens.adapters.curva_fontes.requests.get")
def test_erro_de_rede_vira_falha_controlada(mock_get):
    mock_get.side_effect = requests.Timeout("timeout")

    with pytest.raises(ErroFonteCurva):
        curva_fontes.buscar_curva_prefixada()


def test_cache_ida_e_volta_e_nao_regrava_conteudo_igual(
    tmp_path,
    monkeypatch,
):
    caminho = tmp_path / "curva.json"
    monkeypatch.setattr(curva_fontes, "CACHE_PATH", caminho)

    assert curva_fontes.salvar_cache((_ponto(),)) is True
    primeira_versao = caminho.read_text(encoding="utf-8")
    assert curva_fontes.salvar_cache((_ponto(),)) is False
    assert caminho.read_text(encoding="utf-8") == primeira_versao
    assert curva_fontes.carregar_cache() == [_ponto()]
    assert curva_fontes.data_ultima_atualizacao_cache() == date.today()
    conteudo = json.loads(primeira_versao)
    assert conteudo["licenca"] == "ODbL 1.0"
    assert not list(tmp_path.glob(".curva_cache_*.tmp"))


def test_cache_invalido_gera_erro_controlado(tmp_path, monkeypatch):
    caminho = tmp_path / "curva.json"
    caminho.write_text("{incompleto", encoding="utf-8")
    monkeypatch.setattr(curva_fontes, "CACHE_PATH", caminho)

    with pytest.raises(ErroCacheCurva):
        curva_fontes.carregar_cache()


def test_cache_rejeita_numero_nao_finito(tmp_path, monkeypatch):
    caminho = tmp_path / "curva.json"
    monkeypatch.setattr(curva_fontes, "CACHE_PATH", caminho)
    curva_fontes.salvar_cache((_ponto(),))
    conteudo = json.loads(caminho.read_text(encoding="utf-8"))
    conteudo["registros"][0]["taxa_compra"] = float("nan")
    caminho.write_text(json.dumps(conteudo), encoding="utf-8")

    with pytest.raises(ErroCacheCurva, match="registro inválido"):
        curva_fontes.carregar_cache()


def test_atualizacao_busca_salva_e_retorna_pontos():
    with (
        patch.object(
            curva_fontes,
            "buscar_curva_prefixada",
            return_value=(_ponto(),),
        ),
        patch.object(curva_fontes, "salvar_cache") as salvar,
    ):
        resultado = curva_fontes.atualizar_e_obter_curva()

    assert resultado == (_ponto(),)
    salvar.assert_called_once_with((_ponto(),))
