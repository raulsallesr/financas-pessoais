"""Atualiza o histórico público do Focus sem iniciar a interface Streamlit."""

from __future__ import annotations

from focus_leitura import atualizar_e_obter_historico


def main() -> int:
    historico = atualizar_e_obter_historico()
    indicadores = {leitura.indicador for leitura in historico}
    datas = {leitura.data_coleta for leitura in historico}
    if not historico or not datas:
        raise RuntimeError("A atualização terminou sem leituras do Focus.")
    print(
        "Histórico atualizado: "
        f"{len(historico)} registros, {len(indicadores)} indicadores, "
        f"coleta mais recente em {max(datas).isoformat()}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
