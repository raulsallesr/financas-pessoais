"""Estilo visual centralizado do app Streamlit."""

from __future__ import annotations

import streamlit as st


COR_GRAFICO_PRIMARIA = "#0F766E"

CSS_APP = """
<style>
:root {
    color-scheme: light;
    --fp-bg: #f3f7f5;
    --fp-bg-deep: #e9f1ee;
    --fp-surface: #ffffff;
    --fp-surface-soft: #f8faf9;
    --fp-ink: #17332f;
    --fp-muted: #536965;
    --fp-primary: #0f766e;
    --fp-primary-strong: #0a5b55;
    --fp-primary-soft: #ddf2ed;
    --fp-accent: #a16207;
    --fp-accent-soft: #fff3d6;
    --fp-border: #d8e5e1;
    --fp-shadow: 0 18px 46px rgba(24, 72, 64, 0.09);
    --fp-shadow-soft: 0 7px 22px rgba(24, 72, 64, 0.07);
}

html {
    scroll-behavior: smooth;
}

html, body {
    max-width: 100%;
    overflow-x: hidden;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 88% -10%,
            rgba(189, 226, 216, 0.58) 0,
            rgba(189, 226, 216, 0) 34rem
        ),
        linear-gradient(180deg, #f7faf8 0%, var(--fp-bg) 100%);
    color: var(--fp-ink);
    max-width: 100vw;
    overflow-x: hidden;
}

[data-testid="stHeader"] {
    background: rgba(247, 250, 248, 0.88);
    border-bottom: 1px solid rgba(216, 229, 225, 0.75);
    backdrop-filter: blur(12px);
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #ffffff 0%, #f7faf8 72%, #eef5f2 100%);
    border-right: 1px solid var(--fp-border);
}

[data-testid="stSidebarContent"] {
    padding-top: 1.35rem;
}

.block-container {
    box-sizing: border-box;
    max-width: 1180px;
    padding-top: 2.4rem;
    padding-bottom: 5rem;
    width: 100%;
}

.fp-skip-link {
    background: var(--fp-primary);
    border-radius: 0 0 10px 10px;
    color: #ffffff !important;
    font-weight: 700;
    left: 1rem;
    padding: 0.75rem 1rem;
    position: fixed;
    text-decoration: none;
    top: -5rem;
    transition: top 180ms ease;
    z-index: 1000;
}

.fp-skip-link:focus {
    outline: 3px solid var(--fp-accent-soft);
    outline-offset: 2px;
    top: 0;
}

.fp-section-anchor {
    display: block;
    position: relative;
    scroll-margin-top: 4rem;
    top: -1.5rem;
    visibility: hidden;
}

.fp-sidebar-brand {
    align-items: center;
    display: flex;
    gap: 0.8rem;
    margin-bottom: 1.6rem;
}

.fp-sidebar-brand__mark {
    align-items: center;
    background: linear-gradient(
        145deg,
        var(--fp-primary) 0%,
        var(--fp-primary-strong) 100%
    );
    border-radius: 14px;
    box-shadow: 0 8px 20px rgba(15, 118, 110, 0.22);
    color: #ffffff;
    display: flex;
    height: 44px;
    justify-content: center;
    width: 44px;
}

.fp-sidebar-brand__mark svg {
    height: 23px;
    width: 23px;
}

.fp-sidebar-brand__text {
    display: flex;
    flex-direction: column;
}

.fp-sidebar-brand__text span {
    color: var(--fp-muted);
    font-size: 0.68rem;
    font-weight: 750;
    letter-spacing: 0.12em;
    line-height: 1.2;
}

.fp-sidebar-brand__text strong {
    color: var(--fp-ink);
    font-size: 1.08rem;
    letter-spacing: -0.02em;
}

.fp-section-nav {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    margin-top: 0.55rem;
}

.fp-section-nav a {
    align-items: center;
    border: 1px solid transparent;
    border-radius: 12px;
    color: var(--fp-muted) !important;
    display: flex;
    font-weight: 600;
    gap: 0.75rem;
    min-height: 46px;
    padding: 0.68rem 0.8rem;
    text-decoration: none;
    transition:
        border-color 180ms ease,
        background-color 180ms ease,
        color 180ms ease,
        box-shadow 180ms ease;
}

.fp-section-nav a svg {
    color: var(--fp-primary);
    flex: 0 0 auto;
    height: 20px;
    stroke-width: 1.8;
    width: 20px;
}

.fp-section-nav a:hover {
    background: var(--fp-surface);
    border-color: var(--fp-border);
    box-shadow: var(--fp-shadow-soft);
    color: var(--fp-primary-strong) !important;
}

.fp-section-nav a:active {
    background: var(--fp-primary-soft);
}

body:not(:has(.fp-section-anchor:target))
.fp-section-nav a[href="#visao-geral"],
body:has(#visao-geral:target)
.fp-section-nav a[href="#visao-geral"],
body:has(#boletim-focus:target)
.fp-section-nav a[href="#boletim-focus"],
body:has(#radar-macro:target)
.fp-section-nav a[href="#radar-macro"],
body:has(#minha-carteira:target)
.fp-section-nav a[href="#minha-carteira"] {
    background: linear-gradient(135deg, #e7f5f1 0%, #f6fbf9 100%);
    border-color: #b8dcd4;
    color: var(--fp-primary-strong) !important;
    font-weight: 750;
}

.fp-section-nav a:focus-visible {
    outline: 3px solid rgba(15, 118, 110, 0.36);
    outline-offset: 2px;
}

.st-key-home_hero {
    background:
        radial-gradient(
            circle at 92% 12%,
            rgba(255, 243, 214, 0.95) 0,
            rgba(255, 243, 214, 0) 17rem
        ),
        linear-gradient(135deg, #ffffff 0%, #f0f8f5 100%);
    border: 1px solid #cfe1dc;
    border-radius: 26px;
    box-shadow: var(--fp-shadow);
    box-sizing: border-box;
    margin-bottom: 1.5rem;
    overflow: hidden;
    padding: clamp(1.5rem, 4vw, 3rem);
    position: relative;
    width: 100%;
}

.st-key-home_hero::after {
    border: 1px solid rgba(15, 118, 110, 0.12);
    border-radius: 50%;
    content: "";
    height: 13rem;
    position: absolute;
    right: -5rem;
    top: -6rem;
    width: 13rem;
}

.st-key-home_hero > div {
    position: relative;
    z-index: 1;
}

.st-key-home_hero h1 {
    font-size: clamp(2.15rem, 5vw, 3.65rem);
    line-height: 1.04;
    max-width: 15ch;
}

.st-key-home_hero p {
    color: var(--fp-muted);
    font-size: 1.08rem;
    max-width: 66ch;
}

.fp-eyebrow {
    align-items: center;
    background: var(--fp-primary-soft);
    border: 1px solid #b9ddd5;
    border-radius: 999px;
    color: var(--fp-primary-strong);
    display: inline-flex;
    font-size: 0.73rem;
    font-weight: 800;
    gap: 0.45rem;
    letter-spacing: 0.08em;
    margin-bottom: 0.55rem;
    padding: 0.42rem 0.7rem;
    text-transform: uppercase;
}

.fp-eyebrow svg {
    height: 15px;
    width: 15px;
}

.fp-step-index {
    align-items: center;
    background: var(--fp-accent-soft);
    border: 1px solid #ecd79e;
    border-radius: 10px;
    color: var(--fp-accent);
    display: inline-flex;
    font-size: 0.72rem;
    font-weight: 850;
    height: 2rem;
    justify-content: center;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
    width: 2.2rem;
}

h1, h2, h3 {
    color: var(--fp-ink);
    letter-spacing: -0.032em;
}

p, [data-testid="stCaptionContainer"] {
    line-height: 1.62;
}

[data-testid="stCaptionContainer"] {
    color: var(--fp-muted);
}

[data-testid="stMetricValue"] {
    color: var(--fp-ink);
    font-variant-numeric: tabular-nums;
}

[data-testid="stMetric"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid var(--fp-border) !important;
    border-radius: 18px;
    box-shadow: var(--fp-shadow-soft);
}

[data-testid="stMetric"] {
    min-height: 126px;
    padding: 1.05rem 1.1rem;
}

.st-key-home_overview
div[data-testid="stVerticalBlockBorderWrapper"],
.st-key-resumo_semana
div[data-testid="stVerticalBlockBorderWrapper"],
.st-key-macro_cenario
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-top: 4px solid var(--fp-primary) !important;
}

.st-key-home_step_1
div[data-testid="stVerticalBlockBorderWrapper"],
.st-key-home_step_2
div[data-testid="stVerticalBlockBorderWrapper"],
.st-key-home_step_3
div[data-testid="stVerticalBlockBorderWrapper"] {
    min-height: 188px;
}

[data-testid="stBaseButton-primary"] {
    background: linear-gradient(
        135deg,
        var(--fp-primary) 0%,
        var(--fp-primary-strong) 100%
    ) !important;
    border-color: var(--fp-primary) !important;
    box-shadow: 0 7px 18px rgba(15, 118, 110, 0.2);
    color: #ffffff !important;
}

[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 10px 24px rgba(15, 118, 110, 0.26);
    filter: brightness(1.03);
}

[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-tertiary"] {
    color: var(--fp-primary-strong) !important;
}

.stButton button,
.stLinkButton a,
[data-testid="stPopover"] button {
    border-radius: 12px;
    min-height: 44px;
    transition:
        border-color 180ms ease,
        background-color 180ms ease,
        box-shadow 180ms ease,
        filter 180ms ease;
}

.stButton button:focus-visible,
.stLinkButton a:focus-visible,
[data-testid="stPopover"] button:focus-visible,
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    outline: 3px solid rgba(15, 118, 110, 0.34);
    outline-offset: 2px;
}

[data-testid="stFileUploaderDropzone"] {
    background: var(--fp-surface-soft);
    border-color: #bad6cf;
    border-radius: 16px;
}

hr {
    border-color: var(--fp-border) !important;
}

@media (max-width: 768px) {
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        max-width: 100vw !important;
        min-width: 0 !important;
        overflow-x: hidden;
        width: 100% !important;
    }

    .block-container {
        margin: 0 !important;
        max-width: 100vw !important;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1.25rem;
        width: 100vw !important;
    }

    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 1rem !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        min-width: 0 !important;
        width: 100% !important;
    }

    .st-key-home_hero {
        border-radius: 20px;
        max-width: calc(100vw - 2rem) !important;
        padding: 1.35rem;
        width: calc(100vw - 2rem) !important;
    }

    .st-key-home_hero > div,
    .st-key-home_hero h1,
    .st-key-home_hero p {
        max-width: 100% !important;
        min-width: 0 !important;
        overflow-wrap: break-word;
        width: 100% !important;
    }

    .st-key-home_overview,
    .st-key-home_step_1,
    .st-key-home_step_2,
    .st-key-home_step_3 {
        max-width: calc(100vw - 2rem) !important;
        min-width: 0 !important;
        width: calc(100vw - 2rem) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        box-sizing: border-box;
        max-width: 100% !important;
        min-width: 0 !important;
        width: 100% !important;
    }

    .st-key-home_hero h1 {
        font-size: clamp(1.9rem, 9vw, 2.5rem);
    }

    .st-key-home_hero p {
        font-size: 1rem;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""


def aplicar_estilos() -> None:
    st.markdown(
        CSS_APP,
        unsafe_allow_html=True,
    )
