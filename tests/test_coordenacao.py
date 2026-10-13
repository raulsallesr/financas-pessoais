from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from scripts import equipe

ROOT = Path(__file__).resolve().parents[1]
COORD = ROOT / "docs" / "coordenacao"


def records(folder: str) -> list[tuple[Path, dict[str, str]]]:
    result: list[tuple[Path, dict[str, str]]] = []
    for path in sorted((COORD / folder).glob("*.md")):
        if path.name.startswith("_") or path.name.lower() == "readme.md":
            continue
        fields, _ = equipe.parse_front_matter(path)
        result.append((path, fields))
    return result


def test_coordination_records_have_required_fields() -> None:
    required = {
        "reservas": {"item", "agente", "maquina", "desde", "expira", "arquivos"},
        "diario": {"data", "maquina", "agente", "itens", "commit", "suite", "cobertura"},
        "ideias": {"data", "origem", "status"},
        "decisoes": {"data", "quem", "status"},
        "checkpoints": {
            "data",
            "commit",
            "suite",
            "cobertura",
            "ciclo",
            "dados_cotacao",
            "dados_gerado_em",
        },
    }
    for folder, fields_required in required.items():
        for path, fields in records(folder):
            assert fields_required <= fields.keys(), f"campos ausentes em {path}"


def test_journal_names_follow_protocol() -> None:
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{4}_[a-z0-9-]+-[a-z0-9-]+\.md$")
    for path, _ in records("diario"):
        assert pattern.fullmatch(path.name), path.name


def test_reservations_are_unique_and_expire_after_start() -> None:
    items: list[str] = []
    for path, fields in records("reservas"):
        since = datetime.fromisoformat(fields["desde"])
        expires = datetime.fromisoformat(fields["expira"])
        assert expires >= since, path.name
        items.append(fields["item"])
    assert len(items) == len(set(items))


def test_quadro_has_unique_ids_and_valid_statuses() -> None:
    rows = equipe.parse_quadro(COORD / "QUADRO.md")
    ids = [row["ID"] for row in rows]
    assert rows
    assert len(ids) == len(set(ids))
    assert {row["Status"] for row in rows} <= equipe.VALID_STATUSES
    assert {row["Decisão do Raul"] for row in rows} <= {"", "sim"}


def test_claude_hook_is_valid_and_has_no_permissions() -> None:
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert "permissions" not in settings
    hooks = settings["hooks"]["SessionStart"]
    commands = [hook["command"] for group in hooks for hook in group["hooks"]]
    assert commands == ["python scripts/equipe.py iniciar --hook"]


def test_robot_workflows_rebase_before_push_with_three_attempts() -> None:
    for name in ("atualizar-curva.yml", "atualizar-focus.yml"):
        text = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        pull = "git pull --rebase --autostash origin main"
        assert pull in text
        assert text.index(pull) < text.index("git push")
        assert "for tentativa in 1 2 3" in text
        assert "[skip ci]" in text
        assert "contents: write" in text


def test_workflow_atualizar_ativos_publica_release_com_guardas() -> None:
    text = (ROOT / ".github" / "workflows" / "atualizar-ativos.yml").read_text(
        encoding="utf-8"
    )

    for trecho in (
        "schedule:",
        'cron: "0 22 * * 1-5"',
        "workflow_dispatch:",
        "push:",
        'paths:\n      - ".github/workflows/atualizar-ativos.yml"',
        "contents: write",
        "group: atualizar-ativos",
        "cancel-in-progress: false",
        "actions/setup-python@v5",
        'python-version: "3.13"',
        "cache-dependency-path: requirements.txt",
        "actions/cache@v4",
        "path: ${{ runner.temp }}/lastro/raw",
        'echo "LASTRO_CACHE_DIR=$RUNNER_TEMP/lastro/raw" >> "$GITHUB_ENV"',
        'echo "LASTRO_DADOS_DIR=$RUNNER_TEMP/lastro/derived" >> "$GITHUB_ENV"',
        "lastro-raw-v1-${{ github.run_id }}",
        "python -m pip install -r requirements.txt",
        "python -m scripts.baixar_dados_ativos",
        "python -m scripts.atualizar_ativos",
        "gh release create dados-ativos",
        "gh release upload dados-ativos",
        "gh release edit dados-ativos",
        "--prerelease",
        "--latest=false",
        "--clobber",
        "len(acoes) < 100",
        "len(fiis) < 50",
    ):
        assert trecho in text
    assert "secrets." not in text
    assert "pull_request_target" not in text
    # O contexto `runner` não existe no `env` do job: o GitHub rejeita o arquivo inteiro.
    job_env = text.split("    steps:", 1)[0].split("    timeout-minutes:", 1)[-1]
    assert "runner." not in job_env
    assert (chr(10) + "    env:") not in text.split("    steps:", 1)[0]


def test_public_coordination_files_do_not_contain_secrets() -> None:
    paths = [
        path
        for path in COORD.rglob("*")
        if path.is_file()
    ] + [ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "scripts" / "equipe.py"]
    assert equipe.scan_secrets(paths) == []


def test_secret_scanner_catches_planted_fake_secret(tmp_path: Path) -> None:
    planted = tmp_path / "planted.md"
    planted.write_text(
        "chave: AKIAABCDEFGHIJKLMNOP\ncontato: alguem@example.com\n",
        encoding="utf-8",
    )

    findings = equipe.scan_secrets([planted])

    assert {value for _, value in findings} == {
        "AKIAABCDEFGHIJKLMNOP",
        "alguem@example.com",
    }


def test_pytest_do_ci_enxerga_a_raiz_do_projeto() -> None:
    """O CI roda o executável `pytest`, que não põe a raiz em sys.path.

    Sem `pythonpath` no pyproject, `import ativos` e `from scripts import ...` falham na
    coleta (exit code 2) e o CI fica vermelho enquanto `python -m pytest` passa local.
    """
    pyproject = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(
        encoding="utf-8"
    )

    assert "[tool.pytest.ini_options]" in pyproject
    assert 'pythonpath = ["."]' in pyproject
