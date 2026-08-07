from __future__ import annotations

from pathlib import Path
import tomllib

from ui_estilos import COR_GRAFICO_PRIMARIA, CSS_APP


RAIZ_PROJETO = Path(__file__).resolve().parent.parent


def _luminancia(cor_hex: str) -> float:
    canais = [
        int(cor_hex[indice : indice + 2], 16) / 255
        for indice in (1, 3, 5)
    ]
    lineares = [
        canal / 12.92
        if canal <= 0.04045
        else ((canal + 0.055) / 1.055) ** 2.4
        for canal in canais
    ]
    return (
        0.2126 * lineares[0]
        + 0.7152 * lineares[1]
        + 0.0722 * lineares[2]
    )


def _contraste(cor_a: str, cor_b: str) -> float:
    clara, escura = sorted(
        (_luminancia(cor_a), _luminancia(cor_b)),
        reverse=True,
    )
    return (clara + 0.05) / (escura + 0.05)


def test_tema_streamlit_fica_explicitamente_claro() -> None:
    caminho = RAIZ_PROJETO / ".streamlit" / "config.toml"
    tema = tomllib.loads(caminho.read_text(encoding="utf-8"))["theme"]

    assert tema["base"] == "light"
    assert tema["primaryColor"] == COR_GRAFICO_PRIMARIA
    assert tema["backgroundColor"] == "#F3F7F5"
    assert tema["textColor"] == "#17332F"
    assert tema["showWidgetBorder"] is True
    assert tema["showSidebarBorder"] is True


def test_css_claro_preserva_acessibilidade_e_responsividade() -> None:
    assert "color-scheme: light" in CSS_APP
    assert "prefers-color-scheme: dark" not in CSS_APP
    assert "prefers-reduced-motion: reduce" in CSS_APP
    assert ":focus-visible" in CSS_APP
    assert "@media (max-width: 768px)" in CSS_APP
    assert "min-height: 44px" in CSS_APP
    assert "flex-wrap: wrap !important" in CSS_APP
    assert "max-width: 100vw" in CSS_APP
    assert "max-width: 1100px" in CSS_APP
    assert "gap: 1rem" in CSS_APP
    assert "min-height: 108px" in CSS_APP
    assert ".st-key-home_hero" not in CSS_APP
    assert _contraste("#0F766E", "#FFFFFF") >= 4.5
    assert _contraste("#17332F", "#F3F7F5") >= 4.5
