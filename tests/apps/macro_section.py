"""Entrypoint mínimo usado pelo AppTest da seção Radar Macro."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from focuslens.ui.pagina_macro import render_secao


render_secao()
