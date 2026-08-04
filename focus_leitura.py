"""Adaptador: busca dados do Boletim Focus na API pública do BACEN (Olinda) e
mantém um cache histórico local em JSON.

Fonte oficial: https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata
Sem autenticação. baseCalculo=0 = todos os respondentes (o número usado no
Boletim Focus oficial); baseCalculo=1 = só "Top 5 curto prazo" (não usado aqui).
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import requests

from focus_data import LeituraIndicador

BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"
TIMEOUT_SEGUNDOS = 15
CACHE_PATH = Path(__file__).parent / "dados" / "focus_cache.json"


class ErroBuscaFocus(Exception):
    """Erro ao buscar dados do Focus na API do BACEN (rede, timeout, formato)."""


def _get(endpoint: str, params: dict) -> list[dict]:
    # A API da BACEN (Olinda) não decodifica corretamente o "+" que o
    # `requests` usa por padrão para espaços em query params -- exige "%20"
    # literal, senão devolve 400 ("types not compatible") mesmo em filtros
    # válidos. Por isso montamos a query string manualmente com quote().
    params = {**params, "$format": "json"}
    query = "&".join(f"{chave}={quote(str(valor), safe='')}" for chave, valor in params.items())
    try:
        resposta = requests.get(f"{BASE_URL}/{endpoint}?{query}", timeout=TIMEOUT_SEGUNDOS)
        resposta.raise_for_status()
    except requests.RequestException as erro:
        raise ErroBuscaFocus(
            f"Não foi possível buscar dados do Focus agora ({erro}). Tente novamente mais tarde."
        ) from erro
    return resposta.json().get("value", [])


def _chave_ordenacao_reuniao(reuniao: str) -> tuple[int, int]:
    """'R5/2026' -> (2026, 5), para ordenar cronologicamente (não alfabeticamente)."""
    match = re.match(r"R(\d+)/(\d+)", reuniao)
    if not match:
        return (9999, 99)
    numero, ano = match.groups()
    return (int(ano), int(numero))


def _linha_para_leitura(linha: dict, referencia: str) -> LeituraIndicador:
    return LeituraIndicador(
        indicador=linha["Indicador"],
        referencia=referencia,
        data_coleta=datetime.strptime(linha["Data"], "%Y-%m-%d").date(),
        mediana=linha["Mediana"],
        media=linha["Media"],
        minimo=linha["Minimo"],
        maximo=linha["Maximo"],
        desvio_padrao=linha["DesvioPadrao"],
        num_respondentes=linha["numeroRespondentes"],
    )


def buscar_selic_proxima_reuniao() -> LeituraIndicador:
    linhas = _get(
        "ExpectativasMercadoSelic",
        {"$filter": "baseCalculo eq 0", "$orderby": "Data desc", "$top": 40},
    )
    if not linhas:
        raise ErroBuscaFocus("A API do Focus não retornou nenhuma reunião do Copom.")
    data_mais_recente = max(linha["Data"] for linha in linhas)
    linhas_recentes = [linha for linha in linhas if linha["Data"] == data_mais_recente]
    proxima = min(linhas_recentes, key=lambda linha: _chave_ordenacao_reuniao(linha["Reuniao"]))
    return _linha_para_leitura(proxima, proxima["Reuniao"])


def buscar_anual(indicador: str, ano: int) -> LeituraIndicador:
    linhas = _get(
        "ExpectativasMercadoAnuais",
        {
            "$filter": f"Indicador eq '{indicador}' and baseCalculo eq 0 and DataReferencia eq '{ano}'",
            "$orderby": "Data desc",
            "$top": 1,
        },
    )
    if not linhas:
        raise ErroBuscaFocus(f"A API do Focus não retornou dados de {indicador} para {ano}.")
    return _linha_para_leitura(linhas[0], str(ano))


def buscar_leituras_atuais(ano_referencia: int | None = None) -> list[LeituraIndicador]:
    ano = ano_referencia or date.today().year
    return [
        buscar_selic_proxima_reuniao(),
        buscar_anual("IPCA", ano),
        buscar_anual("Câmbio", ano),
        buscar_anual("PIB Total", ano),
        buscar_anual("IGP-M", ano),
        buscar_anual("Dívida líquida do setor público", ano),
    ]


def carregar_cache() -> list[LeituraIndicador]:
    if not CACHE_PATH.exists():
        return []
    conteudo = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return [
        LeituraIndicador(
            indicador=registro["indicador"],
            referencia=registro["referencia"],
            data_coleta=date.fromisoformat(registro["data_coleta"]),
            mediana=registro["mediana"],
            media=registro["media"],
            minimo=registro["minimo"],
            maximo=registro["maximo"],
            desvio_padrao=registro["desvio_padrao"],
            num_respondentes=registro["num_respondentes"],
        )
        for registro in conteudo.get("registros", [])
    ]


def salvar_cache(historico: list[LeituraIndicador]) -> None:
    registros_unicos = {}
    for leitura in historico:
        chave = (leitura.indicador, leitura.referencia, leitura.data_coleta.isoformat())
        registros_unicos[chave] = leitura

    registros = [
        {
            "indicador": leitura.indicador,
            "referencia": leitura.referencia,
            "data_coleta": leitura.data_coleta.isoformat(),
            "mediana": leitura.mediana,
            "media": leitura.media,
            "minimo": leitura.minimo,
            "maximo": leitura.maximo,
            "desvio_padrao": leitura.desvio_padrao,
            "num_respondentes": leitura.num_respondentes,
        }
        for leitura in sorted(
            registros_unicos.values(),
            key=lambda leitura: (leitura.indicador, leitura.referencia, leitura.data_coleta),
        )
    ]
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(
            {"atualizado_em": date.today().isoformat(), "registros": registros},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def atualizar_e_obter_historico() -> list[LeituraIndicador]:
    """Busca as leituras atuais na API, funde com o cache local e persiste."""
    historico = carregar_cache()
    atuais = buscar_leituras_atuais()
    historico_atualizado = historico + atuais
    salvar_cache(historico_atualizado)
    return historico_atualizado
