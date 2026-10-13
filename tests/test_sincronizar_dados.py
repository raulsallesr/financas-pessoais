from __future__ import annotations

import io
import json
import subprocess
import urllib.error
from pathlib import Path

import pandas as pd
import pytest

from scripts import sincronizar_dados as sincronizar

REPO = "dono/projeto"
API_URL = f"https://api.github.com/repos/{REPO}/releases/tags/dados-ativos"
BASE_URL = "https://downloads.example/"


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


class FakeClient:
    def __init__(self, responses: dict[str, bytes | Exception]):
        self.responses = responses
        self.calls: list[tuple[str, int, str | None]] = []

    def urlopen(self, request, timeout: int):
        url = request.full_url
        self.calls.append((url, timeout, request.get_header("User-agent")))
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        return FakeResponse(response)


def _parquet_bytes(*tickers: str, incluir_preco: bool = True) -> bytes:
    frame = pd.DataFrame({"ticker": list(tickers)})
    if incluir_preco:
        frame["preco"] = [10.0 + indice for indice in range(len(tickers))]
    buffer = io.BytesIO()
    frame.to_parquet(buffer, index=False)
    return buffer.getvalue()


def _meta(classe: str, gerado_em: str = "2026-10-13T20:00:00-03:00") -> dict[str, object]:
    return {
        "schema_version": sincronizar.SCHEMAS_SUPORTADOS[f"{classe}_meta.json"],
        "data_cotacao": "2026-10-13",
        "gerado_em": gerado_em,
        "linhas": 2 if classe == "acoes" else 1,
    }


def _json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def _responses(
    *,
    acoes_meta: dict[str, object] | None = None,
    fiis_meta: dict[str, object] | None = None,
) -> dict[str, bytes | Exception]:
    assets = [
        {"name": name, "browser_download_url": BASE_URL + name}
        for name in sincronizar.ASSETS
    ]
    return {
        API_URL: _json_bytes({"assets": assets}),
        BASE_URL + "acoes.parquet": _parquet_bytes("AAA3", "BBB4"),
        BASE_URL + "acoes_meta.json": _json_bytes(acoes_meta or _meta("acoes")),
        BASE_URL + "fiis.parquet": _parquet_bytes("FIIA11"),
        BASE_URL + "fiis_meta.json": _json_bytes(fiis_meta or _meta("fiis")),
    }


def _gravar_lote_local(pasta: Path, *, gerado_em: str = "2026-10-12T20:00:00-03:00") -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    payloads = _responses(
        acoes_meta=_meta("acoes", gerado_em),
        fiis_meta=_meta("fiis", gerado_em),
    )
    for name in sincronizar.ASSETS:
        conteudo = payloads[BASE_URL + name]
        assert isinstance(conteudo, bytes)
        (pasta / name).write_bytes(conteudo)


def test_sincroniza_valida_substitui_pula_segunda_execucao_e_forca(tmp_path: Path) -> None:
    destino = tmp_path / "derived"
    mensagens: list[str] = []
    primeira = FakeClient(_responses())

    alterou = sincronizar.executar(
        repo=REPO,
        pasta_derivada=destino,
        cliente=primeira,
        saida=mensagens.append,
    )

    assert alterou is True
    assert {path.name for path in destino.iterdir()} == set(sincronizar.ASSETS)
    assert pd.read_parquet(destino / "acoes.parquet")["ticker"].tolist() == ["AAA3", "BBB4"]
    assert "Linhas: ações 2; FIIs 1" in mensagens[-1]
    assert [url for url, _, _ in primeira.calls] == [
        API_URL,
        BASE_URL + "acoes_meta.json",
        BASE_URL + "acoes.parquet",
        BASE_URL + "fiis.parquet",
        BASE_URL + "fiis_meta.json",
    ]
    assert {timeout for _, timeout, _ in primeira.calls} == {30}
    assert {agent for _, _, agent in primeira.calls} == {sincronizar.USER_AGENT}

    segunda = FakeClient(_responses())
    assert not sincronizar.executar(
        repo=REPO,
        pasta_derivada=destino,
        cliente=segunda,
        saida=mensagens.append,
    )
    assert len(segunda.calls) == 2
    assert "iguais ou mais novos" in mensagens[-1]

    forçada = FakeClient(_responses())
    assert sincronizar.executar(
        repo=REPO,
        forcar=True,
        pasta_derivada=destino,
        cliente=forçada,
        saida=mensagens.append,
    )
    assert len(forçada.calls) == 5


@pytest.mark.parametrize(
    ("local_gerado_em", "espera_download"),
    [
        (None, True),
        ("2026-10-12T20:00:00-03:00", True),
        ("2026-10-13T20:00:00-03:00", False),
        ("2026-10-14T20:00:00-03:00", False),
    ],
)
def test_compara_gerado_em_local_ausente_mais_velho_igual_ou_mais_novo(
    tmp_path: Path, local_gerado_em: str | None, espera_download: bool
) -> None:
    destino = tmp_path / "derived"
    if local_gerado_em:
        _gravar_lote_local(destino, gerado_em=local_gerado_em)
    cliente = FakeClient(_responses())

    alterou = sincronizar.executar(
        repo=REPO,
        pasta_derivada=destino,
        cliente=cliente,
        saida=lambda _message: None,
    )

    assert alterou is espera_download
    assert len(cliente.calls) == (5 if espera_download else 2)


@pytest.mark.parametrize(
    ("cenario", "mensagem"),
    [
        ("release_404", "não existe"),
        ("asset_ausente", "assets obrigatórios"),
        ("parquet_corrompido", "corrompido ou ilegível"),
        ("parquet_sem_coluna", "colunas mínimas"),
        ("json_sem_schema", "não contém schema_version"),
        ("schema_nao_suportado", "esquema não suportado"),
    ],
)
def test_falhas_retornam_um_e_preservam_lote_anterior(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    cenario: str,
    mensagem: str,
) -> None:
    destino = tmp_path / "derived"
    _gravar_lote_local(destino)
    anteriores = {name: (destino / name).read_bytes() for name in sincronizar.ASSETS}
    responses = _responses()
    if cenario == "release_404":
        responses[API_URL] = urllib.error.HTTPError(API_URL, 404, "Not Found", None, None)
    elif cenario == "asset_ausente":
        payload = json.loads(responses[API_URL])
        payload["assets"] = [
            asset for asset in payload["assets"] if asset["name"] != "fiis.parquet"
        ]
        responses[API_URL] = _json_bytes(payload)
    elif cenario == "parquet_corrompido":
        responses[BASE_URL + "acoes.parquet"] = b"nao-e-parquet"
    elif cenario == "parquet_sem_coluna":
        responses[BASE_URL + "fiis.parquet"] = _parquet_bytes(
            "FIIA11", incluir_preco=False
        )
    elif cenario == "json_sem_schema":
        meta = _meta("acoes")
        del meta["schema_version"]
        responses[BASE_URL + "acoes_meta.json"] = _json_bytes(meta)
    else:
        meta = _meta("fiis")
        meta["schema_version"] = 999
        responses[BASE_URL + "fiis_meta.json"] = _json_bytes(meta)
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(destino))

    result = sincronizar.main(["--repo", REPO, "--forcar"], cliente=FakeClient(responses))

    assert result == 1
    assert mensagem in capsys.readouterr().err
    assert {name: (destino / name).read_bytes() for name in sincronizar.ASSETS} == anteriores


def test_sem_rede_falha_limpo_sem_chamar_cliente(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class ClienteProibido:
        def urlopen(self, *_args, **_kwargs):
            raise AssertionError("não deveria acessar a rede")

    monkeypatch.setenv("LASTRO_DADOS_DIR", str(tmp_path / "derived"))

    result = sincronizar.main(["--repo", REPO, "--sem-rede"], cliente=ClienteProibido())

    assert result == 1
    assert capsys.readouterr().err == (
        "Erro: rede desativada por --sem-rede; nenhum arquivo local foi alterado\n"
    )
    assert not (tmp_path / "derived").exists()


def test_resolve_repositorio_explicito_origin_e_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    assert sincronizar.resolver_repositorio("dono/projeto.git") == "dono/projeto"
    with pytest.raises(sincronizar.ErroSincronizacao, match="dono/nome"):
        sincronizar.resolver_repositorio("invalido")

    monkeypatch.setattr(sincronizar, "_repositorio_da_origem", lambda: "origem/projeto")
    assert sincronizar.resolver_repositorio(None) == "origem/projeto"
    monkeypatch.setattr(sincronizar, "_repositorio_da_origem", lambda: None)
    assert sincronizar.resolver_repositorio(None) == sincronizar.DEFAULT_REPOSITORY


@pytest.mark.parametrize(
    ("origin", "esperado"),
    [
        ("git@github.com:dono/projeto.git\n", "dono/projeto"),
        ("https://github.com/dono/projeto.git\n", "dono/projeto"),
        ("https://example.com/dono/projeto.git\n", None),
    ],
)
def test_extrai_repositorio_do_remote_origin(
    monkeypatch: pytest.MonkeyPatch, origin: str, esperado: str | None
) -> None:
    result = subprocess.CompletedProcess([], 0, origin, "")
    monkeypatch.setattr(sincronizar.subprocess, "run", lambda *_args, **_kwargs: result)

    assert sincronizar._repositorio_da_origem() == esperado
