import os
from datetime import date, datetime
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from ativos.adapters import b3_cotahist, cvm


class _Resposta:
    def __init__(self, conteudo=b"conteudo"):
        self.conteudo = conteudo

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size):
        assert chunk_size > 0
        yield self.conteudo


class _Cliente:
    def __init__(self):
        self.chamadas = []

    def get(self, url, **kwargs):
        self.chamadas.append((url, kwargs))
        return _Resposta()


def _linha_cotahist(campos=None):
    linha = [" "] * 245
    valores = {
        (0, 2): "01",
        (2, 10): "20261008",
        (10, 12): "02",
        (12, 24): "TEST3",
        (24, 27): "010",
        (27, 39): "EMPRESA",
        (39, 49): "ON NM",
        (108, 121): "0000000012345",
        (147, 152): "00042",
        (170, 188): "000000000001234500",
        (210, 217): "0000010",
        (230, 242): "BRTESTACNOR0",
    }
    valores.update(campos or {})
    for (inicio, fim), valor in valores.items():
        texto = str(valor).ljust(fim - inicio)[: fim - inicio]
        linha[inicio:fim] = texto
    return "".join(linha)


def test_parser_cotahist_respeita_layout_posicional_e_fator():
    registro = b3_cotahist.parse_linha_cotahist(_linha_cotahist())

    assert registro == {
        "data": pd.Timestamp("2026-10-08"),
        "codbdi": "02",
        "ticker": "TEST3",
        "tpmerc": "010",
        "nomres": "EMPRESA",
        "especi": "ON NM",
        "preco": 12.345,
        "totneg": 42,
        "volume": 12_345,
        "fatcot": 10,
        "isin": "BRTESTACNOR0",
    }
    assert b3_cotahist.parse_linha_cotahist("00COTAHIST") is None
    assert b3_cotahist.parse_linha_cotahist(_linha_cotahist({(24, 27): "020"})) is None


def test_leitor_cotahist_filtra_acoes(tmp_path):
    caminho = tmp_path / "COTAHIST_A2026.ZIP"
    linha_acao = _linha_cotahist()
    linha_fii = _linha_cotahist({(10, 12): "12", (12, 24): "FIIX11"})
    with ZipFile(caminho, "w") as arquivo:
        arquivo.writestr("COTAHIST_A2026.TXT", f"{linha_acao}\n{linha_fii}\n")

    quadro = b3_cotahist.ler_cotahist(2026, pasta=tmp_path, apenas_acoes=True)

    assert quadro["ticker"].tolist() == ["TEST3"]


def test_download_cotahist_e_idempotencia_de_ano_fechado(tmp_path):
    cliente = _Cliente()
    destino = b3_cotahist.baixar_cotahist(
        2026,
        pasta=tmp_path,
        hoje=date(2026, 10, 9),
        cliente=cliente,
    )
    assert destino.read_bytes() == b"conteudo"
    assert len(cliente.chamadas) == 1

    cliente_fechado = _Cliente()
    destino_fechado = tmp_path / "COTAHIST_A2025.ZIP"
    destino_fechado.write_bytes(b"preservado")
    b3_cotahist.baixar_cotahist(
        2025,
        pasta=tmp_path,
        hoje=date(2026, 10, 9),
        cliente=cliente_fechado,
    )
    assert destino_fechado.read_bytes() == b"preservado"
    assert cliente_fechado.chamadas == []


def _zip_cvm(tmp_path: Path):
    caminho = tmp_path / "dfp_cia_aberta_2025.zip"
    cabecalho = (
        "CNPJ_CIA;DT_REFER;VERSAO;DENOM_CIA;CD_CVM;CATEG_DOC;ID_DOC;DT_RECEB;LINK_DOC\n"
        "00.000.000/0001-00;2025-12-31;2;ACME;1;DFP;1;2026-03-01;url\n"
    )
    relatorio = (
        "CNPJ_CIA;DT_REFER;VERSAO;DENOM_CIA;CD_CVM;GRUPO_DFP;MOEDA;ESCALA_MOEDA;"
        "ORDEM_EXERC;DT_INI_EXERC;DT_FIM_EXERC;CD_CONTA;DS_CONTA;VL_CONTA;ST_CONTA_FIXA\n"
        "00.000.000/0001-00;2025-12-31;2;ACME;1;DRE;REAL;MIL;ÚLTIMO;2025-01-01;"
        "2025-12-31;3.01;Receita;10;S\n"
    )
    with ZipFile(caminho, "w") as arquivo:
        arquivo.writestr("dfp_cia_aberta_2025.csv", cabecalho)
        arquivo.writestr("dfp_cia_aberta_DRE_con_2025.csv", relatorio)
        arquivo.writestr("dfp_cia_aberta_DFC_MI_con_2025.csv", relatorio)
    return caminho


def test_adapter_cvm_le_relatorio_e_anexa_data_de_entrega(tmp_path):
    _zip_cvm(tmp_path)

    quadro = cvm.ler_relatorio("dfp", 2025, "DRE", pasta=tmp_path)

    assert quadro.loc[0, "DT_RECEB"] == "2026-03-01"
    assert quadro.loc[0, "_consolidado"]
    assert quadro.loc[0, "_tipo_documento"] == "DFP"

    dfc = cvm.ler_relatorio("dfp", 2025, "DFC_MI", pasta=tmp_path)
    assert dfc.loc[0, "DT_RECEB"] == "2026-03-01"


def test_download_cvm_atualiza_corrente_e_preserva_fechado(tmp_path):
    cliente = _Cliente()
    destino = tmp_path / "dfp_cia_aberta_2026.zip"
    destino.write_bytes(b"velho")
    antigo = datetime(2026, 10, 6).timestamp()
    os.utime(destino, (antigo, antigo))

    cvm.baixar_arquivo(
        "https://exemplo/arquivo.zip",
        destino,
        ano=2026,
        hoje=date(2026, 10, 9),
        cliente=cliente,
    )
    assert destino.read_bytes() == b"conteudo"
    assert len(cliente.chamadas) == 1

    cliente.chamadas.clear()
    fechado = tmp_path / "dfp_cia_aberta_2025.zip"
    fechado.write_bytes(b"fechado")
    cvm.baixar_arquivo(
        "https://exemplo/arquivo.zip",
        fechado,
        ano=2025,
        hoje=date(2026, 10, 9),
        cliente=cliente,
    )
    assert cliente.chamadas == []


def test_download_cvm_remove_parcial_quando_cliente_falha(tmp_path):
    class ClienteComFalha:
        def get(self, *args, **kwargs):
            raise RuntimeError("falha simulada")

    try:
        cvm.baixar_arquivo(
            "https://exemplo/arquivo.zip",
            tmp_path / "arquivo.zip",
            ano=2026,
            hoje=date(2026, 10, 9),
            cliente=ClienteComFalha(),
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("a falha sintética deveria se propagar")
    assert not (tmp_path / ".arquivo.zip.part").exists()
