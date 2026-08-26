"""Formatação pura da leitura Focus × Curva para a interface."""

from __future__ import annotations

from convergencia_modelo import SinalCurva, SinalFocus, SinalPonta
from curva_apresentacao import formatar_bps, formatar_numero


def _direcao_curta(sinal: SinalFocus | SinalCurva | SinalPonta) -> str:
    return sinal.direcao.value.removeprefix("Mais ").capitalize()


def valor_focus(sinal: SinalFocus | None) -> str:
    if sinal is None:
        return "Sem comparação"
    prefixo = "+" if sinal.delta_pp > 0 else ""
    return f"{prefixo}{formatar_numero(sinal.delta_pp)} p.p."


def detalhe_focus(sinal: SinalFocus | None) -> str:
    if sinal is None:
        return "Duas coletas da mesma reunião"
    return f"{_direcao_curta(sinal)} · {sinal.referencia}"


def valor_curva(sinal: SinalCurva | None) -> str:
    return formatar_bps(sinal.delta_mediano_bps if sinal else None)


def detalhe_curva(sinal: SinalCurva | None) -> str:
    if sinal is None:
        return "Ao menos 2 vencimentos em comum"
    return f"{_direcao_curta(sinal)} · {sinal.vencimentos_comparaveis} venc."


def valor_ponta(sinal: SinalPonta | None) -> str:
    return formatar_bps(sinal.delta_mediano_bps if sinal else None)


def detalhe_ponta(sinal: SinalPonta | None) -> str:
    if sinal is None:
        return "Recorte disponível com 4+ vencimentos"
    anos = "–".join(str(data.year) for data in sinal.vencimentos)
    return f"{_direcao_curta(sinal)} · {anos}"
