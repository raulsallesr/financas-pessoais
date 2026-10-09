"""Painel compartilhado de premissas do valuation nas páginas do módulo Ativos."""

from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import asdict

import streamlit as st

from ativos.core.linguagem import validar_textos
from ativos.core.premissas import PremissasValuation, premissas_padrao

CHAVES_EDITAVEIS = {
    "rf": "valuation_rf",
    "erp": "valuation_erp",
    "g": "valuation_g",
    "bazin_taxa": "valuation_bazin_taxa",
    "graham_mult": "valuation_graham_mult",
    "min_pares_setor": "valuation_min_pares_setor",
}
CHAVES_REFERENCIA = {
    "fonte_rf": "valuation_fonte_rf",
    "data_curva": "valuation_data_curva",
    "rf_padrao": "valuation_rf_padrao",
}
CAMPOS_PERCENTUAIS = {"rf", "erp", "g", "bazin_taxa"}
TEXTOS_UI_PREMISSAS = validar_textos(
    [
        "Premissas",
        "Edite os parâmetros e veja o cálculo ser refeito nesta sessão.",
        "Taxa livre de risco (%)",
        "Prêmio de risco de ações (%)",
        "Crescimento perpétuo g (%)",
        "Taxa mínima de Bazin (%)",
        "Multiplicador de Graham",
        "Mínimo de pares do setor",
        "Custo do capital próprio (k)",
        "Taxa exigida dos FIIs",
        "Restaurar padrão",
    ]
)


def _valor_para_estado(campo: str, valor: object) -> object:
    return float(valor) * 100 if campo in CAMPOS_PERCENTUAIS else valor


def restaurar_premissas(
    padrao: PremissasValuation,
    estado: MutableMapping[str, object],
) -> None:
    """Restaura os valores editáveis e a referência da curva no estado informado."""
    valores = asdict(padrao)
    for campo, chave in {**CHAVES_EDITAVEIS, **CHAVES_REFERENCIA}.items():
        estado[chave] = _valor_para_estado(campo, valores[campo])


def _inicializar(padrao: PremissasValuation) -> None:
    valores = asdict(padrao)
    for campo, chave in {**CHAVES_EDITAVEIS, **CHAVES_REFERENCIA}.items():
        if chave not in st.session_state:
            st.session_state[chave] = _valor_para_estado(campo, valores[campo])


def _premissas_do_estado() -> PremissasValuation:
    return PremissasValuation(
        rf=float(st.session_state[CHAVES_EDITAVEIS["rf"]]) / 100,
        erp=float(st.session_state[CHAVES_EDITAVEIS["erp"]]) / 100,
        g=float(st.session_state[CHAVES_EDITAVEIS["g"]]) / 100,
        bazin_taxa=float(st.session_state[CHAVES_EDITAVEIS["bazin_taxa"]]) / 100,
        graham_mult=float(st.session_state[CHAVES_EDITAVEIS["graham_mult"]]),
        min_pares_setor=int(st.session_state[CHAVES_EDITAVEIS["min_pares_setor"]]),
        fonte_rf=str(st.session_state[CHAVES_REFERENCIA["fonte_rf"]]),
        data_curva=st.session_state[CHAVES_REFERENCIA["data_curva"]],
        rf_padrao=bool(st.session_state[CHAVES_REFERENCIA["rf_padrao"]]),
    )


def renderizar_premissas(*, expanded: bool = False) -> PremissasValuation:
    """Renderiza controles compartilhados e devolve o conjunto imutável corrente."""
    padrao = premissas_padrao()
    _inicializar(padrao)
    with st.expander("Premissas", expanded=expanded):
        st.write("Edite os parâmetros e veja o cálculo ser refeito nesta sessão.")
        coluna_a, coluna_b, coluna_c = st.columns(3)
        with coluna_a:
            st.number_input(
                "Taxa livre de risco (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.10,
                format="%.2f",
                key=CHAVES_EDITAVEIS["rf"],
                help="Curva do Tesouro Prefixado interpolada para cinco anos.",
            )
        with coluna_b:
            st.number_input(
                "Prêmio de risco de ações (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.10,
                format="%.2f",
                key=CHAVES_EDITAVEIS["erp"],
                help="Parcela adicionada à taxa livre de risco para formar k.",
            )
        with coluna_c:
            st.number_input(
                "Crescimento perpétuo g (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.10,
                format="%.2f",
                key=CHAVES_EDITAVEIS["g"],
                help="Crescimento nominal usado no modelo de Gordon.",
            )

        coluna_d, coluna_e, coluna_f = st.columns(3)
        with coluna_d:
            st.number_input(
                "Taxa mínima de Bazin (%)",
                min_value=0.01,
                max_value=100.0,
                step=0.10,
                format="%.2f",
                key=CHAVES_EDITAVEIS["bazin_taxa"],
            )
        with coluna_e:
            st.number_input(
                "Multiplicador de Graham",
                min_value=0.01,
                step=0.50,
                key=CHAVES_EDITAVEIS["graham_mult"],
            )
        with coluna_f:
            st.number_input(
                "Mínimo de pares do setor",
                min_value=1,
                step=1,
                key=CHAVES_EDITAVEIS["min_pares_setor"],
            )

        atuais = _premissas_do_estado()
        metrica_k, metrica_fii = st.columns(2)
        metrica_k.metric("Custo do capital próprio (k)", f"{atuais.k:.2%}")
        metrica_fii.metric("Taxa exigida dos FIIs", f"{atuais.fii_taxa_exigida:.2%}")
        if atuais.data_curva is not None:
            st.caption(
                "Curva de referência: Tesouro Prefixado em "
                f"{atuais.data_curva.isoformat()} ({atuais.fonte_rf})."
            )
        else:
            st.caption("Curva de referência: padrão documentado de 12,00% (cache indisponível).")
        st.button(
            "Restaurar padrão",
            key="valuation_restaurar_padrao",
            on_click=restaurar_premissas,
            args=(padrao, st.session_state),
        )
    return _premissas_do_estado()
