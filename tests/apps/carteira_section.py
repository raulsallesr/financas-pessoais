"""Entrypoint mínimo usado pelo AppTest da seção Carteira."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from focuslens.ui.pagina_carteira import render


render(None, [])
