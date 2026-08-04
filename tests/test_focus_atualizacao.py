import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focus_atualizacao import (
    avaliar_atualidade,
    deve_verificar_automaticamente,
    dias_uteis_desde,
)


def test_dias_uteis_desde_ignora_fim_de_semana():
    assert dias_uteis_desde(date(2026, 7, 31), date(2026, 8, 3)) == 1


def test_verificacao_automatica_acontece_no_maximo_uma_vez_por_dia_util():
    hoje = date(2026, 8, 4)
    assert deve_verificar_automaticamente(None, hoje)
    assert deve_verificar_automaticamente(date(2026, 8, 3), hoje)
    assert not deve_verificar_automaticamente(hoje, hoje)


def test_verificacao_automatica_nao_repete_cache_antigo_no_fim_de_semana():
    sabado = date(2026, 8, 8)
    assert not deve_verificar_automaticamente(date(2026, 8, 7), sabado)


def test_status_sinaliza_dado_realmente_defasado_sem_depender_so_de_cor():
    status = avaliar_atualidade(
        date(2026, 7, 20),
        date(2026, 8, 4),
    )
    assert status.cor == "orange"
    assert status.rotulo == "Pode estar desatualizado"
    assert "dias úteis" in status.descricao
