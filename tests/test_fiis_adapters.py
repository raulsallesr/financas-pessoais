from datetime import date
from zipfile import ZipFile

import pytest

from ativos.adapters import b3_cotahist, cvm


class _Resposta:
    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size):
        assert chunk_size > 0
        yield b"zip-sintetico"


class _Cliente:
    def __init__(self):
        self.urls = []

    def get(self, url, **kwargs):
        self.urls.append(url)
        return _Resposta()


def _linha_cotahist(codbdi, ticker, especi):
    linha = [" "] * 245
    campos = {
        (0, 2): "01",
        (2, 10): "20261008",
        (10, 12): codbdi,
        (12, 24): ticker,
        (24, 27): "010",
        (27, 39): ticker,
        (39, 49): especi,
        (108, 121): "0000000010000",
        (147, 152): "00010",
        (170, 188): "000000000002000000",
        (210, 217): "0000001",
        (230, 242): f"BR{ticker[:4]}CTF001",
    }
    for (inicio, fim), valor in campos.items():
        linha[inicio:fim] = str(valor).ljust(fim - inicio)[: fim - inicio]
    return "".join(linha)


def test_leitor_cotahist_filtra_somente_fiis(tmp_path):
    with ZipFile(tmp_path / "COTAHIST_A2026.ZIP", "w") as arquivo:
        arquivo.writestr(
            "COTAHIST_A2026.TXT",
            "\n".join(
                [
                    _linha_cotahist("12", "FIIX11", "CI ER"),
                    _linha_cotahist("02", "ACAO3", "ON NM"),
                    _linha_cotahist("12", "DIRE11", "DIR"),
                ]
            ),
        )

    quadro = b3_cotahist.ler_cotahist(2026, pasta=tmp_path, apenas_fiis=True)

    assert quadro["ticker"].tolist() == ["FIIX11"]
    with pytest.raises(ValueError, match="uma classe"):
        b3_cotahist.ler_cotahist(
            2026, pasta=tmp_path, apenas_acoes=True, apenas_fiis=True
        )


def test_adapter_le_quadro_mensal_fii_com_texto_original(tmp_path):
    caminho = tmp_path / "inf_mensal_fii_2026.zip"
    with ZipFile(caminho, "w") as arquivo:
        arquivo.writestr(
            "inf_mensal_fii_geral_2026.csv",
            (
                "CNPJ_Fundo_Classe;Data_Referencia;Versao;Nome_Fundo_Classe\n"
                "00.000.000/0001-00;2026-01-01;2;Fundo Sintético\n"
            ).encode("latin1"),
        )

    quadro = cvm.ler_informe_fii("mensal", 2026, "geral", pasta=tmp_path)

    assert quadro.loc[0, "Nome_Fundo_Classe"] == "Fundo Sintético"
    assert quadro.loc[0, "Versao"] == "2"


def test_download_informe_fii_e_idempotencia_de_ano_fechado(tmp_path):
    cliente = _Cliente()
    destino = cvm.baixar_informe_fii(
        "mensal", 2026, pasta=tmp_path, hoje=date(2026, 10, 9), cliente=cliente
    )

    assert destino.read_bytes() == b"zip-sintetico"
    assert cliente.urls == [
        "https://dados.cvm.gov.br/dados/FII/DOC/INF_MENSAL/DADOS/inf_mensal_fii_2026.zip"
    ]

    fechado = tmp_path / "inf_trimestral_fii_2025.zip"
    fechado.write_bytes(b"preservado")
    cliente.urls.clear()
    cvm.baixar_informe_fii(
        "trimestral", 2025, pasta=tmp_path, hoje=date(2026, 10, 9), cliente=cliente
    )
    assert fechado.read_bytes() == b"preservado"
    assert cliente.urls == []


def test_adapter_fii_rejeita_tipo_desconhecido(tmp_path):
    with pytest.raises(ValueError, match="desconhecido"):
        cvm.baixar_informe_fii("semestral", 2026, pasta=tmp_path)
    with pytest.raises(ValueError, match="desconhecido"):
        cvm.ler_informe_fii("semestral", 2026, "geral", pasta=tmp_path)
