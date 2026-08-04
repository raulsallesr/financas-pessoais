"""Estilo visual centralizado do app Streamlit."""

from __future__ import annotations

import streamlit as st


def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
        html {
            scroll-behavior: smooth;
        }

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

        .fp-section-anchor {
            display: block;
            position: relative;
            top: -1.5rem;
            visibility: hidden;
            scroll-margin-top: 1.5rem;
        }

        .fp-section-nav {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-top: 0.75rem;
        }

        .fp-section-nav a {
            align-items: center;
            border: 1px solid transparent;
            border-radius: 12px;
            color: var(--fp-ink);
            display: flex;
            gap: 0.7rem;
            min-height: 44px;
            padding: 0.65rem 0.75rem;
            text-decoration: none;
            transition: border-color 180ms ease, background-color 180ms ease;
        }

        .fp-section-nav a:hover {
            background: var(--fp-surface);
            border-color: var(--fp-border);
            color: var(--fp-primary);
        }

        .fp-section-nav a:active {
            background: color-mix(
                in srgb,
                var(--fp-primary) 12%,
                var(--fp-surface)
            );
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
            background: var(--fp-surface);
            border-color: var(--fp-primary);
            color: var(--fp-primary);
            font-weight: 600;
        }

        .fp-section-nav a:focus-visible {
            outline: 3px solid var(--fp-primary);
            outline-offset: 2px;
        }

        .fp-section-nav .material-symbols-rounded {
            color: var(--fp-primary);
            font-size: 1.25rem;
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
        .st-key-home_overview
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
            outline: 3px solid var(--fp-primary);
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
