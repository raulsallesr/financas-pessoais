import { demoSnapshot } from "./demoSnapshot";
import {
  AssetClass,
  ClassEffect,
  MarketSignal,
  MarketSnapshot,
  MarketSource,
  PublicMarketSnapshotV1,
  SignalTone,
  SnapshotProof,
} from "../domain/types";
import { ASSET_CLASSES } from "../domain/privatePortfolio";

const SIGNAL_TONES: readonly SignalTone[] = ["positive", "attention", "neutral"];
const FORBIDDEN_PUBLIC_KEYS = new Set([
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
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isIsoDate(value: unknown): value is string {
  return typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value);
}

function isIsoDateTime(value: unknown): value is string {
  return (
    typeof value === "string" &&
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value)
  );
}

function containsForbiddenKey(value: unknown): boolean {
  if (Array.isArray(value)) {
    return value.some(containsForbiddenKey);
  }
  if (!isRecord(value)) {
    return false;
  }
  return Object.entries(value).some(
    ([key, item]) => FORBIDDEN_PUBLIC_KEYS.has(key.toLowerCase()) || containsForbiddenKey(item),
  );
}

function isStringArray(value: unknown): value is readonly string[] {
  return Array.isArray(value) && value.every(isNonEmptyString);
}

function isProof(value: unknown): value is SnapshotProof {
  return (
    isRecord(value) &&
    isNonEmptyString(value.source) &&
    isNonEmptyString(value.text)
  );
}

function isSource(value: unknown): value is MarketSource {
  return (
    isRecord(value) &&
    isNonEmptyString(value.id) &&
    isNonEmptyString(value.label) &&
    typeof value.available === "boolean" &&
    (value.asOf === null || isIsoDate(value.asOf)) &&
    isNonEmptyString(value.status)
  );
}

function isClassEffect(value: unknown): value is ClassEffect {
  return (
    isRecord(value) &&
    SIGNAL_TONES.includes(value.tone as SignalTone) &&
    isNonEmptyString(value.headline) &&
    isNonEmptyString(value.explanation)
  );
}

function isEffects(value: unknown): value is MarketSignal["effects"] {
  if (!isRecord(value)) {
    return false;
  }
  return Object.entries(value).every(
    ([assetClass, effect]) =>
      ASSET_CLASSES.includes(assetClass as AssetClass) && isClassEffect(effect),
  );
}

function isSignal(value: unknown): value is MarketSignal {
  return (
    isRecord(value) &&
    isNonEmptyString(value.id) &&
    isNonEmptyString(value.label) &&
    isNonEmptyString(value.value) &&
    isNonEmptyString(value.change) &&
    isNonEmptyString(value.headline) &&
    isNonEmptyString(value.explanation) &&
    isNonEmptyString(value.source) &&
    isIsoDate(value.updatedAt) &&
    SIGNAL_TONES.includes(value.tone as SignalTone) &&
    isEffects(value.effects)
  );
}

export function validateLiveSnapshot(
  document: unknown,
): document is PublicMarketSnapshotV1 {
  if (!isRecord(document) || containsForbiddenKey(document)) {
    return false;
  }
  if (
    document.schemaVersion !== 1 ||
    document.mode !== "live" ||
    !isIsoDateTime(document.generatedAt) ||
    !isIsoDate(document.asOf) ||
    !isNonEmptyString(document.verdict) ||
    !isNonEmptyString(document.verdictSupport) ||
    !Array.isArray(document.proofs) ||
    document.proofs.length === 0 ||
    !document.proofs.every(isProof) ||
    !Array.isArray(document.sources) ||
    document.sources.length === 0 ||
    !document.sources.every(isSource) ||
    !Array.isArray(document.signals) ||
    document.signals.length === 0 ||
    !document.signals.every(isSignal) ||
    !isStringArray(document.limits) ||
    !isStringArray(document.changeConditions)
  ) {
    return false;
  }
  const signalIds = document.signals.map((signal) => signal.id);
  const sourceIds = document.sources.map((source) => source.id);
  return (
    new Set(signalIds).size === signalIds.length &&
    new Set(sourceIds).size === sourceIds.length
  );
}

export function selectMarketSnapshot(document: unknown): MarketSnapshot {
  let candidate = document;
  if (typeof document === "string") {
    try {
      candidate = JSON.parse(document);
    } catch {
      candidate = null;
    }
  }
  if (!validateLiveSnapshot(candidate)) {
    return {
      ...demoSnapshot,
      fallbackReason:
        "A fotografia pública está ausente ou incompatível. Exibindo dados sintéticos locais.",
    };
  }
  const sourcesAvailable = candidate.sources.filter((source) => source.available).length;
  return {
    ...candidate,
    positions: demoSnapshot.positions,
    sourcesAvailable,
    sourcesTotal: candidate.sources.length,
  };
}
