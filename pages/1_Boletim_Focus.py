"""Entrypoint Streamlit da página do Boletim Focus."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pagina_focus import render

render()
