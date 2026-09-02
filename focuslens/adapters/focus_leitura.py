"""Adaptador: busca dados do Boletim Focus na API pública do BACEN (Olinda) e
mantém um cache histórico local em JSON.

Fonte oficial: https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata
Sem autenticação. baseCalculo=0 = todos os respondentes (o número usado no
Boletim Focus oficial); baseCalculo=1 = só "Top 5 curto prazo" (não usado aqui).
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import requests

from focuslens.core.focus_data import LeituraIndicador
from focuslens.paths import DATA_DIR

BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"
TIMEOUT_SEGUNDOS = 15
CACHE_PATH = DATA_DIR / "focus_cache.json"
INDICADORES_ANUAIS = (
    "IPCA",
    "Câmbio",
    "PIB Total",
    "IGP-M",
    "Dívida líquida do setor público",
)


class ErroBuscaFocus(Exception):
    """Erro ao buscar dados do Focus na API do BACEN (rede, timeout, formato)."""


class ErroCacheFocus(Exception):
    """O cache local não pôde ser lido ou persistido com segurança."""


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
    try:
        conteudo = resposta.json()
        linhas = conteudo.get("value", [])
    except (AttributeError, ValueError) as erro:
        raise ErroBuscaFocus(
            "A API do Focus respondeu em um formato inesperado."
        ) from erro
    if not isinstance(linhas, list):
        raise ErroBuscaFocus(
            "A API do Focus respondeu em um formato inesperado."
        )
    return linhas


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
        *(buscar_anual(indicador, ano) for indicador in INDICADORES_ANUAIS),
    ]


def _amostrar_uma_leitura_por_semana(
    linhas: list[dict],
    referencia: str,
    max_semanas: int,
) -> list[LeituraIndicador]:
    """Mantém a coleta mais recente de cada semana ISO."""
    por_semana: dict[tuple[int, int], LeituraIndicador] = {}
    for linha in linhas:
        leitura = _linha_para_leitura(linha, referencia)
        calendario = leitura.data_coleta.isocalendar()
        chave = (calendario.year, calendario.week)
        existente = por_semana.get(chave)
        if existente is None or leitura.data_coleta > existente.data_coleta:
            por_semana[chave] = leitura
    return sorted(
        por_semana.values(),
        key=lambda leitura: leitura.data_coleta,
    )[-max_semanas:]


def buscar_historico_recente(
    ano_referencia: int | None = None,
    *,
    max_semanas: int = 12,
) -> list[LeituraIndicador]:
    """Busca uma fotografia semanal recente para o gráfico nascer útil."""
    if max_semanas < 2:
        raise ValueError("max_semanas deve ser pelo menos 2.")

    ano = ano_referencia or date.today().year
    limite = max_semanas * 7
    selic_atual = buscar_selic_proxima_reuniao()
    linhas_selic = _get(
        "ExpectativasMercadoSelic",
        {
            "$filter": (
                "baseCalculo eq 0 and "
                f"Reuniao eq '{selic_atual.referencia}'"
            ),
            "$orderby": "Data desc",
            "$top": limite,
        },
    )
    if not linhas_selic:
        raise ErroBuscaFocus(
            "A API do Focus não retornou o histórico recente da Selic."
        )

    historico = _amostrar_uma_leitura_por_semana(
        linhas_selic,
        selic_atual.referencia,
        max_semanas,
    )
    for indicador in INDICADORES_ANUAIS:
        linhas = _get(
            "ExpectativasMercadoAnuais",
            {
                "$filter": (
                    f"Indicador eq '{indicador}' and baseCalculo eq 0 "
                    f"and DataReferencia eq '{ano}'"
                ),
                "$orderby": "Data desc",
                "$top": limite,
            },
        )
        if not linhas:
            raise ErroBuscaFocus(
                f"A API do Focus não retornou o histórico de {indicador}."
            )
        historico.extend(
            _amostrar_uma_leitura_por_semana(
                linhas,
                str(ano),
                max_semanas,
            )
        )
    return historico


def historico_precisa_backfill(
    historico: list[LeituraIndicador],
    *,
    minimo_pontos: int = 2,
) -> bool:
    contagem = {
        indicador: len(
            {
                leitura.data_coleta
                for leitura in historico
                if leitura.indicador == indicador
            }
        )
        for indicador in ("Selic", *INDICADORES_ANUAIS)
    }
    return any(total < minimo_pontos for total in contagem.values())


def _ler_conteudo_cache() -> dict:
    if not CACHE_PATH.exists():
        return {"registros": []}
    try:
        conteudo = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as erro:
        raise ErroCacheFocus(
            "O histórico local do Focus está ilegível."
        ) from erro
    if not isinstance(conteudo, dict) or not isinstance(
        conteudo.get("registros", []), list
    ):
        raise ErroCacheFocus(
            "O histórico local do Focus tem uma estrutura inválida."
        )
    return conteudo


def data_ultima_atualizacao_cache() -> date | None:
    valor = _ler_conteudo_cache().get("atualizado_em")
    if valor is None:
        return None
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError) as erro:
        raise ErroCacheFocus(
            "A data de atualização do histórico local é inválida."
        ) from erro


def carregar_cache() -> list[LeituraIndicador]:
    conteudo = _ler_conteudo_cache()
    try:
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
    except (KeyError, TypeError, ValueError) as erro:
        raise ErroCacheFocus(
            "O histórico local do Focus contém um registro inválido."
        ) from erro


def consolidar_historico(
    historico: list[LeituraIndicador],
) -> list[LeituraIndicador]:
    registros_unicos = {}
    for leitura in historico:
        chave = (leitura.indicador, leitura.referencia, leitura.data_coleta.isoformat())
        registros_unicos[chave] = leitura
    return sorted(
        registros_unicos.values(),
        key=lambda leitura: (
            leitura.indicador,
            leitura.referencia,
            leitura.data_coleta,
        ),
    )


def salvar_cache(historico: list[LeituraIndicador]) -> None:
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
        for leitura in consolidar_historico(historico)
    ]
    conteudo = {
        "atualizado_em": date.today().isoformat(),
        "registros": registros,
    }
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporario: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=CACHE_PATH.parent,
            prefix=".focus_cache_",
            suffix=".tmp",
            delete=False,
        ) as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
            arquivo.flush()
            os.fsync(arquivo.fileno())
            temporario = Path(arquivo.name)
        temporario.replace(CACHE_PATH)
    except OSError as erro:
        raise ErroCacheFocus(
            "Não foi possível salvar o histórico local do Focus."
        ) from erro
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)


def atualizar_e_obter_historico() -> list[LeituraIndicador]:
    """Busca as leituras atuais na API, funde com o cache local e persiste."""
    try:
        historico = carregar_cache()
    except ErroCacheFocus:
        historico = []
    atuais = (
        buscar_historico_recente()
        if historico_precisa_backfill(historico)
        else buscar_leituras_atuais()
    )
    historico_atualizado = consolidar_historico(historico + atuais)
    salvar_cache(historico_atualizado)
    return historico_atualizado
