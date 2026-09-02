"""Atualiza a curva pública do Tesouro sem iniciar o Streamlit."""

from __future__ import annotations

from focuslens.adapters.curva_fontes import atualizar_e_obter_curva


def main() -> int:
    pontos = atualizar_e_obter_curva()
    datas = {ponto.data_referencia for ponto in pontos}
    if not pontos or not datas:
        raise RuntimeError("A atualização terminou sem pontos da curva.")
    data_atual = max(datas)
    vencimentos = {
        ponto.vencimento
        for ponto in pontos
        if ponto.data_referencia == data_atual
    }
    print(
        "Curva atualizada: "
        f"{len(pontos)} pontos em {len(datas)} datas, "
        f"{len(vencimentos)} vencimentos na curva de "
        f"{data_atual.isoformat()}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
