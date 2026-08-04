"""Página: interpretador do Boletim Focus (BACEN)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from financas_taxonomia import UNIDADE_INDICADOR
from focus_data import comparar, leitura_anterior, leitura_mais_recente, serie_historica
from focus_leitura import ErroBuscaFocus, atualizar_e_obter_historico, carregar_cache
from focus_regras import explicar_leigo, resumo_efeitos

st.set_page_config(page_title="Boletim Focus", page_icon="📊", layout="wide")

st.title("📊 Boletim Focus, explicado")
st.info(
    "Conteúdo educacional, feito para ajudar iniciantes a entender o "
    "mercado -- não é recomendação de investimento personalizada.",
    icon="ℹ️",
)

atualizar = st.button("🔄 Atualizar com dados mais recentes")

if atualizar:
    with st.spinner("Buscando dados mais recentes na API do BACEN..."):
        try:
            historico = atualizar_e_obter_historico()
            st.success("Dados atualizados.")
        except ErroBuscaFocus as erro:
            st.error(str(erro))
            historico = carregar_cache()
else:
    historico = carregar_cache()

if not historico:
    st.warning(
        "Ainda não há dados salvos. Clique em 'Atualizar com dados mais "
        "recentes' para buscar o primeiro snapshot."
    )
    st.stop()

indicadores = sorted({leitura.indicador for leitura in historico})

comparativos = []
for indicador in indicadores:
    leituras_indicador = [leitura for leitura in historico if leitura.indicador == indicador]
    atual = leitura_mais_recente(leituras_indicador)
    anterior = leitura_anterior(historico, atual)
    comparativos.append(comparar(atual, anterior))

st.subheader("O que mudou esta semana")
colunas = st.columns(len(comparativos))
for coluna, comparativo in zip(colunas, comparativos):
    with coluna:
        unidade = UNIDADE_INDICADOR.get(comparativo.atual.indicador, "")
        st.metric(
            label=f"{comparativo.atual.indicador} ({unidade})",
            value=f"{comparativo.atual.mediana:.2f}",
            delta=f"{comparativo.delta:+.2f}" if comparativo.anterior else None,
        )
        st.caption(
            f"Referência: {comparativo.atual.referencia} · "
            f"coletado em {comparativo.atual.data_coleta.strftime('%d/%m/%Y')}"
        )

st.subheader("Explicando em linguagem simples")
for comparativo in comparativos:
    with st.expander(comparativo.atual.indicador, expanded=True):
        st.write(explicar_leigo(comparativo))
        efeitos = resumo_efeitos(comparativo)
        if efeitos:
            st.markdown("**Efeitos historicamente esperados por classe de investimento:**")
            for efeito in efeitos:
                icone = {"positivo": "🟢", "negativo": "🔴", "neutro": "⚪"}.get(efeito.sentido, "⚪")
                st.markdown(f"- {icone} **{efeito.classe.value}**: {efeito.explicacao}")

st.subheader("Como evoluiu nas últimas semanas")
for indicador in indicadores:
    serie = serie_historica(historico, indicador)
    unidade = UNIDADE_INDICADOR.get(indicador, "")
    st.caption(f"{indicador} ({unidade})")
    if len(serie) < 2:
        st.caption(
            "Ainda não há histórico suficiente (pelo menos 2 atualizações) "
            "para mostrar uma tendência aqui."
        )
        continue
    df_serie = pd.DataFrame(
        {"mediana": [leitura.mediana for leitura in serie]},
        index=[leitura.data_coleta for leitura in serie],
    )
    st.line_chart(df_serie)
    if indicador == "Selic":
        st.caption(
            "A 'próxima reunião do Copom' muda com o tempo -- quando o "
            "Copom se reúne, a linha pode dar um salto que não é uma "
            "mudança real de expectativa, e sim a troca de qual reunião "
            "está sendo observada."
        )

st.subheader("Tabela detalhada")
linhas_tabela = [
    {
        "Indicador": comparativo.atual.indicador,
        "Referência": comparativo.atual.referencia,
        "Mediana atual": comparativo.atual.mediana,
        "Mediana anterior": comparativo.anterior.mediana if comparativo.anterior else None,
        "Delta": comparativo.delta,
        "Mínimo": comparativo.atual.minimo,
        "Máximo": comparativo.atual.maximo,
        "Nº respondentes": comparativo.atual.num_respondentes,
    }
    for comparativo in comparativos
]
st.dataframe(pd.DataFrame(linhas_tabela), use_container_width=True, hide_index=True)

st.caption(
    "Fonte: BACEN -- Sistema de Expectativas de Mercado (Boletim Focus), "
    "via API pública Olinda."
)
