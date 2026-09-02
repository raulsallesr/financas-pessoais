import sys
from datetime import UTC, date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from focuslens.core.focus_data import LeituraIndicador, comparar
from focuslens.core.macro_modelo import construir_cenario, extrair_temas_editoriais
from focuslens.core.mercado_data import PontoMercado, SerieMercado
from focuslens.core.noticias_data import Noticia


def _leitura(indicador: str, valor: float, data_coleta: date):
    return LeituraIndicador(
        indicador=indicador,
        referencia="2026",
        data_coleta=data_coleta,
        mediana=valor,
        media=valor,
        minimo=valor - 0.2,
        maximo=valor + 0.2,
        desvio_padrao=0.1,
        num_respondentes=100,
    )


def _comparativo(indicador: str, anterior: float, atual: float):
    return comparar(
        _leitura(indicador, atual, date(2026, 8, 4)),
        _leitura(indicador, anterior, date(2026, 7, 28)),
    )


def _serie(codigo: str, anterior: float, atual: float):
    nomes = {
        "USDBRL": ("Dólar PTAX", "R$"),
        "BRENT": ("Petróleo Brent", "US$/barril"),
        "BTCBRL": ("Bitcoin", "R$"),
    }
    nome, unidade = nomes[codigo]
    return SerieMercado(
        codigo=codigo,
        nome=nome,
        unidade=unidade,
        fonte="Teste",
        fonte_url="https://example.com",
        pontos=(
            PontoMercado(date(2026, 7, 1), anterior),
            PontoMercado(date(2026, 8, 4), atual),
        ),
    )


def _noticia(titulo: str):
    return Noticia(
        titulo=titulo,
        link="https://example.com/noticia",
        fonte="Teste",
        publicada_em=datetime(2026, 8, 4, tzinfo=UTC),
    )


def test_cenario_combina_focus_mercados_e_condiciona_projecao():
    comparativos = [
        _comparativo("Selic", 13.75, 14.0),
        _comparativo("IPCA", 4.8, 5.0),
        _comparativo("Câmbio", 5.0, 5.2),
        _comparativo("PIB Total", 2.0, 1.8),
        _comparativo(
            "Dívida líquida do setor público",
            69.0,
            70.0,
        ),
    ]
    series = [
        _serie("USDBRL", 5.0, 5.2),
        _serie("BRENT", 80.0, 88.0),
        _serie("BTCBRL", 400_000, 340_000),
    ]
    noticias = [
        _noticia("Inflação, Selic e dólar dominam o mercado"),
        _noticia("Petróleo sobe com risco no exterior"),
    ]
    cenario = construir_cenario(
        comparativos,
        series,
        noticias,
        hoje=date(2026, 8, 4),
    )

    assert cenario.titulo == "Juros altos com pressão inflacionária"
    assert cenario.confianca == "moderada"
    assert any(
        item.classe == "Pós-fixados"
        and item.estado == "vento favorável"
        for item in cenario.perspectivas
    )
    assert any(
        item.classe == "Prefixados longos"
        and item.estado == "mais pressionado"
        for item in cenario.perspectivas
    )
    assert any(
        item.classe == "Fundos imobiliários / FIAGRO"
        and item.estado == "mais pressionado"
        for item in cenario.perspectivas
    )
    assert cenario.invalidadores
    assert {"Inflação", "Juros"}.issubset(
        {tema.tema for tema in cenario.temas_editoriais}
    )


def test_motor_nao_usa_linguagem_imperativa_de_investimento():
    cenario = construir_cenario(
        [_comparativo("Selic", 13.75, 14.0)],
        [],
        [],
    )
    texto = " ".join(
        (
            cenario.titulo,
            cenario.resumo,
            *cenario.projecoes,
            *cenario.invalidadores,
            *(item.explicacao for item in cenario.perspectivas),
        )
    ).casefold()
    for proibida in ("compre", "venda", "invista", "recomendo"):
        assert proibida not in texto


def test_temas_editoriais_nao_inventam_tema_sem_palavra_chave():
    temas = extrair_temas_editoriais(
        [_noticia("Empresa anuncia novo produto")]
    )
    assert temas == ()


def test_temas_editoriais_nao_usam_categoria_ampla_como_evidencia():
    noticia = Noticia(
        titulo="Ouro registra maior ganho semanal desde janeiro",
        link="https://example.com/ouro",
        fonte="Teste",
        publicada_em=datetime(2026, 8, 4, tzinfo=UTC),
        categorias=("Juros", "Câmbio"),
    )

    assert extrair_temas_editoriais([noticia]) == ()


def test_fonte_muito_defasada_nao_sustenta_confianca_moderada():
    cenario = construir_cenario(
        [
            _comparativo("Selic", 13.75, 14.0),
            _comparativo("IPCA", 4.8, 5.0),
            _comparativo("PIB Total", 2.0, 1.8),
        ],
        [
            _serie("USDBRL", 5.0, 5.2),
            _serie("BRENT", 80.0, 88.0),
        ],
        [],
        hoje=date(2026, 9, 1),
    )
    assert cenario.confianca == "baixa"
