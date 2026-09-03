import re
from pathlib import Path
from urllib.parse import unquote

from focuslens.paths import DATA_DIR, MOBILE_DIR, PROJECT_ROOT


def test_repository_paths_remain_stable_after_package_organization():
    assert PROJECT_ROOT == Path(__file__).resolve().parent.parent
    assert DATA_DIR == PROJECT_ROOT / "dados"
    assert MOBILE_DIR == PROJECT_ROOT / "mobile"


def test_root_keeps_only_the_public_python_entrypoint():
    loose_modules = {path.name for path in PROJECT_ROOT.glob("*.py")}

    assert loose_modules == {"app_financas.py"}


def test_local_markdown_links_resolve_after_document_organization():
    broken_links = []

    for document in PROJECT_ROOT.rglob("*.md"):
        if ".git" in document.parts or "node_modules" in document.parts:
            continue
        content = document.read_text(encoding="utf-8")
        for raw_target in re.findall(r"\]\(([^)]+)\)", content):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            resolved = document.parent / unquote(target)
            if not resolved.exists():
                broken_links.append(
                    f"{document.relative_to(PROJECT_ROOT)} -> {raw_target}"
                )

    assert broken_links == []
