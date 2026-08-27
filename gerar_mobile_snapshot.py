"""Gera o snapshot público consumido pelo FocusLens Mobile, sem acessar rede."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from mobile_snapshot import DEFAULT_SNAPSHOT_PATH, gerar_snapshot_mobile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SNAPSHOT_PATH,
        help="Destino do JSON versionado.",
    )
    parser.add_argument(
        "--reference-date",
        type=date.fromisoformat,
        default=None,
        help="Data ISO usada pelos diagnósticos de defasagem (padrão: hoje).",
    )
    argumentos = parser.parse_args()
    snapshot = gerar_snapshot_mobile(
        argumentos.output,
        hoje=argumentos.reference_date,
    )
    print(
        f"Snapshot mobile v{snapshot['schemaVersion']} salvo em "
        f"{argumentos.output} ({len(snapshot['signals'])} sinais)."
    )


if __name__ == "__main__":
    main()
