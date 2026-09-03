"""Adaptador read-only dos motores Python para o contrato móvel público.

O módulo lê contratos já calculados, nunca consulta rede e nunca recebe dados de
carteira. A saída versionada pode ser publicada junto do app porque contém
somente dados públicos do Focus e do Tesouro Transparente.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from focuslens.adapters.curva_fontes import ErroCacheCurva
from focuslens.adapters.curva_fontes import carregar_cache as carregar_cache_curva
from focuslens.adapters.focus_leitura import ErroCacheFocus
from focuslens.adapters.focus_leitura import carregar_cache as carregar_cache_focus
from focuslens.core.convergencia_modelo import LeituraConvergencia, montar_leitura_convergencia
from focuslens.core.curva_data import PontoCurva
from focuslens.core.curva_modelo import (
    EstadoCurva,
    LeituraCurva,
    descricao_leitura_curva,
    montar_leitura_curva,
    titulo_leitura_curva,
)
from focuslens.core.financas_taxonomia import ClasseAtivo, Direcao
from focuslens.core.focus_data import ComparativoIndicador, LeituraIndicador, montar_comparativos
from focuslens.core.focus_regras import explicar_leigo, resumo_efeitos
from focuslens.core.focus_semanal import (
    EstadoFocusSemanal,
    ResumoFocusSemanal,
    montar_resumo_semanal,
)
from focuslens.core.resumo_integrado import ResumoIntegrado, montar_resumo_integrado
from focuslens.paths import MOBILE_DIR
from focuslens.ui.curva_apresentacao import formatar_bps
from focuslens.ui.focus_apresentacao import formatar_delta, formatar_valor

SCHEMA_VERSION = 1
DEFAULT_SNAPSHOT_PATH = MOBILE_DIR / "src" / "data" / "liveSnapshot.json"

_CLASSES_MOBILE = {
    ClasseAtivo.POS_FIXADO: "Renda fixa pós-fixada",
    ClasseAtivo.PRE_FIXADO: "Renda fixa prefixada",
    ClasseAtivo.IPCA_MAIS: "Títulos IPCA+",
    ClasseAtivo.BOLSA: "Bolsa brasileira",
    ClasseAtivo.CAMBIO: "Exterior / dólar",
}
_TONS = {
    "positivo": "positive",
    "negativo": "attention",
    "neutro": "neutral",
}
_HEADLINES_EFFECT = {
    "positivo": "Leitura historicamente favorável",
    "negativo": "Leitura pede atenção",
    "neutro": "Efeito historicamente misto",
}
_FORBIDDEN_PUBLIC_KEYS = {
    "amount",
    "cpf",
    "cnpj",
    "email",
    "identifier",
    "patrimonio",
    "portfolio",
    "position",
    "positions",
    "valor",
}
_REQUIRED_TOP_LEVEL = {
    "schemaVersion",
    "mode",
    "generatedAt",
    "asOf",
    "verdict",
    "verdictSupport",
    "proofs",
    "sources",
    "signals",
    "limits",
    "changeConditions",
}


@dataclass(frozen=True)
class ContratosSnapshotMobile:
    """Quatro contratos aprovados que alimentam o adaptador móvel."""

    resumo: ResumoIntegrado
    focus: ResumoFocusSemanal
    curva: LeituraCurva
    convergencia: LeituraConvergencia


def montar_contratos_snapshot(
    historico_focus: list[LeituraIndicador],
    pontos_curva: list[PontoCurva],
    hoje: date,
) -> ContratosSnapshotMobile:
    """Compõe os motores existentes a partir de dados já carregados."""
    comparativos = montar_comparativos(historico_focus)
    focus = montar_resumo_semanal(comparativos, hoje)
    curva = montar_leitura_curva(pontos_curva, hoje)
    convergencia = montar_leitura_convergencia(comparativos, curva, hoje)
    resumo = montar_resumo_integrado(focus, curva, convergencia)
    return ContratosSnapshotMobile(
        resumo=resumo,
        focus=focus,
        curva=curva,
        convergencia=convergencia,
    )


def carregar_contratos_dos_caches(
    hoje: date | None = None,
) -> ContratosSnapshotMobile:
    """Lê apenas os caches públicos versionados, com degradação por fonte."""
    try:
        historico_focus = carregar_cache_focus()
    except ErroCacheFocus:
        historico_focus = []
    try:
        pontos_curva = carregar_cache_curva()
    except ErroCacheCurva:
        pontos_curva = []
    return montar_contratos_snapshot(
        historico_focus,
        pontos_curva,
        hoje or date.today(),
    )


def _datetime_iso(valor: datetime) -> str:
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=UTC)
    return valor.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _efeitos_mobile(comparativo: ComparativoIndicador) -> dict[str, dict[str, str]]:
    efeitos: dict[str, dict[str, str]] = {}
    for efeito in resumo_efeitos(comparativo):
        classe = _CLASSES_MOBILE[efeito.classe]
        efeitos[classe] = {
            "tone": _TONS[efeito.sentido],
            "headline": _HEADLINES_EFFECT[efeito.sentido],
            "explanation": efeito.explicacao,
        }
    return efeitos


def _tom_sinal(efeitos: dict[str, dict[str, str]]) -> str:
    tons = {efeito["tone"] for efeito in efeitos.values()}
    if tons == {"positive"}:
        return "positive"
    if tons == {"attention"}:
        return "attention"
    return "neutral"


def _titulo_movimento(comparativo: ComparativoIndicador) -> str:
    indicador = comparativo.atual.indicador
    if comparativo.direcao == Direcao.SUBIU:
        return f"Expectativa de {indicador} subiu"
    if comparativo.direcao == Direcao.CAIU:
        return f"Expectativa de {indicador} caiu"
    return f"Expectativa de {indicador} segue estável"


def _sinal_focus(comparativo: ComparativoIndicador) -> dict[str, Any]:
    efeitos = _efeitos_mobile(comparativo)
    identificador = (
        comparativo.atual.indicador.lower()
        .replace("â", "a")
        .replace(" ", "-")
    )
    return {
        "id": f"focus-{identificador}",
        "label": f"Focus · {comparativo.atual.indicador}",
        "value": formatar_valor(comparativo),
        "change": formatar_delta(comparativo),
        "headline": _titulo_movimento(comparativo),
        "explanation": explicar_leigo(comparativo),
        "source": "BACEN · Focus",
        "updatedAt": comparativo.atual.data_coleta.isoformat(),
        "tone": _tom_sinal(efeitos),
        "effects": efeitos,
    }


def _sinal_curva(curva: LeituraCurva) -> dict[str, Any] | None:
    if curva.atual is None:
        return None
    movimento = formatar_bps(curva.movimento_mediano_d5_bps)
    return {
        "id": "curva-prefixada",
        "label": "Curva prefixada",
        "value": movimento,
        "change": "mediana frente a D-5",
        "headline": titulo_leitura_curva(curva),
        "explanation": descricao_leitura_curva(curva),
        "source": "Tesouro Transparente",
        "updatedAt": curva.atual.data_referencia.isoformat(),
        "tone": "neutral",
        # O motor de curva não calcula efeito por classe. Não inventar esse elo.
        "effects": {},
    }


def _fontes(contratos: ContratosSnapshotMobile) -> list[dict[str, Any]]:
    focus_disponivel = (
        contratos.focus.estado != EstadoFocusSemanal.INDISPONIVEL
        and contratos.focus.data_mais_recente is not None
    )
    curva_disponivel = (
        contratos.curva.estado != EstadoCurva.INDISPONIVEL
        and contratos.curva.atual is not None
    )
    return [
        {
            "id": "focus",
            "label": "BACEN · Focus",
            "available": focus_disponivel,
            "asOf": (
                contratos.focus.data_mais_recente.isoformat()
                if contratos.focus.data_mais_recente
                else None
            ),
            "status": contratos.focus.estado.value,
        },
        {
            "id": "curva",
            "label": "Tesouro Transparente",
            "available": curva_disponivel,
            "asOf": (
                contratos.curva.atual.data_referencia.isoformat()
                if contratos.curva.atual
                else None
            ),
            "status": contratos.curva.estado.value,
        },
    ]


def montar_snapshot_mobile(
    contratos: ContratosSnapshotMobile,
    *,
    gerado_em: datetime | None = None,
) -> dict[str, Any]:
    """Serializa os quatro contratos sem recalcular regras financeiras."""
    fontes = _fontes(contratos)
    sinais = [_sinal_focus(item) for item in contratos.focus.destaques]
    sinal_curva = _sinal_curva(contratos.curva)
    if sinal_curva is not None:
        sinais.append(sinal_curva)
    if not sinais:
        raise ValueError("As fontes não produziram nenhum sinal móvel publicável.")

    datas = [fonte["asOf"] for fonte in fontes if fonte["asOf"] is not None]
    provas = [
        {"source": prova.origem, "text": prova.descricao}
        for prova in contratos.resumo.provas
    ]
    snapshot = {
        "schemaVersion": SCHEMA_VERSION,
        "mode": "live",
        "generatedAt": _datetime_iso(gerado_em or datetime.now(UTC)),
        "asOf": max(datas),
        "verdict": contratos.resumo.veredito,
        "verdictSupport": provas[0]["text"],
        "proofs": provas,
        "sources": fontes,
        "signals": sinais,
        "limits": list(contratos.resumo.limites),
        "changeConditions": list(contratos.resumo.condicoes_de_mudanca),
    }
    validar_snapshot_publico(snapshot)
    return snapshot


def _chaves_proibidas(valor: Any) -> set[str]:
    if isinstance(valor, dict):
        encontradas = {
            str(chave).lower()
            for chave in valor
            if str(chave).lower() in _FORBIDDEN_PUBLIC_KEYS
        }
        for item in valor.values():
            encontradas.update(_chaves_proibidas(item))
        return encontradas
    if isinstance(valor, list):
        encontradas: set[str] = set()
        for item in valor:
            encontradas.update(_chaves_proibidas(item))
        return encontradas
    return set()


def validar_snapshot_publico(snapshot: dict[str, Any]) -> None:
    """Falha fechado para versão, estrutura mínima e dados de carteira."""
    faltantes = _REQUIRED_TOP_LEVEL.difference(snapshot)
    if faltantes:
        lista = ", ".join(sorted(faltantes))
        raise ValueError(f"O snapshot móvel não contém campos obrigatórios: {lista}.")
    if snapshot.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("Versão de schema móvel incompatível.")
    if snapshot.get("mode") != "live":
        raise ValueError("O artefato público deve usar mode=live.")
    if not snapshot.get("signals"):
        raise ValueError("O snapshot móvel exige ao menos um sinal.")
    if not snapshot.get("sources"):
        raise ValueError("O snapshot móvel exige fontes explícitas.")
    if not isinstance(snapshot["verdict"], str) or not snapshot["verdict"].strip():
        raise ValueError("O snapshot móvel exige veredito não vazio.")
    if not isinstance(snapshot["verdictSupport"], str) or not snapshot["verdictSupport"].strip():
        raise ValueError("O snapshot móvel exige suporte não vazio.")
    try:
        date.fromisoformat(snapshot["asOf"])
        datetime.fromisoformat(snapshot["generatedAt"].replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as erro:
        raise ValueError("O snapshot móvel exige datas ISO válidas.") from erro
    if not isinstance(snapshot["proofs"], list) or not snapshot["proofs"] or not all(
        isinstance(prova, dict)
        and isinstance(prova.get("source"), str)
        and prova["source"].strip()
        and isinstance(prova.get("text"), str)
        and prova["text"].strip()
        for prova in snapshot["proofs"]
    ):
        raise ValueError("As provas do snapshot móvel são inválidas.")
    if not isinstance(snapshot["sources"], list) or not all(
        isinstance(fonte, dict)
        and isinstance(fonte.get("id"), str)
        and fonte["id"].strip()
        and isinstance(fonte.get("label"), str)
        and fonte["label"].strip()
        and isinstance(fonte.get("available"), bool)
        and (fonte.get("asOf") is None or isinstance(fonte.get("asOf"), str))
        and isinstance(fonte.get("status"), str)
        and fonte["status"].strip()
        for fonte in snapshot["sources"]
    ):
        raise ValueError("As fontes do snapshot móvel são inválidas.")
    ids_fontes = [fonte["id"] for fonte in snapshot["sources"]]
    if len(set(ids_fontes)) != len(ids_fontes):
        raise ValueError("As fontes móveis exigem identificadores únicos.")
    try:
        for fonte in snapshot["sources"]:
            if fonte["asOf"] is not None:
                date.fromisoformat(fonte["asOf"])
    except ValueError as erro:
        raise ValueError("A data de uma fonte móvel é inválida.") from erro
    for campo in ("limits", "changeConditions"):
        if not isinstance(snapshot[campo], list) or not all(
            isinstance(item, str) and item.strip() for item in snapshot[campo]
        ):
            raise ValueError(f"O campo {campo} do snapshot móvel é inválido.")
    campos_sinal = {
        "id",
        "label",
        "value",
        "change",
        "headline",
        "explanation",
        "source",
        "updatedAt",
        "tone",
        "effects",
    }
    for sinal in snapshot["signals"]:
        if not isinstance(sinal, dict) or not campos_sinal.issubset(sinal):
            raise ValueError("A estrutura de um sinal móvel é inválida.")
        if not all(
            isinstance(sinal[campo], str) and sinal[campo].strip()
            for campo in campos_sinal.difference({"effects"})
        ):
            raise ValueError("Os campos textuais de um sinal móvel são inválidos.")
        try:
            date.fromisoformat(sinal["updatedAt"])
        except ValueError as erro:
            raise ValueError("A data de um sinal móvel é inválida.") from erro
        if sinal["tone"] not in {"positive", "attention", "neutral"}:
            raise ValueError("O tom de um sinal móvel é inválido.")
        if not isinstance(sinal["effects"], dict):
            raise ValueError("Os efeitos de um sinal móvel são inválidos.")
        for classe, efeito in sinal["effects"].items():
            if classe not in _CLASSES_MOBILE.values() or not isinstance(efeito, dict):
                raise ValueError("Uma classe de efeito móvel é inválida.")
            if (
                efeito.get("tone") not in {"positive", "attention", "neutral"}
                or not isinstance(efeito.get("headline"), str)
                or not efeito["headline"].strip()
                or not isinstance(efeito.get("explanation"), str)
                or not efeito["explanation"].strip()
            ):
                raise ValueError("Um efeito móvel é inválido.")
    ids = [sinal.get("id") for sinal in snapshot["signals"]]
    if any(not identificador for identificador in ids) or len(set(ids)) != len(ids):
        raise ValueError("Os sinais móveis exigem identificadores únicos.")
    proibidas = _chaves_proibidas(snapshot)
    if proibidas:
        lista = ", ".join(sorted(proibidas))
        raise ValueError(f"O snapshot público contém chaves proibidas: {lista}.")


def salvar_snapshot_mobile(
    snapshot: dict[str, Any],
    destino: Path = DEFAULT_SNAPSHOT_PATH,
) -> None:
    """Grava JSON UTF-8 estável e troca o arquivo de forma atômica."""
    validar_snapshot_publico(snapshot)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    conteudo = json.dumps(
        snapshot,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    descritor, temporario = tempfile.mkstemp(
        dir=destino.parent,
        prefix=f".{destino.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(descritor, "w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(conteudo)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, destino)
    finally:
        if os.path.exists(temporario):
            os.unlink(temporario)


def _preservar_generated_at_se_inalterado(
    snapshot: dict[str, Any],
    destino: Path,
) -> None:
    """Evita diff de relógio quando o conteúdo público não mudou."""
    try:
        anterior = json.loads(Path(destino).read_text(encoding="utf-8"))
        validar_snapshot_publico(anterior)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return
    conteudo_novo = {chave: valor for chave, valor in snapshot.items() if chave != "generatedAt"}
    conteudo_anterior = {
        chave: valor for chave, valor in anterior.items() if chave != "generatedAt"
    }
    if conteudo_novo == conteudo_anterior:
        snapshot["generatedAt"] = anterior["generatedAt"]


def gerar_snapshot_mobile(
    destino: Path = DEFAULT_SNAPSHOT_PATH,
    *,
    hoje: date | None = None,
    gerado_em: datetime | None = None,
) -> dict[str, Any]:
    """Gera o artefato somente dos caches locais e devolve o contrato salvo."""
    contratos = carregar_contratos_dos_caches(hoje)
    snapshot = montar_snapshot_mobile(contratos, gerado_em=gerado_em)
    if gerado_em is None:
        _preservar_generated_at_se_inalterado(snapshot, destino)
    salvar_snapshot_mobile(snapshot, destino)
    return snapshot
