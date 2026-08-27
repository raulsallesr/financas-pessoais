from __future__ import annotations

from datetime import date, datetime, timezone
import json

import pytest

from curva_data import PontoCurva
from focus_data import LeituraIndicador
from mobile_snapshot import (
    gerar_snapshot_mobile,
    montar_contratos_snapshot,
    montar_snapshot_mobile,
    salvar_snapshot_mobile,
    validar_snapshot_publico,
)


def _leitura(
    indicador: str,
    data_coleta: date,
    mediana: float,
    *,
    referencia: str = "2026",
) -> LeituraIndicador:
    return LeituraIndicador(
        indicador=indicador,
        referencia=referencia,
        data_coleta=data_coleta,
        mediana=mediana,
        media=mediana,
        minimo=mediana - 0.1,
        maximo=mediana + 0.1,
        desvio_padrao=0.05,
        num_respondentes=100,
    )


def _ponto(data_referencia: date, ano: int, taxa: float) -> PontoCurva:
    return PontoCurva(
        data_referencia=data_referencia,
        tipo_titulo="Tesouro Prefixado",
        vencimento=date(ano, 1, 1),
        taxa_compra=taxa,
        taxa_venda=None,
        pu_compra=None,
        pu_venda=None,
        fonte="Tesouro Transparente",
    )


def _contratos_completos():
    historico = [
        _leitura("Selic", date(2026, 8, 14), 14.0, referencia="R6/2026"),
        _leitura("Selic", date(2026, 8, 21), 13.75, referencia="R6/2026"),
        _leitura("IPCA", date(2026, 8, 14), 4.3),
        _leitura("IPCA", date(2026, 8, 21), 4.2),
    ]
    pontos = []
    for indice, dia in enumerate(range(18, 24)):
        data_ref = date(2026, 8, dia)
        pontos.extend(
            [
                _ponto(data_ref, 2029, 13.2 - indice * 0.04),
                _ponto(data_ref, 2032, 14.0 - indice * 0.05),
            ]
        )
    return montar_contratos_snapshot(historico, pontos, date(2026, 8, 24))


def test_snapshot_v1_serializa_contratos_e_datas_iso():
    snapshot = montar_snapshot_mobile(
        _contratos_completos(),
        gerado_em=datetime(2026, 8, 27, 15, 30, tzinfo=timezone.utc),
    )

    assert snapshot["schemaVersion"] == 1
    assert snapshot["mode"] == "live"
    assert snapshot["generatedAt"] == "2026-08-27T15:30:00Z"
    assert snapshot["asOf"] == "2026-08-23"
    assert {fonte["id"] for fonte in snapshot["sources"]} == {"focus", "curva"}
    assert all(fonte["available"] for fonte in snapshot["sources"])
    assert {sinal["id"] for sinal in snapshot["signals"]} >= {
        "focus-selic",
        "curva-prefixada",
    }
    assert snapshot["proofs"]
    assert snapshot["limits"]


def test_serializacao_e_deterministica_com_os_mesmos_contratos(tmp_path):
    contratos = _contratos_completos()
    gerado_em = datetime(2026, 8, 27, 15, 30, tzinfo=timezone.utc)
    primeiro = montar_snapshot_mobile(contratos, gerado_em=gerado_em)
    segundo = montar_snapshot_mobile(contratos, gerado_em=gerado_em)
    caminho = tmp_path / "snapshot.json"

    salvar_snapshot_mobile(primeiro, caminho)
    bytes_primeiro = caminho.read_bytes()
    salvar_snapshot_mobile(segundo, caminho)

    assert primeiro == segundo
    assert caminho.read_bytes() == bytes_primeiro
    assert bytes_primeiro.endswith(b"\n")
    assert json.loads(bytes_primeiro) == primeiro


def test_gerador_preserva_generated_at_quando_conteudo_nao_muda(
    tmp_path,
    monkeypatch,
):
    contratos = _contratos_completos()
    caminho = tmp_path / "snapshot.json"
    primeiro_instante = datetime(2026, 8, 27, 15, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(
        "mobile_snapshot.carregar_contratos_dos_caches",
        lambda hoje=None: contratos,
    )

    primeiro = gerar_snapshot_mobile(caminho, gerado_em=primeiro_instante)
    segundo = gerar_snapshot_mobile(caminho)

    assert primeiro["generatedAt"] == "2026-08-27T15:30:00Z"
    assert segundo == primeiro
    assert json.loads(caminho.read_text(encoding="utf-8")) == primeiro


def test_snapshot_publico_rejeita_dados_de_carteira():
    snapshot = montar_snapshot_mobile(
        _contratos_completos(),
        gerado_em=datetime(2026, 8, 27, tzinfo=timezone.utc),
    )
    incompleto = dict(snapshot)
    del incompleto["generatedAt"]

    with pytest.raises(ValueError, match="generatedAt"):
        validar_snapshot_publico(incompleto)

    snapshot["positions"] = [{"amount": 1_000}]
    with pytest.raises(ValueError, match="amount, positions"):
        validar_snapshot_publico(snapshot)


def test_fonte_indisponivel_degrada_sem_apagar_a_outra():
    pontos = []
    for indice, dia in enumerate(range(18, 24)):
        data_ref = date(2026, 8, dia)
        pontos.extend(
            [
                _ponto(data_ref, 2029, 13.2 - indice * 0.04),
                _ponto(data_ref, 2032, 14.0 - indice * 0.05),
            ]
        )
    contratos = montar_contratos_snapshot([], pontos, date(2026, 8, 24))
    snapshot = montar_snapshot_mobile(
        contratos,
        gerado_em=datetime(2026, 8, 27, tzinfo=timezone.utc),
    )
    fontes = {fonte["id"]: fonte for fonte in snapshot["sources"]}

    assert fontes["focus"]["available"] is False
    assert fontes["focus"]["asOf"] is None
    assert fontes["curva"]["available"] is True
    assert [sinal["id"] for sinal in snapshot["signals"]] == ["curva-prefixada"]


def test_sem_as_duas_fontes_nao_substitui_snapshot_por_vazio():
    contratos = montar_contratos_snapshot([], [], date(2026, 8, 24))

    with pytest.raises(ValueError, match="nenhum sinal"):
        montar_snapshot_mobile(
            contratos,
            gerado_em=datetime(2026, 8, 27, tzinfo=timezone.utc),
        )
