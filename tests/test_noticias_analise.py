import sys
from datetime import UTC, date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from financas_taxonomia import Direcao
from focus_data import ComparativoIndicador, LeituraIndicador
from noticias_analise import analisar_artigo
from noticias_artigo import ArtigoExtraido
from noticias_data import Noticia


def _comparativo(indicador, direcao, mediana):
    atual = LeituraIndicador(
        indicador=indicador,
        referencia="2026",
        data_coleta=date(2026, 8, 4),
        mediana=mediana,
        media=mediana,
        minimo=mediana - 0.2,
        maximo=mediana + 0.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )
    return ComparativoIndicador(
        atual=atual,
        anterior=None,
        delta=0.1,
        direcao=direcao,
    )


def _artigo():
    noticia = Noticia(
        titulo="Alimentos e dívida entram no radar",
        link="https://agenciabrasil.ebc.com.br/economia/noticia",
        fonte="Agência Brasil",
        publicada_em=datetime(2026, 8, 7, tzinfo=UTC),
    )
    paragrafos = (
        (
            "Segundo a FAO, os preços dos alimentos sobem e reforçam a "
            "pressão inflacionária. O IPCA citado é de 5,2%."
        ),
        (
            "O Banco Central do Brasil acompanha a alta de juros. A dívida "
            "pública sobe e alcança R$ 1,4 bilhão no período."
        ),
    )
    return ArtigoExtraido(
        noticia=noticia,
        descricao="Alimentos e dívida pressionam os indicadores econômicos.",
        paragrafos=paragrafos,
        palavras=sum(len(item.split()) for item in paragrafos),
        origem="Texto da matéria",
        trecho_verificacao=(
            "Alimentos e dívida pressionam os indicadores econômicos."
        ),
        texto="\n\n".join(paragrafos),
    )


def test_analise_liga_evidencias_da_materia_ao_focus_sem_guardar_texto():
    analise = analisar_artigo(
        _artigo(),
        [
            _comparativo("IPCA", Direcao.SUBIU, 5.2),
            _comparativo(
                "Dívida líquida do setor público",
                Direcao.CAIU,
                69.5,
            ),
            _comparativo("Selic", Direcao.ESTAVEL, 14.0),
        ],
    )

    assert analise.temas[0] == "Inflação"
    assert "Fiscal" in analise.temas
    assert {
        (item.tema, item.relacao)
        for item in analise.conexoes
    } >= {
        ("Inflação", "Em linha"),
        ("Fiscal", "Em tensão"),
    }
    assert {(item.valor, item.contexto) for item in analise.numeros} >= {
        ("5,2%", "Inflação"),
        ("R$ 1,4 bilhão", "Fiscal"),
    }
    assert {"FAO", "Banco Central do Brasil"}.issubset(
        set(analise.instituicoes)
    )
    assert any("IPCA" in item for item in analise.onde_olhar)
    assert not hasattr(analise, "texto")


def test_analise_e_conservadora_quando_nao_ha_sinal_macro():
    artigo = _artigo()
    artigo_sem_sinal = ArtigoExtraido(
        noticia=artigo.noticia,
        descricao="Uma descrição editorial sem direção econômica.",
        paragrafos=("A matéria apresenta um novo serviço ao público.",),
        palavras=9,
        origem="Descrição editorial da página",
        trecho_verificacao="Uma descrição editorial sem direção econômica.",
        texto="A matéria apresenta um novo serviço ao público.",
    )

    analise = analisar_artigo(artigo_sem_sinal, [])

    assert analise.temas == ()
    assert analise.conexoes == ()
    assert "não contém sinais suficientes" in analise.sintese
    texto_gerado = " ".join(
        [analise.sintese, analise.limitacao, *analise.onde_olhar]
    ).casefold()
    assert all(
        termo not in texto_gerado
        for termo in ("compre", "venda", "invista", "recomendo")
    )
