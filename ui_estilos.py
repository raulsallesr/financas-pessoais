"""Estilo visual centralizado do app Streamlit."""

from __future__ import annotations

import streamlit as st


def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
        :root {
            --fp-bg: #f3f6fb;
            --fp-surface: #fbfcfe;
            --fp-ink: #14213d;
            --fp-muted: #52627a;
            --fp-primary: #1e40af;
            --fp-border: #dce4f0;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --fp-bg: #0f172a;
                --fp-surface: #172036;
                --fp-ink: #f8fafc;
                --fp-muted: #b5c0d0;
                --fp-primary: #60a5fa;
                --fp-border: #334155;
            }
        }

        [data-testid="stAppViewContainer"] {
            background: var(--fp-bg);
            color: var(--fp-ink);
        }

        [data-testid="stHeader"] {
            background: color-mix(in srgb, var(--fp-bg) 92%, transparent);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            color: var(--fp-ink);
            letter-spacing: -0.025em;
        }

        p, [data-testid="stCaptionContainer"] {
            line-height: 1.55;
        }

        [data-testid="stMetricValue"] {
            font-variant-numeric: tabular-nums;
        }

        [data-testid="stMetric"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--fp-surface);
            border-color: var(--fp-border);
            border-radius: 16px;
        }

        .st-key-resumo_semana
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-left: 5px solid var(--fp-primary);
        }

        .st-key-home_feature_focus
        div[data-testid="stVerticalBlockBorderWrapper"],
        .st-key-home_feature_macro
        div[data-testid="stVerticalBlockBorderWrapper"],
        .st-key-macro_cenario
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-left: 5px solid var(--fp-primary);
        }

        .stButton button,
        .stLinkButton a,
        [data-testid="stPopover"] button {
            min-height: 44px;
            border-radius: 12px;
            transition: border-color 180ms ease, background-color 180ms ease;
        }

        .stButton button:focus-visible,
        .stLinkButton a:focus-visible,
        [data-testid="stPopover"] button:focus-visible {
            outline: 3px solid rgba(30, 64, 175, 0.28);
            outline-offset: 2px;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 1.25rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                scroll-behavior: auto !important;
                transition-duration: 0.01ms !important;
                animation-duration: 0.01ms !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
