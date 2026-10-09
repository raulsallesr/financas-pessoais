from pathlib import Path

from ativos import paths


def test_paths_respeitam_variaveis_de_ambiente(monkeypatch, tmp_path):
    bruto = tmp_path / "bruto"
    derivado = tmp_path / "derivado"
    monkeypatch.setenv("LASTRO_CACHE_DIR", str(bruto))
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(derivado))

    assert paths.cache_bruto_dir() == bruto
    assert paths.dados_derivados_dir() == derivado
    assert paths.caminho_acoes() == derivado / "acoes.parquet"
    assert paths.caminho_meta_acoes() == derivado / "acoes_meta.json"
    assert paths.caminho_fiis() == derivado / "fiis.parquet"
    assert paths.caminho_meta_fiis() == derivado / "fiis_meta.json"


def test_paths_padrao_ficam_fora_do_repositorio(monkeypatch):
    monkeypatch.delenv("LASTRO_CACHE_DIR", raising=False)
    monkeypatch.delenv("LASTRO_DADOS_DIR", raising=False)

    assert paths.cache_bruto_dir() == Path.home() / ".cache" / "lastro" / "raw"
    assert paths.dados_derivados_dir() == Path.home() / ".cache" / "lastro" / "derived"
