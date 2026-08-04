import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from financas_taxonomia import ClasseAtivo, Direcao
from motor_indicadores import classificar_direcao, efeitos_por_indicador


def test_classificar_direcao_subiu():
    assert classificar_direcao(0.5) == Direcao.SUBIU


def test_classificar_direcao_caiu():
    assert classificar_direcao(-0.5) == Direcao.CAIU


def test_classificar_direcao_estavel_dentro_do_limiar():
    assert classificar_direcao(0.01) == Direcao.ESTAVEL
    assert classificar_direcao(-0.01) == Direcao.ESTAVEL


def test_efeitos_selic_subiu_inclui_pos_fixado_positivo_e_bolsa_negativo():
    efeitos = efeitos_por_indicador("Selic", Direcao.SUBIU)
    classes = {efeito.classe: efeito.sentido for efeito in efeitos}
    assert classes[ClasseAtivo.POS_FIXADO] == "positivo"
    assert classes[ClasseAtivo.BOLSA] == "negativo"


def test_efeitos_selic_caiu_inverte_sentido_pos_fixado():
    efeitos = efeitos_por_indicador("Selic", Direcao.CAIU)
    classes = {efeito.classe: efeito.sentido for efeito in efeitos}
    assert classes[ClasseAtivo.POS_FIXADO] == "negativo"


def test_efeitos_ipca_subiu_favorece_ipca_mais():
    efeitos = efeitos_por_indicador("IPCA", Direcao.SUBIU)
    classes = {efeito.classe: efeito.sentido for efeito in efeitos}
    assert classes[ClasseAtivo.IPCA_MAIS] == "positivo"


def test_efeitos_indicador_desconhecido_retorna_vazio():
    assert efeitos_por_indicador("PIB", Direcao.SUBIU) == []


def test_efeitos_direcao_estavel_nao_cadastrada_retorna_vazio():
    assert efeitos_por_indicador("Selic", Direcao.ESTAVEL) == []


def test_efeitos_pib_total_subiu_favorece_bolsa():
    efeitos = efeitos_por_indicador("PIB Total", Direcao.SUBIU)
    classes = {efeito.classe: efeito.sentido for efeito in efeitos}
    assert classes[ClasseAtivo.BOLSA] == "positivo"


def test_efeitos_pib_total_caiu_prejudica_bolsa():
    efeitos = efeitos_por_indicador("PIB Total", Direcao.CAIU)
    classes = {efeito.classe: efeito.sentido for efeito in efeitos}
    assert classes[ClasseAtivo.BOLSA] == "negativo"


def test_efeitos_divida_publica_subiu_pressiona_cambio_e_prefixado():
    efeitos = efeitos_por_indicador("Dívida líquida do setor público", Direcao.SUBIU)
    classes = {efeito.classe: efeito.sentido for efeito in efeitos}
    assert classes[ClasseAtivo.CAMBIO] == "positivo"
    assert classes[ClasseAtivo.PRE_FIXADO] == "negativo"


def test_efeitos_igpm_nao_tem_regra_de_classe_de_ativo():
    assert efeitos_por_indicador("IGP-M", Direcao.SUBIU) == []
    assert efeitos_por_indicador("IGP-M", Direcao.CAIU) == []
