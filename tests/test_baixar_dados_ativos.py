import requests

from scripts import baixar_dados_ativos as baixar


class _Resposta:
    def __init__(self, status):
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def iter_content(self, chunk_size):
        yield b"conteudo"


class _Cliente:
    """Devolve 404 para os anos pedidos em `ausentes`."""

    def __init__(self, ausentes=()):
        self.ausentes = ausentes
        self.urls = []

    def get(self, url, **kwargs):
        self.urls.append(url)
        return _Resposta(404 if any(str(ano) in url for ano in self.ausentes) else 200)


def test_plano_cobre_seis_dfp_e_dois_anos_das_demais_fontes():
    rotulos = [rotulo for rotulo, _ in baixar.planejar(2026)]

    assert [r for r in rotulos if "DFP" in r] == [f"CVM DFP {ano}" for ano in range(2020, 2027)]
    for fonte in ("ITR", "FCA", "FII mensal", "FII trimestral", "COTAHIST"):
        assert [r for r in rotulos if fonte in r and "DFP" not in r][-2:] == [
            r for r in rotulos if fonte in r
        ][-2:]
        assert sum(fonte in r for r in rotulos) == 2
    assert rotulos[0] == "CVM cadastro de companhias"


def test_executar_baixa_tudo_para_a_pasta_informada(tmp_path):
    cliente = _Cliente()
    saidas = []

    ok, indisponiveis = baixar.executar(
        2026, pasta=tmp_path, cliente=cliente, saida=saidas.append
    )

    assert indisponiveis == []
    assert len(ok) == len(baixar.planejar(2026))
    assert (tmp_path / "dfp_cia_aberta_2026.zip").exists()
    assert (tmp_path / "COTAHIST_A2025.ZIP").exists()
    assert (tmp_path / "cad_cia_aberta.csv").exists()
    assert any("[1/" in linha for linha in saidas)


def test_ano_ainda_nao_publicado_nao_derruba_o_download(tmp_path):
    cliente = _Cliente(ausentes=("2026",))

    ok, indisponiveis = baixar.executar(
        2026, pasta=tmp_path, cliente=cliente, saida=lambda _: None
    )

    assert "CVM DFP 2026" in indisponiveis
    assert "CVM DFP 2025" in ok
    assert not (tmp_path / "dfp_cia_aberta_2026.zip").exists()


def test_cache_nao_baixa_de_novo_ano_encerrado(tmp_path):
    cliente = _Cliente()
    baixar.executar(2026, pasta=tmp_path, cliente=cliente, saida=lambda _: None)
    primeiras = len(cliente.urls)

    baixar.executar(2026, pasta=tmp_path, cliente=cliente, saida=lambda _: None)

    # só o ano corrente (e o cadastro) podem ser renovados; anos encerrados ficam
    assert len(cliente.urls) - primeiras <= primeiras // 2


def test_listar_nao_baixa_nada(capsys):
    assert baixar.main(["--ano", "2026", "--listar"]) == 0
    assert "CVM DFP 2020" in capsys.readouterr().out
