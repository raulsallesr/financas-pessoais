"""Caminhos estáveis do repositório, independentes do diretório de execução."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "dados"
MOBILE_DIR = PROJECT_ROOT / "mobile"
