import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest


def test_resumo_mostra_veredito_provas_datas_limite_e_condicao():
    pagina = Path(__file__).resolve().parent / "apps" / "resumo_section.py"
    app = AppTest.from_file(pagina, default_timeout=15).run()

    assert not app.exception
    assert app.header[0].value == "O que merece atenção agora"
    assert "A curva ficou mais benigna que o Focus" in [
        item.value for item in app.subheader
    ]
    assert not app.metric
    markdown = " ".join(item.value for item in app.markdown)
    assert "Focus: 13,75% → 13,75%." in markdown
    assert "Curva: mediana de -24 bps." in markdown
    assert "Taxa de título não é previsão pura da Selic." in markdown
    assert "voltar ao intervalo estável" in markdown
    captions = " ".join(item.value for item in app.caption)
    assert "BACEN · Focus: 14/08/2026 e 21/08/2026" in captions
    assert "Tesouro Transparente: 19/08/2026 e 26/08/2026" in captions
    assert "CONTEXTO EXTERNO QUE COMPLEMENTA A LEITURA" in captions
    assert "PTAX / BACEN · Horizonte: próximas 4–12 semanas" in captions
    assert "Dólar ganhou força no período" in markdown
    assert "Por que Focus × Curva lidera" in markdown
    assert "o Resumo apenas escolhe a melhor leitura disponível" in markdown
    assert "não altera o veredito, o Radar nem a carteira" in markdown
    assert "não prova causa, probabilidade ou retorno futuro" in captions
