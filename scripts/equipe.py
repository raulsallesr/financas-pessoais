"""Coordenação local entre IAs e máquinas do projeto Lastro.

Este módulo usa somente a biblioteca padrão para poder rodar antes da criação
do ambiente virtual. A interface pública é ``python scripts/equipe.py``.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any

GIT_TIMEOUT = 20
FETCH_TIMEOUT = 15
API_TIMEOUT = 5
VALID_STATUSES = {"aberto", "em andamento", "pronto", "bloqueado"}
COORD = Path("docs/coordenacao")
SECRET_PATTERNS = (
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
)
EMAIL_PATTERN = re.compile(r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])")
ALLOWED_EMAILS = (
    re.compile(r"^noreply@anthropic\.com$", re.IGNORECASE),
    re.compile(r"^[^@]+@users\.noreply\.github\.com$", re.IGNORECASE),
)


class EquipeError(RuntimeError):
    """Erro esperado da CLI, com código de saída estável."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


def _configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    timeout: int = GIT_TIMEOUT,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    try:
        return subprocess.run(
            list(command),
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=process_env,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(list(command), 124, "", str(exc))


def _git(
    root: Path,
    *args: str,
    timeout: int = GIT_TIMEOUT,
    check: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = _run(("git", *args), cwd=root, timeout=timeout, env=env)
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise EquipeError(f"git {' '.join(args)} falhou: {detail or 'erro desconhecido'}")
    return result


def repository_root() -> Path:
    configured = os.environ.get("EQUIPE_RAIZ")
    if configured:
        return Path(configured).expanduser().resolve()
    probe = _run(("git", "rev-parse", "--show-toplevel"), cwd=Path.cwd())
    if probe.returncode == 0 and probe.stdout.strip():
        return Path(probe.stdout.strip()).resolve()
    return Path(__file__).resolve().parent.parent


def current_time() -> datetime:
    fixed = os.environ.get("EQUIPE_AGORA")
    if fixed:
        try:
            return datetime.strptime(fixed, "%Y-%m-%dT%H:%M")
        except ValueError as exc:
            raise EquipeError("EQUIPE_AGORA deve usar o formato AAAA-MM-DDTHH:MM") from exc
    return datetime.now().astimezone().replace(tzinfo=None, second=0, microsecond=0)


def parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.strip()).replace(tzinfo=None)
    except (TypeError, ValueError):
        return None


def parse_front_matter_text(text: str) -> tuple[dict[str, str], str]:
    """Lê front matter simples e tolerante; devolve campos e corpo."""
    normalized = text.lstrip("\ufeff")
    lines = normalized.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, normalized
    fields: dict[str, str] = {}
    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        if key:
            fields[key] = value.strip()
    body = "".join(lines[end + 1 :]) if end is not None else ""
    return fields, body


def parse_front_matter(path: Path) -> tuple[dict[str, str], str]:
    try:
        return parse_front_matter_text(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return {}, ""


def _title_from_body(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _markdown_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(
        (
            path
            for path in folder.glob("*.md")
            if not path.name.startswith("_") and path.name.lower() != "readme.md"
        ),
        key=lambda path: path.name,
    )


def parse_quadro(path: Path) -> list[dict[str, str]]:
    """Lê a tabela do quadro sem depender da posição fixa das colunas."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    headers: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in lines:
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if headers is None and cells and cells[0].lower() == "id":
            headers = cells
            continue
        if headers is None or len(cells) != len(headers):
            continue
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        row = dict(zip(headers, cells, strict=True))
        if row.get("ID"):
            rows.append(row)
    return rows


def update_quadro_item(path: Path, item: str, updates: dict[str, str]) -> bool:
    """Altera somente a linha do ID pedido, mantendo todos os outros bytes."""
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            text = handle.read()
    except OSError:
        return False
    lines = text.splitlines(keepends=True)
    headers: list[str] | None = None
    changed = False
    for index, line in enumerate(lines):
        content = line.rstrip("\r\n")
        ending = line[len(content) :]
        if not content.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in content.strip().strip("|").split("|")]
        if headers is None and cells and cells[0].lower() == "id":
            headers = cells
            continue
        if headers is None or len(cells) != len(headers) or not cells or cells[0] != item:
            continue
        mapping = dict(zip(headers, cells, strict=True))
        mapping.update(updates)
        lines[index] = "| " + " | ".join(mapping[header] for header in headers) + " |" + ending
        changed = True
        break
    if changed:
        _atomic_write(path, "".join(lines))
    return changed


def _replace_front_matter_field(path: Path, key: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"^(\s*{re.escape(key)}\s*:\s*).*$", re.MULTILINE | re.IGNORECASE)
    if not pattern.search(text):
        raise EquipeError(f"campo {key} ausente em {path}")
    _atomic_write(path, pattern.sub(lambda match: match.group(1) + value, text, count=1))


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-equipe")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _split_csv(value: str | None) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _ignored_status_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized == "dados" or normalized.startswith("dados/") or any(
        part.startswith(".pytest") for part in PurePosixPath(normalized).parts
    )


def _dirty_paths(root: Path) -> list[str]:
    result = _git(root, "status", "--porcelain", "--untracked-files=all", "-z")
    if result.returncode:
        return []
    entries = result.stdout.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        status = entry[:2]
        path = entry[3:]
        if status[0] in {"R", "C"} and index < len(entries):
            path = entries[index]
            index += 1
        path = path.replace("\\", "/")
        if not _ignored_status_path(path) and path not in paths:
            paths.append(path)
    return paths


def _reservation_records(root: Path, now: datetime) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in _markdown_files(root / COORD / "reservas"):
        fields, _ = parse_front_matter(path)
        since = parse_iso(fields.get("desde", ""))
        expires = parse_iso(fields.get("expira", ""))
        records.append(
            {
                "path": path,
                "item": fields.get("item", path.stem),
                "agente": fields.get("agente", "?"),
                "maquina": fields.get("maquina", "?"),
                "desde": since,
                "expira": expires,
                "arquivos": _split_csv(fields.get("arquivos")),
                "vencida": expires is not None and expires < now,
            }
        )
    return records


def _age(since: datetime | None, now: datetime) -> str:
    if since is None:
        return "idade desconhecida"
    minutes = max(0, int((now - since).total_seconds() // 60))
    if minutes < 60:
        return f"{minutes}min"
    hours = minutes // 60
    if hours < 48:
        return f"{hours}h"
    return f"{hours // 24}d"


def _path_matches(path: str, patterns: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/")
    for raw_pattern in patterns:
        pattern = raw_pattern.replace("\\", "/")
        while pattern.startswith("./"):
            pattern = pattern[2:]
        if normalized == pattern or normalized.startswith(pattern.rstrip("/") + "/"):
            return True
        if fnmatch.fnmatchcase(normalized, pattern) or PurePosixPath(normalized).match(pattern):
            return True
    return False


def _head(root: Path) -> str:
    result = _git(root, "rev-parse", "--short", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else "sem-commit"


def _branch(root: Path) -> str:
    result = _git(root, "branch", "--show-current")
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return "desconhecida"


def _has_remote(root: Path) -> bool:
    result = _git(root, "remote", "get-url", "origin")
    return result.returncode == 0 and bool(result.stdout.strip())


def _fetch_origin(root: Path) -> subprocess.CompletedProcess[str]:
    return _git(root, "fetch", "origin", timeout=FETCH_TIMEOUT)


def _push_origin(root: Path) -> subprocess.CompletedProcess[str]:
    return _git(root, "push", "origin", "HEAD:main")


def _push_tag(root: Path, name: str) -> subprocess.CompletedProcess[str]:
    return _git(root, "push", "origin", name)


def _network_disabled(explicit: bool = False) -> bool:
    return explicit or os.environ.get("EQUIPE_SEM_REDE") == "1"


def _fetch_is_recent(root: Path, now: datetime) -> bool:
    fetch_head = root / ".git" / "FETCH_HEAD"
    try:
        modified = datetime.fromtimestamp(fetch_head.stat().st_mtime)
    except OSError:
        return False
    return now - modified < timedelta(minutes=10)


def _github_repo(root: Path) -> tuple[str, str] | None:
    result = _git(root, "remote", "get-url", "origin")
    if result.returncode:
        return None
    url = result.stdout.strip().removesuffix(".git")
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+)$", url)
    return (match.group(1), match.group(2)) if match else None


def _ci_status(root: Path) -> str:
    repository = _github_repo(root)
    if not repository:
        return "CI: indisponível"
    owner, name = repository
    url = (
        f"https://api.github.com/repos/{owner}/{name}/actions/workflows/"
        "tests.yml/runs?branch=main&per_page=5"
    )
    request = urllib.request.Request(url, headers={"User-Agent": "lastro-equipe-cli"})
    try:
        with urllib.request.urlopen(request, timeout=API_TIMEOUT) as response:
            payload = json.load(response)
        runs = payload.get("workflow_runs", [])
        latest = runs[0]
        concluded = next((run for run in runs if run.get("status") == "completed"), None)
    except (OSError, ValueError, KeyError, IndexError, urllib.error.URLError):
        return "CI: indisponível"
    if concluded is None:
        return f"CI: {latest.get('status', 'desconhecida')} (sem execução concluída recente)"
    conclusion = concluded.get("conclusion") or "desconhecida"
    date = (concluded.get("updated_at") or concluded.get("created_at") or "sem data")
    date = date.replace("T", " ")[:16]
    sha = str(concluded.get("head_sha", ""))[:7]
    if conclusion in {"failure", "timed_out", "startup_failure"}:
        title = str(concluded.get("display_title", "")).strip()[:60]
        return (
            f"ATENÇÃO: CI VERMELHO na main ({conclusion}, commit {sha}, {date}): {title}. "
            "Prioridade zero: corrija antes de qualquer item (rode o comando do workflow "
            "com o executável pytest e confira o passo que falhou)."
        )
    note = ""
    if latest is not concluded and latest.get("status") != "completed":
        note = f"; nova execução em andamento ({str(latest.get('head_sha', ''))[:7]})"
    return f"CI: {conclusion} em {date} ({sha}){note}"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, UnicodeError):
        return {}


def _data_lines(root: Path, now: datetime) -> list[str]:
    derived = Path(
        os.environ.get("LASTRO_DADOS_DIR", str(Path.home() / ".cache" / "lastro" / "derived"))
    ).expanduser()
    metadata_path = derived / "acoes_meta.json"
    metadata = _read_json(metadata_path)
    lines: list[str] = []
    if metadata:
        quote_date = metadata.get("data_cotacao", "não disponível")
        generated = metadata.get("gerado_em", "não disponível")
        lines.append(f"Dados ativos: cotação {quote_date}; gerados {generated}")
        generated_at = parse_iso(str(generated))
        if generated_at is None or now - generated_at > timedelta(days=3):
            lines.append("Dados ativos defasados; sincronize primeiro com:")
            lines.append("  python -m scripts.sincronizar_dados")
            lines.append("Alternativa completa (~300 MB):")
            lines.append("  python -m scripts.baixar_dados_ativos")
            lines.append("  python -m scripts.atualizar_ativos")
    else:
        lines.append(f"Dados ativos: metadados ausentes em {metadata_path}")
        lines.append("  python -m scripts.sincronizar_dados")
        lines.append("Alternativa completa (~300 MB):")
        lines.append("  python -m scripts.baixar_dados_ativos")
        lines.append("  python -m scripts.atualizar_ativos")
    curve = _read_json(root / "dados" / "curva_prefixada_cache.json")
    if curve.get("atualizado_em"):
        lines.append(f"Curva prefixada: atualizada {curve['atualizado_em']}")
    return lines


def _front_matter_records(folder: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in _markdown_files(folder):
        fields, body = parse_front_matter(path)
        records.append(
            {
                "path": path,
                "fields": fields,
                "title": _title_from_body(body, path.stem),
            }
        )
    return records


def _upstream_lines(root: Path) -> list[str]:
    if _git(root, "rev-parse", "--verify", "origin/main").returncode:
        return ["Git: origin/main indisponível"]
    counts = _git(root, "rev-list", "--left-right", "--count", "HEAD...origin/main")
    try:
        ahead, behind = [int(value) for value in counts.stdout.split()[:2]]
    except (TypeError, ValueError):
        ahead, behind = 0, 0
    lines = [f"Git: à frente {ahead} / atrás {behind} de origin/main"]
    commits = _git(root, "log", "--format=%an%x1f%s", "HEAD..origin/main")
    bots = 0
    people: list[str] = []
    for line in commits.stdout.splitlines():
        author, _, subject = line.partition("\x1f")
        if author.strip().endswith("[bot]"):
            bots += 1
        else:
            people.append(subject.strip())
    if bots or people:
        lines.append(f"Commits novos: robô {bots}; demais {len(people)}")
        lines.extend(f"  {subject}" for subject in people[:3])
    return lines


def _fast_forward_if_clean(root: Path) -> str | None:
    """Traz commits novos de origin/main só se for seguro: sem trabalho local a proteger.

    Árvore suja (fora de dados/) pode ser trabalho de outra IA e nunca é tocada.
    """
    if _branch(root) != "main" or _dirty_paths(root):
        return None
    counts = _git(root, "rev-list", "--left-right", "--count", "HEAD...origin/main")
    try:
        ahead, behind = (int(value) for value in counts.stdout.split())
    except ValueError:
        return None
    if ahead or not behind:
        return None
    merged = _git(root, "merge", "--ff-only", "origin/main")
    if merged.returncode:
        return (
            "Não sincronizei origin/main (alterações locais em dados/); "
            "use git pull --rebase --autostash."
        )
    return f"Sincronizado: +{behind} commits de origin/main."


def _iniciar_lines(root: Path, now: datetime, *, sem_rede: bool, hook: bool) -> list[str]:
    if not (root / ".git").exists():
        raise EquipeError(f"não é um repositório git: {root}")
    fetch_warning = None
    should_fetch = not _network_disabled(sem_rede) and _has_remote(root)
    if hook and _fetch_is_recent(root, now):
        should_fetch = False
    if should_fetch:
        fetched = _fetch_origin(root)
        if fetched.returncode:
            fetch_warning = "Rede: git fetch indisponível; seguindo com o estado local."

    sync_note = _fast_forward_if_clean(root) if should_fetch and not fetch_warning else None

    lines = [f"[EQUIPE] {now:%Y-%m-%d %H:%M} — branch {_branch(root)} @ {_head(root)}"]
    if sync_note:
        lines.append(sync_note)
    lines.extend(_upstream_lines(root))
    if fetch_warning:
        lines.append(fetch_warning)

    reservations = _reservation_records(root, now)
    active = [record for record in reservations if not record["vencida"]]
    expired = [record for record in reservations if record["vencida"]]
    dirty = _dirty_paths(root)
    if dirty:
        lines.append(f"Árvore suja ({len(dirty)}):")
        for path in dirty[:8]:
            owners = [
                f"{record['agente']}-{record['maquina']} (item {record['item']})"
                for record in active
                if _path_matches(path, record["arquivos"])
            ]
            if owners:
                lines.append(f"  {path} — provável dono: {', '.join(owners)}")
            else:
                lines.append(f"  {path}")
        if any(
            not any(_path_matches(path, record["arquivos"]) for record in active)
            for path in dirty[:8]
        ):
            lines.append(
                "  Sem reserva: pode ser trabalho de outra IA; veja o diário; não sobrescreva."
            )
    if active:
        lines.append("Reservas ativas:")
        lines.extend(
            f"  {r['item']} — {r['agente']}-{r['maquina']} ({_age(r['desde'], now)})"
            for r in active
        )
    if expired:
        lines.append("Reservas vencidas:")
        lines.extend(
            f"  {r['item']} — {r['agente']}-{r['maquina']} ({_age(r['desde'], now)})"
            for r in expired
        )

    journals = _front_matter_records(root / COORD / "diario")
    journals.sort(key=lambda record: record["fields"].get("data", ""), reverse=True)
    if journals:
        lines.append("Diário recente:")
        for record in journals[:3]:
            fields = record["fields"]
            who = f"{fields.get('agente', '?')}-{fields.get('maquina', '?')}"
            lines.append(
                f"  {fields.get('data', '?')} — {who}: {record['title']} "
                f"[{fields.get('itens', '') or '-'}]"
            )

    ideas = [
        record
        for record in _front_matter_records(root / COORD / "ideias")
        if record["fields"].get("status") == "nova"
    ]
    if ideas:
        lines.append(f"Ideias novas ({len(ideas)}): " + "; ".join(r["title"] for r in ideas[:5]))

    rows = parse_quadro(root / COORD / "QUADRO.md")
    underway = [row for row in rows if row.get("Status") == "em andamento"]
    waiting = [
        row
        for row in rows
        if row.get("Decisão do Raul", "").lower() == "sim" and row.get("Status") != "pronto"
    ]
    if underway:
        lines.append(
            "Em andamento: "
            + "; ".join(f"{r['ID']} {r['Item']} ({r.get('Dono') or 'sem dono'})" for r in underway)
        )
    if waiting:
        lines.append("Aguardam o Raul: " + "; ".join(f"{r['ID']} {r['Item']}" for r in waiting))

    lines.extend(_data_lines(root, now))
    lines.append("CI: indisponível" if _network_disabled(sem_rede) else _ci_status(root))
    if len(lines) > 40:
        lines = lines[:39] + ["[EQUIPE] relatório truncado em 40 linhas."]
    return lines


def _prompt_text(root: Path, now: datetime) -> str:
    rows = parse_quadro(root / COORD / "QUADRO.md")
    underway = [f"{row['ID']} {row['Item']}" for row in rows if row.get("Status") == "em andamento"]
    waiting = [
        f"{row['ID']} {row['Item']}"
        for row in rows
        if row.get("Decisão do Raul", "").lower() == "sim" and row.get("Status") != "pronto"
    ]
    next_open = next(
        (f"{row['ID']} {row['Item']}" for row in rows if row.get("Status") == "aberto"),
        "nenhum",
    )
    active = [record for record in _reservation_records(root, now) if not record["vencida"]]
    reservations = [f"{r['item']} por {r['agente']}-{r['maquina']}" for r in active]
    return (
        f"Retome o repositório Lastro em {root.name}, em {now:%Y-%m-%d %H:%M}, "
        f"commit {_head(root)}. "
        "Leia nesta ordem AGENTS.md, CONTEXT.md, docs/coordenacao/QUADRO.md e "
        "docs/coordenacao/PROTOCOLO.md. "
        f"Itens em andamento: {', '.join(underway) or 'nenhum'}. "
        f"Reservas ativas: {', '.join(reservations) or 'nenhuma'}. "
        f"Aguardam o Raul: {', '.join(waiting) or 'nenhum'}. "
        f"Próximo item aberto: {next_open}. "
        "Regras: reserve antes de editar; mantenha ruff e a suíte completa verdes antes de "
        "empurrar; feche a sessão com equipe fechar."
    )


def command_iniciar(args: argparse.Namespace, root: Path) -> int:
    try:
        now = current_time()
        if args.prompt:
            print(_prompt_text(root, now))
        else:
            print("\n".join(_iniciar_lines(root, now, sem_rede=args.sem_rede, hook=args.hook)))
        return 0
    except Exception as exc:  # o hook nunca pode impedir uma sessão
        if args.hook:
            return 0
        if isinstance(exc, EquipeError):
            raise
        raise EquipeError(f"não foi possível montar o relatório: {exc}") from exc


def _identity(args: argparse.Namespace) -> tuple[str, str]:
    agent = (getattr(args, "agente", None) or os.environ.get("EQUIPE_AGENTE", "")).strip()
    machine = (getattr(args, "maquina", None) or os.environ.get("EQUIPE_MAQUINA", "")).strip()
    if not agent or not machine:
        raise EquipeError(
            "agente e máquina são obrigatórios; use --agente/--maquina ou "
            "EQUIPE_AGENTE/EQUIPE_MAQUINA"
        )
    return agent, machine


def _commit_paths(root: Path, paths: Sequence[Path], message: str) -> None:
    relative = list(dict.fromkeys(_relative(path, root) for path in paths))
    if not relative:
        raise EquipeError("nenhum arquivo para commitar")
    existing = [_relative(path, root) for path in paths if path.exists()]
    if existing:
        _git(root, "add", "-A", "--", *existing, check=True)
    result = _git(root, "commit", "--only", "-m", message, "--", *relative)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise EquipeError(f"não foi possível criar o commit: {detail}")


def _unmerged_paths(root: Path) -> list[str]:
    result = _git(root, "diff", "--name-only", "--diff-filter=U")
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def _pull_rebase(root: Path) -> subprocess.CompletedProcess[str]:
    return _git(root, "pull", "--rebase", "--autostash", "origin", "main")


def _rollback_commit(
    root: Path,
    previous_head: str,
    originals: dict[Path, bytes | None],
) -> None:
    _git(root, "rebase", "--abort")
    _git(root, "reset", "--soft", previous_head)
    relative = [_relative(path, root) for path in originals]
    _git(root, "restore", "--staged", "--source=HEAD", "--", *relative)
    for path, content in originals.items():
        if content is None:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)


QuadroEdit = tuple[str, dict[str, str], set[str]]


def _resolve_known_conflicts(root: Path, quadro_edits: Sequence[QuadroEdit]) -> bool:
    """Resolve sozinho os conflitos de rebase que são só INDICE.md e QUADRO.md.

    QUADRO.md: aceita a versão do remoto e reaplica somente as linhas que ESTA sessão
    alterou (itens vizinhos na tabela colidem no git mesmo sendo linhas diferentes).
    Se o remoto mostra o item com outro dono, é colisão real e a resolução desiste.
    INDICE.md: é gerado, então basta regenerar.
    """
    index_relative = (COORD / "INDICE.md").as_posix()
    quadro_relative = (COORD / "QUADRO.md").as_posix()
    for _ in range(6):
        conflicts = _unmerged_paths(root)
        if not conflicts or not set(conflicts) <= {index_relative, quadro_relative}:
            return False
        if quadro_relative in conflicts:
            if not quadro_edits:
                return False
            quadro = root / quadro_relative
            _git(root, "checkout", "--ours", "--", quadro_relative, check=True)
            remote_rows = {row["ID"]: row for row in parse_quadro(quadro)}
            for item, updates, allowed_owners in quadro_edits:
                owner = remote_rows.get(item, {}).get("Dono", "")
                if owner not in allowed_owners:
                    return False
                update_quadro_item(quadro, item, updates)
            _git(root, "add", "--", quadro_relative, check=True)
        if index_relative in conflicts or quadro_relative in conflicts:
            generate_index(root, current_time())
            _git(root, "add", "--", index_relative, check=True)
        committed = _git(root, "commit", "--no-verify", "-C", "REBASE_HEAD")
        if committed.returncode:
            return False
        continued = _git(root, "rebase", "--continue")
        if continued.returncode == 0:
            return True
    return False


def _exigir_main(root: Path) -> None:
    """Os comandos que publicam empurram para main; recusam outra branch.

    Refatoração grande em branch é integrada por fast-forward, à mão, não por aqui.
    """
    if not _has_remote(root) or os.environ.get("EQUIPE_PERMITIR_BRANCH") == "1":
        return
    atual = _branch(root)
    if atual != "main":
        raise EquipeError(
            f"a branch atual é '{atual}', não 'main'. Este comando publica em main; "
            "integre a branch por fast-forward (git merge --ff-only) antes, ou use "
            "--sem-push para registrar só localmente.",
            1,
        )


def _sync_push(
    root: Path,
    *,
    collision_path: str | None = None,
    previous_head: str | None = None,
    originals: dict[Path, bytes | None] | None = None,
    resolve_index: bool = False,
    quadro_edits: Sequence[QuadroEdit] = (),
) -> None:
    if not _has_remote(root):
        return
    for attempt in range(2):
        pulled = _pull_rebase(root)
        if pulled.returncode:
            conflicts = _unmerged_paths(root)
            if (
                collision_path
                and collision_path in conflicts
                and previous_head
                and originals is not None
            ):
                _rollback_commit(root, previous_head, originals)
                raise EquipeError("colisão: outra IA reservou este item", 3)
            if (resolve_index or quadro_edits) and _resolve_known_conflicts(root, quadro_edits):
                pass
            else:
                _git(root, "rebase", "--abort")
                detail = ", ".join(conflicts) or "estado de rebase desconhecido"
                raise EquipeError(
                    f"conflito de git ao sincronizar ({detail}); rebase abortado", 3
                )
        pushed = _push_origin(root)
        if pushed.returncode == 0:
            return
        if attempt == 1:
            detail = (pushed.stderr or pushed.stdout).strip()
            raise EquipeError(f"git push falhou após nova tentativa: {detail}", 3)


def _initial_pull(root: Path) -> None:
    if not _has_remote(root):
        return
    pulled = _pull_rebase(root)
    if pulled.returncode:
        if _unmerged_paths(root):
            _git(root, "rebase", "--abort")
            raise EquipeError("conflito de git antes da reserva", 3)
        detail = (pulled.stderr or pulled.stdout).strip()
        raise EquipeError(f"git pull falhou: {detail}", 3)


def command_reservar(args: argparse.Namespace, root: Path) -> int:
    agent, machine = _identity(args)
    now = current_time()
    if args.horas <= 0:
        raise EquipeError("--horas deve ser maior que zero")
    _initial_pull(root)
    reservation = root / COORD / "reservas" / f"{args.item}.md"
    quadro = root / COORD / "QUADRO.md"
    existing, _ = parse_front_matter(reservation) if reservation.exists() else ({}, "")
    expires = parse_iso(existing.get("expira", ""))
    if reservation.exists() and (expires is None or expires >= now):
        owner = f"{existing.get('agente', '?')}-{existing.get('maquina', '?')}"
        since = existing.get("desde", "data desconhecida")
        raise EquipeError(f"item {args.item} já reservado por {owner} desde {since}", 2)
    if reservation.exists():
        print(f"Reserva vencida do item {args.item} será substituída.")

    previous_head = _git(root, "rev-parse", "HEAD", check=True).stdout.strip()
    originals = {
        reservation: reservation.read_bytes() if reservation.exists() else None,
        quadro: quadro.read_bytes() if quadro.exists() else None,
    }
    expiry = now + timedelta(hours=args.horas)
    files = ", ".join(_split_csv(args.arquivos))
    content = (
        "---\n"
        f"item: {args.item}\n"
        f"agente: {agent}\n"
        f"maquina: {machine}\n"
        f"desde: {now:%Y-%m-%dT%H:%M}\n"
        f"expira: {expiry:%Y-%m-%dT%H:%M}\n"
        f"arquivos: {files}\n"
        "---\n"
        f"Reserva do item {args.item}.\n"
    )
    _atomic_write(reservation, content)
    updated = update_quadro_item(
        quadro,
        args.item,
        {"Status": "em andamento", "Dono": f"{agent}-{machine}", "Atualizado": f"{now:%Y-%m-%d}"},
    )
    if not updated:
        print(
            f"Aviso: item {args.item} não existe no QUADRO.md; "
            "reserva criada sem alterar o quadro."
        )
    paths = [reservation] + ([quadro] if updated else [])
    _commit_paths(root, paths, f"Equipe: reserva do item {args.item} ({agent}/{machine})")
    if not args.sem_push:
        _sync_push(
            root,
            collision_path=_relative(reservation, root),
            previous_head=previous_head,
            originals=originals,
            quadro_edits=(
                [
                    (
                        args.item,
                        {
                            "Status": "em andamento",
                            "Dono": f"{agent}-{machine}",
                            "Atualizado": f"{now:%Y-%m-%d}",
                        },
                        {"", f"{agent}-{machine}"},
                    )
                ]
                if updated
                else []
            ),
        )
    print(f"Item {args.item} reservado por {agent}-{machine} até {expiry:%Y-%m-%dT%H:%M}.")
    return 0


def _is_code_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return not (
        normalized.startswith("docs/coordenacao/")
        or normalized == "docs/coordenacao"
        or _ignored_status_path(normalized)
    )


def _run_gate(root: Path) -> tuple[bool, str, str]:
    ruff = _run(("ruff", "check", "."), cwd=root, timeout=300)
    tests = _run(
        (
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-q",
            "-p",
            "no:cacheprovider",
            "--cov=.",
        ),
        cwd=root,
        timeout=1800,
    )
    output = "\n".join((tests.stdout, tests.stderr))
    passed_match = re.search(r"(\d+) passed", output)
    coverage_match = re.search(r"Total coverage:\s*([0-9.]+)%", output, re.IGNORECASE)
    if not coverage_match:
        coverage_match = re.search(r"^TOTAL\s+\d+\s+\d+\s+([0-9.]+)%", output, re.MULTILINE)
    suite = f"{passed_match.group(1)} passed" if passed_match else "falhou"
    coverage = coverage_match.group(1) if coverage_match else "não disponível"
    return ruff.returncode == 0 and tests.returncode == 0, suite, coverage


def _last_journal(root: Path) -> dict[str, Any] | None:
    records = _front_matter_records(root / COORD / "diario")
    if not records:
        return None
    return max(records, key=lambda record: record["fields"].get("data", ""))


def _automatic_facts(root: Path) -> list[str]:
    last = _last_journal(root)
    if not last:
        return []
    commit = last["fields"].get("commit", "")
    if not commit or _git(root, "cat-file", "-e", f"{commit}^{{commit}}").returncode:
        return []
    result = _git(root, "diff", "--name-only", f"{commit}..HEAD")
    return [
        path
        for path in result.stdout.splitlines()
        if path.strip() and not path.replace("\\", "/").startswith("dados/")
    ]


def _short_title(summary: str) -> str:
    first = re.split(r"(?<=[.!?])\s+", summary.strip(), maxsplit=1)[0].strip()
    return (first or "Sessão de trabalho")[:80].rstrip()


def _selected_reservations(
    root: Path,
    now: datetime,
    agent: str,
    machine: str,
    items: list[str],
) -> list[dict[str, Any]]:
    records = _reservation_records(root, now)
    if items:
        selected = [record for record in records if record["item"] in items]
        missing = sorted(set(items) - {record["item"] for record in selected})
        if missing:
            print("Aviso: reservas não encontradas: " + ", ".join(missing))
        return selected
    return [
        record
        for record in records
        if record["agente"] == agent and record["maquina"] == machine
    ]


def command_fechar(args: argparse.Namespace, root: Path) -> int:
    agent, machine = _identity(args)
    dirty_code = [path for path in _dirty_paths(root) if _is_code_path(path)]
    if dirty_code and not args.forcar:
        raise EquipeError(
            "há mudanças de código não commitadas; commite antes de fechar: "
            + ", ".join(dirty_code[:8])
        )
    if args.sem_gate:
        suite, coverage = "nao rodada", "nao disponivel"
    else:
        passed, suite, coverage = _run_gate(root)
        if not passed:
            raise EquipeError(f"gate falhou ({suite}; cobertura {coverage})", 4)

    now = current_time()
    items = _split_csv(args.itens)
    ready = set(_split_csv(args.pronto))
    selected = _selected_reservations(root, now, agent, machine, items)
    journal = root / COORD / "diario" / f"{now:%Y-%m-%d_%H%M}_{machine}-{agent}.md"
    if journal.exists():
        raise EquipeError(f"já existe diário para esta sessão: {journal.name}")
    journal_items = items or [str(record["item"]) for record in selected]
    facts = _automatic_facts(root)
    facts_text = "\n".join(f"- `{path}`" for path in facts) or (
        "- Nenhum arquivo commitado desde o último diário."
    )
    content = (
        "---\n"
        f"data: {now:%Y-%m-%dT%H:%M}\n"
        f"maquina: {machine}\n"
        f"agente: {agent}\n"
        f"itens: {', '.join(journal_items)}\n"
        f"commit: {_head(root)}\n"
        f"suite: {suite}\n"
        f"cobertura: {coverage}\n"
        "---\n"
        f"# {_short_title(args.resumo)}\n"
        "## O que fiz\n"
        f"{args.resumo.strip()}\n"
        "## Decisões\n"
        f"{(args.decisao or 'Nenhuma').strip()}\n"
        "## O que falta\n"
        f"{args.proximo.strip()}\n"
        "## Perguntas ao Raul\n"
        "Nenhuma\n"
        "## Fatos automáticos\n"
        f"{facts_text}\n"
    )
    _atomic_write(journal, content)

    quadro = root / COORD / "QUADRO.md"
    quadro_changed = False
    removed: list[Path] = []
    quadro_edits: list[QuadroEdit] = []
    for record in selected:
        item = str(record["item"])
        status = "pronto" if item in ready else "aberto"
        updates = {"Status": status, "Dono": "", "Atualizado": f"{now:%Y-%m-%d}"}
        changed_row = update_quadro_item(quadro, item, updates)
        quadro_changed = changed_row or quadro_changed
        if changed_row:
            quadro_edits.append((item, updates, {"", f"{agent}-{machine}"}))
        path = record["path"]
        if path.exists():
            removed.append(path)
            _git(root, "rm", "--", _relative(path, root), check=True)

    index = generate_index(root, now)
    paths = [journal, index] + ([quadro] if quadro_changed else []) + removed
    _commit_paths(root, paths, f"Equipe: diário da sessão {agent}-{machine}")
    if not args.sem_push:
        _sync_push(root, resolve_index=True, quadro_edits=quadro_edits)
    print(f"Sessão fechada: {journal.name} ({suite}; cobertura {coverage}).")
    return 0


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")[:60].rstrip("-")
    return slug or "registro"


def _unique_dated_path(folder: Path, date: str, title: str) -> Path:
    stem = f"{date}_{slugify(title)}"
    candidate = folder / f"{stem}.md"
    suffix = 2
    while candidate.exists():
        candidate = folder / f"{stem}-{suffix}.md"
        suffix += 1
    return candidate


def _publish_commit(root: Path, paths: Sequence[Path], message: str, sem_push: bool) -> None:
    _commit_paths(root, paths, message)
    if not sem_push:
        _sync_push(root)


def command_ideia(args: argparse.Namespace, root: Path) -> int:
    now = current_time()
    path = _unique_dated_path(root / COORD / "ideias", f"{now:%Y-%m-%d}", args.titulo)
    origin = args.origem or os.environ.get("EQUIPE_AGENTE") or "nao informada"
    body = (args.corpo or "A detalhar.").strip()
    content = (
        "---\n"
        f"data: {now:%Y-%m-%d}\n"
        f"origem: {origin}\n"
        "status: nova\n"
        "---\n"
        f"# {args.titulo.strip()}\n"
        "## Problema\n"
        f"{body}\n"
        "## Proposta\n"
        "A detalhar.\n"
        "## Custo e risco\n"
        "A avaliar.\n"
    )
    _atomic_write(path, content)
    _publish_commit(root, [path], f"Equipe: ideia {args.titulo.strip()}", args.sem_push)
    print(f"Ideia registrada em {_relative(path, root)}.")
    return 0


def _decision_path(root: Path, value: str) -> Path:
    requested = Path(value)
    if requested.is_absolute():
        candidate = requested.resolve()
    else:
        candidate = (root / COORD / "decisoes" / requested.name).resolve()
    decisions = (root / COORD / "decisoes").resolve()
    if candidate.parent != decisions or not candidate.exists():
        raise EquipeError(f"decisão substituída não encontrada: {value}")
    return candidate


def command_decisao(args: argparse.Namespace, root: Path) -> int:
    now = current_time()
    path = _unique_dated_path(root / COORD / "decisoes", f"{now:%Y-%m-%d}", args.titulo)
    who = args.quem or os.environ.get("EQUIPE_AGENTE") or "nao informado"
    paths = [path]
    if args.substitui:
        old = _decision_path(root, args.substitui)
        _replace_front_matter_field(old, "status", "substituida")
        paths.append(old)
    content = (
        "---\n"
        f"data: {now:%Y-%m-%d}\n"
        f"quem: {who}\n"
        "status: vigente\n"
        "---\n"
        f"# {args.titulo.strip()}\n"
        "## Decisão\n"
        f"{args.decisao.strip()}\n"
        "## Por quê\n"
        f"{args.porque.strip()}\n"
        "## Alternativas rejeitadas\n"
        f"{(args.alternativas or 'Nenhuma registrada.').strip()}\n"
    )
    _atomic_write(path, content)
    _publish_commit(root, paths, f"Equipe: decisão {args.titulo.strip()}", args.sem_push)
    print(f"Decisão registrada em {_relative(path, root)}.")
    return 0


def _checkpoint_number(root: Path) -> int:
    numbers: list[int] = []
    for path in _markdown_files(root / COORD / "checkpoints"):
        match = re.fullmatch(r"ckpt-(\d+)", path.stem)
        if match:
            numbers.append(int(match.group(1)))
    tags = _git(root, "tag", "--list", "ckpt-*")
    for tag in tags.stdout.splitlines():
        match = re.fullmatch(r"ckpt-(\d+)", tag.strip())
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def _data_metadata() -> tuple[str, str]:
    derived = Path(
        os.environ.get("LASTRO_DADOS_DIR", str(Path.home() / ".cache" / "lastro" / "derived"))
    ).expanduser()
    metadata = _read_json(derived / "acoes_meta.json")
    return (
        str(metadata.get("data_cotacao", "nao disponivel")),
        str(metadata.get("gerado_em", "nao disponivel")),
    )


def command_checkpoint(args: argparse.Namespace, root: Path) -> int:
    if args.sem_gate:
        suite, coverage = "nao rodada", "nao disponivel"
    else:
        passed, suite, coverage = _run_gate(root)
        if not passed:
            raise EquipeError(f"gate falhou ({suite}; cobertura {coverage})", 4)
    now = current_time()
    number = _checkpoint_number(root)
    name = f"ckpt-{number:03d}"
    path = root / COORD / "checkpoints" / f"{name}.md"
    quote_date, generated = _data_metadata()
    rows = parse_quadro(root / COORD / "QUADRO.md")
    counts = {status: sum(row.get("Status") == status for row in rows) for status in VALID_STATUSES}
    ready = [f"{row['ID']} {row['Item']}" for row in rows if row.get("Status") == "pronto"]
    content = (
        "---\n"
        f"data: {now:%Y-%m-%dT%H:%M}\n"
        f"commit: {_head(root)}\n"
        f"suite: {suite}\n"
        f"cobertura: {coverage}\n"
        f"ciclo: {args.ciclo or 'nao informado'}\n"
        f"dados_cotacao: {quote_date}\n"
        f"dados_gerado_em: {generated}\n"
        "---\n"
        f"# Checkpoint {name}\n"
        "## Estado dos itens\n"
        + "\n".join(f"- {status}: {counts[status]}" for status in sorted(VALID_STATUSES))
        + "\n## Itens prontos\n"
        + ("\n".join(f"- {item}" for item in ready) if ready else "- Nenhum")
        + "\n"
    )
    _atomic_write(path, content)
    _commit_paths(root, [path], f"Equipe: checkpoint {name}")
    if args.tag:
        tagged = _git(root, "tag", "-a", name, "-m", f"Checkpoint {name}")
        if tagged.returncode:
            raise EquipeError(f"não foi possível criar a tag {name}")
    if not args.sem_push:
        _sync_push(root)
        if args.tag:
            pushed = _push_tag(root, name)
            if pushed.returncode:
                raise EquipeError(f"não foi possível empurrar a tag {name}", 3)
    print(f"Checkpoint {name} criado.")
    return 0


def generate_index(root: Path, now: datetime | None = None) -> Path:
    now = now or current_time()
    reservations = _reservation_records(root, now)
    journals = _front_matter_records(root / COORD / "diario")
    journals.sort(key=lambda record: record["fields"].get("data", ""), reverse=True)
    ideas = [
        record
        for record in _front_matter_records(root / COORD / "ideias")
        if record["fields"].get("status") in {"nova", "aceita"}
    ]
    decisions = [
        record
        for record in _front_matter_records(root / COORD / "decisoes")
        if record["fields"].get("status") == "vigente"
    ]
    waiting = [
        row
        for row in parse_quadro(root / COORD / "QUADRO.md")
        if row.get("Decisão do Raul", "").lower() == "sim" and row.get("Status") != "pronto"
    ]
    checkpoints = _front_matter_records(root / COORD / "checkpoints")
    checkpoints.sort(key=lambda record: record["path"].name, reverse=True)

    lines = [
        f"Gerado por `scripts/equipe.py indice` em {now:%Y-%m-%d}. Não edite.",
        "",
        "# Índice da coordenação",
        "",
        "## Reservas ativas",
    ]
    active = [record for record in reservations if not record["vencida"]]
    lines.extend(
        f"- Item {r['item']}: {r['agente']}-{r['maquina']} desde "
        f"{r['desde'].strftime('%Y-%m-%dT%H:%M') if r['desde'] else '?'}"
        for r in active
    )
    if not active:
        lines.append("- Nenhuma.")
    lines.extend(["", "## Reservas vencidas"])
    expired = [record for record in reservations if record["vencida"]]
    lines.extend(f"- Item {r['item']}: {r['agente']}-{r['maquina']}" for r in expired)
    if not expired:
        lines.append("- Nenhuma.")

    lines.extend(["", "## Últimas sessões"])
    for record in journals[:10]:
        fields = record["fields"]
        link = record["path"].relative_to(root / COORD).as_posix()
        lines.append(
            f"- [{record['title']}]({link}) — {fields.get('data', '?')}; "
            f"{fields.get('agente', '?')}-{fields.get('maquina', '?')}; "
            f"itens {fields.get('itens', '-') or '-'}"
        )
    if not journals:
        lines.append("- Nenhuma.")

    lines.extend(["", "## Ideias novas ou aceitas"])
    for record in ideas:
        fields = record["fields"]
        link = record["path"].relative_to(root / COORD).as_posix()
        lines.append(
            f"- [{record['title']}]({link}) — {fields.get('status')}"
        )
    if not ideas:
        lines.append("- Nenhuma.")

    lines.extend(["", "## Decisões vigentes"])
    for record in decisions:
        link = record["path"].relative_to(root / COORD).as_posix()
        lines.append(f"- [{record['title']}]({link})")
    if not decisions:
        lines.append("- Nenhuma.")

    lines.extend(["", "## Aguardam o Raul"])
    lines.extend(f"- {row['ID']} — {row['Item']}" for row in waiting)
    if not waiting:
        lines.append("- Nenhum item.")

    lines.extend(["", "## Último checkpoint"])
    if checkpoints:
        latest = checkpoints[0]
        link = latest["path"].relative_to(root / COORD).as_posix()
        lines.append(f"- [{latest['title']}]({link})")
    else:
        lines.append("- Nenhum.")
    path = root / COORD / "INDICE.md"
    _atomic_write(path, "\n".join(lines) + "\n")
    return path


def command_indice(args: argparse.Namespace, root: Path) -> int:
    path = generate_index(root, current_time())
    print(f"Índice regenerado em {_relative(path, root)}.")
    return 0


def scan_secrets(paths: Iterable[Path]) -> list[tuple[Path, str]]:
    findings: list[tuple[Path, str]] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for pattern in SECRET_PATTERNS:
            if match := pattern.search(text):
                findings.append((path, match.group(0)))
        for email in EMAIL_PATTERN.findall(text):
            if not any(pattern.fullmatch(email) for pattern in ALLOWED_EMAILS):
                findings.append((path, email))
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Coordenação das IAs do Lastro")
    subparsers = parser.add_subparsers(dest="command", required=True)

    iniciar = subparsers.add_parser("iniciar", help="mostra o estado para retomada")
    iniciar.add_argument("--prompt", action="store_true")
    iniciar.add_argument("--hook", action="store_true")
    iniciar.add_argument("--sem-rede", action="store_true")
    iniciar.set_defaults(handler=command_iniciar)

    reservar = subparsers.add_parser("reservar", help="reserva um item do quadro")
    reservar.add_argument("item")
    reservar.add_argument("--agente")
    reservar.add_argument("--maquina")
    reservar.add_argument("--arquivos", default="")
    reservar.add_argument("--horas", type=int, default=24)
    reservar.add_argument("--sem-push", action="store_true")
    reservar.set_defaults(handler=command_reservar)

    fechar = subparsers.add_parser("fechar", help="registra e encerra uma sessão")
    fechar.add_argument("--resumo", required=True)
    fechar.add_argument("--proximo", required=True)
    fechar.add_argument("--decisao")
    fechar.add_argument("--itens", default="")
    fechar.add_argument("--pronto", default="")
    fechar.add_argument("--sem-gate", action="store_true")
    fechar.add_argument("--sem-push", action="store_true")
    fechar.add_argument("--forcar", action="store_true")
    fechar.add_argument("--agente")
    fechar.add_argument("--maquina")
    fechar.set_defaults(handler=command_fechar)

    ideia = subparsers.add_parser("ideia", help="registra uma ideia")
    ideia.add_argument("titulo")
    ideia.add_argument("--origem")
    ideia.add_argument("--corpo")
    ideia.add_argument("--sem-push", action="store_true")
    ideia.set_defaults(handler=command_ideia)

    decisao = subparsers.add_parser("decisao", help="registra uma decisão")
    decisao.add_argument("titulo")
    decisao.add_argument("--decisao", required=True)
    decisao.add_argument("--porque", required=True)
    decisao.add_argument("--alternativas")
    decisao.add_argument("--quem")
    decisao.add_argument("--substitui")
    decisao.add_argument("--sem-push", action="store_true")
    decisao.set_defaults(handler=command_decisao)

    checkpoint = subparsers.add_parser("checkpoint", help="cria um marco de ciclo")
    checkpoint.add_argument("--tag", action="store_true")
    checkpoint.add_argument("--ciclo")
    checkpoint.add_argument("--sem-gate", action="store_true")
    checkpoint.add_argument("--sem-push", action="store_true")
    checkpoint.set_defaults(handler=command_checkpoint)

    indice = subparsers.add_parser("indice", help="regenera o índice da coordenação")
    indice.set_defaults(handler=command_indice)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_output()
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        root = repository_root()
        publica = args.command in ("reservar", "fechar", "ideia", "decisao", "checkpoint")
        if publica and not getattr(args, "sem_push", False):
            _exigir_main(root)
        return int(args.handler(args, root))
    except EquipeError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return exc.code
    except KeyboardInterrupt:
        print("Erro: operação interrompida.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
