from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from scripts import equipe

NOW = "2026-10-13T12:00"
TABLE = """# Quadro

| ID | Item | Status | Dono | Atualizado | Decisão do Raul | Notas |
|---|---|---|---|---|---|---|
| 0.1 | Protocolo | aberto | | 2026-10-13 | | base |
| 1.2 | Qualidade | aberto | | 2026-10-13 | | próximo |
| 1.7 | Nome | aberto | | 2026-10-13 | sim | Raul decide |
"""


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check and result.returncode:
        raise AssertionError(result.stderr or result.stdout)
    return result


def configure_git(root: Path, name: str = "Test Agent") -> None:
    git(root, "config", "user.name", name)
    git(root, "config", "user.email", "test@users.noreply.github.com")


def commit_all(root: Path, message: str = "base") -> str:
    git(root, "add", "-A")
    git(root, "commit", "-m", message)
    return git(root, "rev-parse", "HEAD").stdout.strip()


def make_repo(tmp_path: Path, *, remote: bool = False) -> tuple[Path, Path | None]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-b", "main")
    configure_git(root)
    coord = root / "docs" / "coordenacao"
    for folder in ("reservas", "diario", "ideias", "decisoes", "checkpoints"):
        (coord / folder).mkdir(parents=True)
    (coord / "QUADRO.md").write_text(TABLE, encoding="utf-8")
    (root / "dados").mkdir()
    (root / "dados" / "curva_prefixada_cache.json").write_text(
        json.dumps({"atualizado_em": "2026-10-13"}), encoding="utf-8"
    )
    (root / "code.py").write_text("VALUE = 1\n", encoding="utf-8")
    commit_all(root)
    bare = None
    if remote:
        bare = tmp_path / "remote.git"
        bare.mkdir()
        git(bare, "init", "--bare", "-b", "main")
        git(root, "remote", "add", "origin", str(bare))
        git(root, "push", "-u", "origin", "main")
    return root, bare


def clone_repo(bare: Path, target: Path, name: str) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "-b", "main", str(bare), str(target)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    configure_git(target, name)
    return target


def quadro_por_id(root: Path) -> dict[str, dict[str, str]]:
    quadro = root / "docs" / "coordenacao" / "QUADRO.md"
    return {row["ID"]: row for row in equipe.parse_quadro(quadro)}


def set_cli_env(monkeypatch: pytest.MonkeyPatch, root: Path, now: str = NOW) -> None:
    monkeypatch.setenv("EQUIPE_RAIZ", str(root))
    monkeypatch.setenv("EQUIPE_AGORA", now)
    monkeypatch.delenv("EQUIPE_AGENTE", raising=False)
    monkeypatch.delenv("EQUIPE_MAQUINA", raising=False)


def call(monkeypatch: pytest.MonkeyPatch, root: Path, *args: str) -> int:
    set_cli_env(monkeypatch, root)
    return equipe.main(list(args))


def write_reservation(
    root: Path,
    *,
    item: str = "0.1",
    agent: str = "codex",
    machine: str = "trabalho",
    since: str = "2026-10-13T10:00",
    expires: str = "2026-10-14T10:00",
    files: str = "code.py",
) -> Path:
    path = root / "docs" / "coordenacao" / "reservas" / f"{item}.md"
    path.write_text(
        "---\n"
        f"item: {item}\n"
        f"agente: {agent}\n"
        f"maquina: {machine}\n"
        f"desde: {since}\n"
        f"expira: {expires}\n"
        f"arquivos: {files}\n"
        "---\nReserva.\n",
        encoding="utf-8",
    )
    return path


def test_front_matter_parser_is_tolerant(tmp_path: Path) -> None:
    path = tmp_path / "record.md"
    path.write_text(
        "\ufeff---\nItem: 1.6b\nlinha inválida\nstatus: nova\n---\n# Corpo\n",
        encoding="utf-8",
    )

    fields, body = equipe.parse_front_matter(path)

    assert fields == {"item": "1.6b", "status": "nova"}
    assert body == "# Corpo\n"
    assert equipe.parse_front_matter_text("sem bloco") == ({}, "sem bloco")


def test_quadro_parser_and_single_line_edit_preserve_other_bytes(tmp_path: Path) -> None:
    path = tmp_path / "QUADRO.md"
    original = TABLE.replace("\n", "\r\n")
    path.write_bytes(original.encode("utf-8"))

    assert [row["ID"] for row in equipe.parse_quadro(path)] == ["0.1", "1.2", "1.7"]
    assert equipe.update_quadro_item(path, "1.2", {"Status": "em andamento", "Dono": "codex-casa"})

    before = original.splitlines(keepends=True)
    after = path.read_bytes().decode("utf-8").splitlines(keepends=True)
    differences = [
        index
        for index, pair in enumerate(zip(before, after, strict=True))
        if pair[0] != pair[1]
    ]
    assert differences == [5]
    assert "| 1.2 | Qualidade | em andamento | codex-casa |" in after[5]
    assert not equipe.update_quadro_item(path, "9.9", {"Status": "pronto"})


def test_reservar_pushes_and_second_attempt_returns_two(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, bare = make_repo(tmp_path, remote=True)
    assert bare

    result = call(
        monkeypatch,
        root,
        "reservar",
        "0.1",
        "--agente",
        "codex",
        "--maquina",
        "casa",
        "--arquivos",
        "scripts/equipe.py, tests/test_equipe.py",
    )

    assert result == 0
    verification = clone_repo(bare, tmp_path / "verification", "Verifier")
    fields, _ = equipe.parse_front_matter(
        verification / "docs" / "coordenacao" / "reservas" / "0.1.md"
    )
    assert fields["agente"] == "codex"
    assert fields["expira"] == "2026-10-14T12:00"
    row = next(
        row
        for row in equipe.parse_quadro(verification / "docs/coordenacao/QUADRO.md")
        if row["ID"] == "0.1"
    )
    assert row["Dono"] == "codex-casa"
    assert call(monkeypatch, root, "reservar", "0.1", "--agente", "outra", "--maquina", "pc") == 2
    assert "já reservado" in capsys.readouterr().err


def test_reservar_replaces_expired_and_requires_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _ = make_repo(tmp_path)
    write_reservation(root, expires="2026-10-13T11:59")
    commit_all(root, "expired")

    assert (
        call(
            monkeypatch,
            root,
            "reservar",
            "0.1",
            "--agente",
            "claude",
            "--maquina",
            "casa",
            "--sem-push",
        )
        == 0
    )
    fields, _ = equipe.parse_front_matter(root / "docs/coordenacao/reservas/0.1.md")
    assert fields["agente"] == "claude"
    assert "será substituída" in capsys.readouterr().out

    assert call(monkeypatch, root, "reservar", "1.2", "--sem-push") == 1
    assert "agente e máquina" in capsys.readouterr().err


def test_reservar_push_collision_rolls_back_local_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seed, bare = make_repo(tmp_path / "seed", remote=True)
    assert seed and bare
    first = clone_repo(bare, tmp_path / "first", "First")
    second = clone_repo(bare, tmp_path / "second", "Second")
    second_head = git(second, "rev-parse", "HEAD").stdout.strip()
    monkeypatch.setattr(equipe, "_initial_pull", lambda _root: None)

    assert call(monkeypatch, first, "reservar", "0.1", "--agente", "a", "--maquina", "pc1") == 0
    assert call(monkeypatch, second, "reservar", "0.1", "--agente", "b", "--maquina", "pc2") == 3

    assert git(second, "rev-parse", "HEAD").stdout.strip() == second_head
    assert not (second / "docs/coordenacao/reservas/0.1.md").exists()
    assert "colisão: outra IA reservou este item" in capsys.readouterr().err


def test_fechar_green_writes_journal_releases_reservation_and_marks_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _ = make_repo(tmp_path)
    reservation = write_reservation(root)
    equipe.update_quadro_item(
        root / "docs/coordenacao/QUADRO.md",
        "0.1",
        {"Status": "em andamento", "Dono": "codex-trabalho"},
    )
    commit_all(root, "reservation")
    monkeypatch.setattr(equipe, "_run_gate", lambda _root: (True, "12 passed", "91.5"))

    result = call(
        monkeypatch,
        root,
        "fechar",
        "--resumo",
        "Implementei tudo. Evidência adicional.",
        "--proximo",
        "Revisar.",
        "--decisao",
        "Nenhuma fora da spec.",
        "--itens",
        "0.1",
        "--pronto",
        "0.1",
        "--agente",
        "codex",
        "--maquina",
        "trabalho",
        "--sem-push",
    )

    assert result == 0
    assert not reservation.exists()
    journal = root / "docs/coordenacao/diario/2026-10-13_1200_trabalho-codex.md"
    fields, body = equipe.parse_front_matter(journal)
    assert fields["suite"] == "12 passed"
    assert fields["cobertura"] == "91.5"
    assert fields["itens"] == "0.1"
    assert "# Implementei tudo." in body
    assert "## Fatos automáticos" in body
    row = next(
        row
        for row in equipe.parse_quadro(root / "docs/coordenacao/QUADRO.md")
        if row["ID"] == "0.1"
    )
    assert row["Status"] == "pronto"
    assert row["Dono"] == ""
    assert (root / "docs/coordenacao/INDICE.md").exists()
    assert git(root, "status", "--short").stdout == ""


def test_fechar_red_gate_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _ = make_repo(tmp_path)
    monkeypatch.setattr(equipe, "_run_gate", lambda _root: (False, "falhou", "70"))

    result = call(
        monkeypatch,
        root,
        "fechar",
        "--resumo",
        "Falharia.",
        "--proximo",
        "Corrigir.",
        "--agente",
        "codex",
        "--maquina",
        "casa",
        "--sem-push",
    )

    assert result == 4
    assert not list((root / "docs/coordenacao/diario").glob("*.md"))
    assert not (root / "docs/coordenacao/INDICE.md").exists()


def test_fechar_refuses_dirty_code_and_forcar_accepts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _ = make_repo(tmp_path)
    (root / "code.py").write_text("VALUE = 2\n", encoding="utf-8")
    base_args = (
        "fechar",
        "--resumo",
        "Registro forçado.",
        "--proximo",
        "Commitar código.",
        "--agente",
        "codex",
        "--maquina",
        "casa",
        "--sem-gate",
        "--sem-push",
    )

    assert call(monkeypatch, root, *base_args) == 1
    assert not list((root / "docs/coordenacao/diario").glob("*.md"))
    assert call(monkeypatch, root, *base_args, "--forcar") == 0
    fields, _ = equipe.parse_front_matter(
        root / "docs/coordenacao/diario/2026-10-13_1200_casa-codex.md"
    )
    assert fields["suite"] == "nao rodada"


def test_fechar_resolves_only_index_conflict_between_two_clones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, bare = make_repo(tmp_path / "seed", remote=True)
    assert bare
    first = clone_repo(bare, tmp_path / "first", "First")
    second = clone_repo(bare, tmp_path / "second", "Second")
    common = ("fechar", "--resumo", "Sessão.", "--proximo", "Fim.", "--sem-gate")

    assert call(monkeypatch, first, *common, "--agente", "a", "--maquina", "pc1") == 0
    assert call(monkeypatch, second, *common, "--agente", "b", "--maquina", "pc2") == 0

    verification = clone_repo(bare, tmp_path / "verify", "Verifier")
    journals = list((verification / "docs/coordenacao/diario").glob("*.md"))
    assert {path.name for path in journals} == {
        "2026-10-13_1200_pc1-a.md",
        "2026-10-13_1200_pc2-b.md",
    }
    index = (verification / "docs/coordenacao/INDICE.md").read_text(encoding="utf-8")
    assert "pc1-a" in index
    assert "pc2-b" in index


def test_fechar_aborts_on_non_index_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, bare = make_repo(tmp_path / "seed", remote=True)
    assert bare
    first = clone_repo(bare, tmp_path / "first", "First")
    second = clone_repo(bare, tmp_path / "second", "Second")
    args = (
        "fechar",
        "--resumo",
        "Resumo A.",
        "--proximo",
        "Fim.",
        "--sem-gate",
        "--agente",
        "igual",
        "--maquina",
        "pc",
    )

    assert call(monkeypatch, first, *args) == 0
    conflicting = list(args)
    conflicting[2] = "Resumo B."
    assert call(monkeypatch, second, *conflicting) == 3
    assert not (second / ".git" / "rebase-merge").exists()


def test_iniciar_reports_remote_commits_dirty_tree_expired_reservation_and_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, bare = make_repo(tmp_path, remote=True)
    assert bare
    producer = clone_repo(bare, tmp_path / "producer", "github-actions[bot]")
    (producer / "bot.txt").write_text("bot\n", encoding="utf-8")
    commit_all(producer, "Atualiza cache")
    assert equipe._push_origin(producer).returncode == 0
    configure_git(producer, "Pessoa")
    (producer / "human.txt").write_text("human\n", encoding="utf-8")
    commit_all(producer, "Mudança humana")
    assert equipe._push_origin(producer).returncode == 0
    (root / "dados" / "noise.json").write_text("{}", encoding="utf-8")
    (root / "code.py").write_text("VALUE = 3\n", encoding="utf-8")
    write_reservation(root, expires="2026-10-13T11:00")

    assert call(monkeypatch, root, "iniciar") == 0
    report = capsys.readouterr().out
    assert "robô 1; demais 1" in report
    assert "Mudança humana" in report
    assert "code.py" in report
    assert "dados/noise.json" not in report
    assert "Reservas vencidas" in report
    assert len(report.splitlines()) <= 40

    assert call(monkeypatch, root, "iniciar", "--prompt", "--sem-rede") == 0
    prompt = capsys.readouterr().out
    assert "2026-10-13 12:00" in prompt
    assert git(root, "rev-parse", "--short", "HEAD").stdout.strip() in prompt
    assert "Próximo item aberto: 0.1 Protocolo" in prompt
    assert "reserve antes de editar" in prompt


def test_iniciar_offline_without_remote_and_hook_failure_are_safe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _ = make_repo(tmp_path)

    assert call(monkeypatch, root, "iniciar", "--sem-rede") == 0
    assert "origin/main indisponível" in capsys.readouterr().out
    set_cli_env(monkeypatch, root, "data-inválida")
    assert equipe.main(["iniciar", "--hook"]) == 0
    assert capsys.readouterr().out == ""


def test_ideia_slug_suffix_decision_substitution_and_index_idempotence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _ = make_repo(tmp_path)
    for _ in range(2):
        assert call(
            monkeypatch,
            root,
            "ideia",
            "Ação & Tesouro IPCA+",
            "--origem",
            "codex-casa",
            "--corpo",
            "Comparar métodos.",
            "--sem-push",
        ) == 0
    ideas = sorted((root / "docs/coordenacao/ideias").glob("*.md"))
    assert [path.name for path in ideas] == [
        "2026-10-13_acao-tesouro-ipca-2.md",
        "2026-10-13_acao-tesouro-ipca.md",
    ]

    assert call(
        monkeypatch,
        root,
        "decisao",
        "Escolha inicial",
        "--decisao",
        "Usar A.",
        "--porque",
        "É simples.",
        "--quem",
        "raul",
        "--sem-push",
    ) == 0
    old = "2026-10-13_escolha-inicial.md"
    assert call(
        monkeypatch,
        root,
        "decisao",
        "Escolha final",
        "--decisao",
        "Usar B.",
        "--porque",
        "É robusto.",
        "--alternativas",
        "A.",
        "--substitui",
        old,
        "--sem-push",
    ) == 0
    old_fields, _ = equipe.parse_front_matter(root / "docs/coordenacao/decisoes" / old)
    new_fields, _ = equipe.parse_front_matter(
        root / "docs/coordenacao/decisoes/2026-10-13_escolha-final.md"
    )
    assert old_fields["status"] == "substituida"
    assert new_fields["status"] == "vigente"

    index = equipe.generate_index(root, datetime(2026, 10, 13, 12, 0))
    first = index.read_bytes()
    equipe.generate_index(root, datetime(2026, 10, 13, 18, 0))
    assert index.read_bytes() == first
    assert "Escolha final" in first.decode("utf-8")
    assert "Escolha inicial" not in first.decode("utf-8")


def test_checkpoint_numbers_reads_metadata_and_creates_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _ = make_repo(tmp_path)
    derived = tmp_path / "derived"
    derived.mkdir()
    (derived / "acoes_meta.json").write_text(
        json.dumps({"data_cotacao": "2026-10-10", "gerado_em": "2026-10-11T09:00"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("LASTRO_DADOS_DIR", str(derived))

    assert (
        call(
            monkeypatch,
            root,
            "checkpoint",
            "--ciclo",
            "1",
            "--sem-gate",
            "--tag",
            "--sem-push",
        )
        == 0
    )
    assert call(monkeypatch, root, "checkpoint", "--ciclo", "2", "--sem-gate", "--sem-push") == 0

    checkpoints = sorted((root / "docs/coordenacao/checkpoints").glob("ckpt-*.md"))
    assert [path.name for path in checkpoints] == ["ckpt-001.md", "ckpt-002.md"]
    fields, body = equipe.parse_front_matter(checkpoints[0])
    assert fields["dados_cotacao"] == "2026-10-10"
    assert fields["dados_gerado_em"] == "2026-10-11T09:00"
    assert "- pronto: 0" in body
    assert git(root, "tag", "--list").stdout.strip() == "ckpt-001"


def test_helpers_cover_paths_time_and_secret_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EQUIPE_AGORA", "2026-10-13T12:34")
    assert equipe.current_time() == datetime(2026, 10, 13, 12, 34)
    assert equipe.parse_iso("inválido") is None
    assert equipe.slugify("Árvore / Coração") == "arvore-coracao"
    assert equipe._path_matches("tests/test_x.py", ["tests/*.py"])
    assert equipe._ignored_status_path(".pytest_cache/a")
    secret = tmp_path / "secret.md"
    secret.write_text("token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ e pessoa@example.com", encoding="utf-8")
    findings = equipe.scan_secrets([secret])
    assert {finding for _, finding in findings} == {
        "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "pessoa@example.com",
    }


def test_comandos_que_publicam_recusam_branch_diferente_de_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, bare = make_repo(tmp_path, remote=True)
    assert bare
    git(root, "checkout", "-b", "refatoracao-1-6b")

    result = call(
        monkeypatch, root, "reservar", "0.1", "--agente", "codex", "--maquina", "casa"
    )

    assert result == 1
    assert "refatoracao-1-6b" in capsys.readouterr().err
    assert not (root / "docs" / "coordenacao" / "reservas" / "0.1.md").exists()
    heads = git(bare, "rev-parse", "refs/heads/main").stdout.strip()
    assert heads == git(root, "rev-parse", "main").stdout.strip()


def test_branch_so_registra_local_com_sem_push_e_com_permissao_explicita(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, bare = make_repo(tmp_path, remote=True)
    assert bare
    git(root, "checkout", "-b", "refatoracao-1-6b")

    sem_push = call(
        monkeypatch,
        root,
        "reservar",
        "0.1",
        "--agente",
        "codex",
        "--maquina",
        "casa",
        "--sem-push",
    )
    monkeypatch.setenv("EQUIPE_PERMITIR_BRANCH", "1")
    git(root, "checkout", "main")
    git(root, "checkout", "-b", "outra")
    permitido = call(
        monkeypatch, root, "reservar", "1.2", "--agente", "codex", "--maquina", "casa"
    )

    assert sem_push == 0
    assert permitido == 0


def test_iniciar_sincroniza_quando_limpo_e_mostra_a_reserva_de_outra_maquina(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, bare = make_repo(tmp_path, remote=True)
    assert bare
    outra = clone_repo(bare, tmp_path / "outra", "Outra Maquina")
    reservou = call(
        monkeypatch, outra, "reservar", "1.2", "--agente", "claude", "--maquina", "casa"
    )
    assert reservou == 0
    capsys.readouterr()

    assert call(monkeypatch, root, "iniciar") == 0
    saida = capsys.readouterr().out

    assert "Sincronizado: +1 commits" in saida
    assert "Reservas ativas:" in saida
    assert "1.2 — claude-casa" in saida


def test_iniciar_nao_toca_na_arvore_suja_de_outra_ia(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, bare = make_repo(tmp_path, remote=True)
    assert bare
    outra = clone_repo(bare, tmp_path / "outra", "Outra Maquina")
    reservou = call(
        monkeypatch, outra, "reservar", "1.2", "--agente", "claude", "--maquina", "casa"
    )
    assert reservou == 0
    codigo = "VALUE = 2  # trabalho de outra IA" + chr(10)
    (root / "code.py").write_text(codigo, encoding="utf-8")
    capsys.readouterr()

    assert call(monkeypatch, root, "iniciar") == 0
    saida = capsys.readouterr().out

    assert "Sincronizado" not in saida
    assert "atrás 1" in saida
    assert (root / "code.py").read_text(encoding="utf-8").endswith("outra IA" + chr(10))
    assert not (root / "docs" / "coordenacao" / "reservas" / "1.2.md").exists()


def test_fechar_resolve_conflito_do_quadro_entre_itens_vizinhos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    casa, bare = make_repo(tmp_path, remote=True)
    assert bare
    trabalho = clone_repo(bare, tmp_path / "trabalho", "Trabalho")
    reservou = call(monkeypatch, casa, "reservar", "0.1", "--agente", "claude", "--maquina", "casa")
    assert reservou == 0
    git(trabalho, "pull", "--rebase", "origin", "main")
    original = equipe._sync_push
    interposto = {"feito": False}

    def interpor(root: Path, **kwargs: object) -> None:
        if root == casa and not interposto["feito"]:
            interposto["feito"] = True
            resultado = call(
                monkeypatch,
                trabalho,
                "reservar",
                "1.2",
                "--agente",
                "codex",
                "--maquina",
                "trabalho",
            )
            assert resultado == 0
            set_cli_env(monkeypatch, casa)
        original(root, **kwargs)

    monkeypatch.setattr(equipe, "_sync_push", interpor)

    resultado = call(
        monkeypatch,
        casa,
        "fechar",
        "--agente",
        "claude",
        "--maquina",
        "casa",
        "--resumo",
        "Item 0.1 concluido.",
        "--proximo",
        "Seguir.",
        "--itens",
        "0.1",
        "--pronto",
        "0.1",
        "--sem-gate",
    )

    assert resultado == 0
    assert interposto["feito"]
    verificacao = clone_repo(bare, tmp_path / "verificacao", "Verificador")
    linhas = quadro_por_id(verificacao)
    assert linhas["0.1"]["Status"] == "pronto"
    assert linhas["0.1"]["Dono"] == ""
    assert linhas["1.2"]["Status"] == "em andamento"
    assert linhas["1.2"]["Dono"] == "codex-trabalho"
    reservas = verificacao / "docs" / "coordenacao" / "reservas"
    assert (reservas / "1.2.md").exists()
    assert not (reservas / "0.1.md").exists()
    assert not (casa / ".git" / "rebase-merge").exists()


def test_fechar_aborta_quando_o_remoto_mostra_outro_dono_no_mesmo_item(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    casa, bare = make_repo(tmp_path, remote=True)
    assert bare
    trabalho = clone_repo(bare, tmp_path / "trabalho", "Trabalho")
    reservou = call(monkeypatch, casa, "reservar", "1.2", "--agente", "claude", "--maquina", "casa")
    assert reservou == 0
    git(trabalho, "pull", "--rebase", "origin", "main")
    quadro = trabalho / "docs" / "coordenacao" / "QUADRO.md"
    assert equipe.update_quadro_item(quadro, "1.2", {"Dono": "outra-pc", "Status": "em andamento"})
    git(trabalho, "add", "docs/coordenacao/QUADRO.md")
    git(trabalho, "commit", "-m", "edicao manual do quadro")
    git(trabalho, "push", "origin", "main")
    capsys.readouterr()

    resultado = call(
        monkeypatch,
        casa,
        "fechar",
        "--agente",
        "claude",
        "--maquina",
        "casa",
        "--resumo",
        "Item 1.2 concluido.",
        "--proximo",
        "Seguir.",
        "--itens",
        "1.2",
        "--pronto",
        "1.2",
        "--sem-gate",
    )

    assert resultado == 3
    assert "conflito de git" in capsys.readouterr().err
    assert not (casa / ".git" / "rebase-merge").exists()
    verificacao = clone_repo(bare, tmp_path / "verificacao", "Verificador")
    linhas = quadro_por_id(verificacao)
    assert linhas["1.2"]["Dono"] == "outra-pc"
