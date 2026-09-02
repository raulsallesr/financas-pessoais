from datetime import UTC, date, datetime

from focuslens.core.financas_taxonomia import Direcao
from focuslens.core.focus_data import ComparativoIndicador, LeituraIndicador
from focuslens.core.noticias_data import Noticia
from focuslens.core.noticias_focus import cruzar_noticias_com_focus


def _comparativo(indicador: str, direcao: Direcao) -> ComparativoIndicador:
    atual = LeituraIndicador(
        indicador=indicador,
        referencia="2026",
        data_coleta=date(2026, 8, 7),
        mediana=5.0,
        media=5.0,
        minimo=4.8,
        maximo=5.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )
    anterior = LeituraIndicador(
        indicador=indicador,
        referencia="2026",
        data_coleta=date(2026, 7, 31),
        mediana=4.9,
        media=4.9,
        minimo=4.7,
        maximo=5.1,
        desvio_padrao=0.1,
        num_respondentes=100,
    )
    return ComparativoIndicador(
        atual=atual,
        anterior=anterior,
        delta=0.1,
        direcao=direcao,
    )


def _noticia(titulo: str, fonte: str, indice: int) -> Noticia:
    return Noticia(
        titulo=titulo,
        link=f"https://exemplo.com/noticia-{indice}",
        fonte=fonte,
        publicada_em=datetime(2026, 8, 7, 12 - indice, tzinfo=UTC),
    )


def test_cruzamento_identifica_convergencia_e_tensao_multifuente():
    comparativos = [
        _comparativo("IPCA", Direcao.CAIU),
        _comparativo("Câmbio", Direcao.CAIU),
        _comparativo("Selic", Direcao.ESTAVEL),
    ]
    noticias = [
        _noticia("Inflação desacelera no mês", "Agência Brasil", 0),
        _noticia(
            "Mercado reduz expectativa de inflação",
            "InfoMoney",
            1,
        ),
        _noticia("Dólar sobe com pressão externa", "Money Times", 2),
        _noticia("Dólar avança diante do real", "InvestNews", 3),
        _noticia("Copom mantém Selic", "NeoFeed", 4),
    ]

    leituras = cruzar_noticias_com_focus(
        comparativos,
        noticias,
        limite_temas=5,
    )
    por_tema = {leitura.tema: leitura for leitura in leituras}

    assert por_tema["Inflação"].relacao == "Em linha"
    assert por_tema["Câmbio"].relacao == "Em tensão"
    assert por_tema["Juros"].relacao == "Sem direção clara"
    assert por_tema["Inflação"].fontes == ("Agência Brasil", "InfoMoney")
    assert len(por_tema["Câmbio"].destaques) == 2


def test_cruzamento_prioriza_temas_com_mais_fontes():
    comparativos = [
        _comparativo("IPCA", Direcao.ESTAVEL),
        _comparativo("Câmbio", Direcao.ESTAVEL),
    ]
    noticias = [
        _noticia("IPCA sobe", "Fonte A", 0),
        _noticia("Inflação acelera", "Fonte B", 1),
        _noticia("Dólar sobe", "Fonte A", 2),
    ]

    leituras = cruzar_noticias_com_focus(
        comparativos,
        noticias,
        limite_temas=1,
    )

    assert [leitura.tema for leitura in leituras] == ["Inflação"]


def test_cruzamento_nao_inventa_tema_apenas_por_categoria_ampla():
    noticia = Noticia(
        titulo="Ouro registra maior ganho semanal desde janeiro",
        link="https://exemplo.com/ouro",
        fonte="Fonte A",
        publicada_em=datetime(2026, 8, 7, tzinfo=UTC),
        categorias=("Juros", "Câmbio"),
    )

    leituras = cruzar_noticias_com_focus(
        [
            _comparativo("Selic", Direcao.ESTAVEL),
            _comparativo("Câmbio", Direcao.ESTAVEL),
        ],
        [noticia],
    )

    assert leituras == []
