import { MarketSignal } from "./types";

export const FAVORITE_SIGNALS_SCHEMA_VERSION = 1 as const;
export const MAX_FAVORITE_SIGNALS = 24;

export type FavoriteSignalsV1 = {
  schemaVersion: typeof FAVORITE_SIGNALS_SCHEMA_VERSION;
  signalIds: readonly string[];
};

function isSignalId(value: unknown): value is string {
  return (
    typeof value === "string" &&
    value.length > 0 &&
    value.length <= 96 &&
    /^[a-z0-9][a-z0-9._-]*$/i.test(value)
  );
}

export function validateFavoriteSignals(
  document: unknown,
): document is FavoriteSignalsV1 {
  if (typeof document !== "object" || document === null || Array.isArray(document)) {
    return false;
  }
  const candidate = document as Record<string, unknown>;
  if (
    candidate.schemaVersion !== FAVORITE_SIGNALS_SCHEMA_VERSION ||
    !Array.isArray(candidate.signalIds) ||
    candidate.signalIds.length > MAX_FAVORITE_SIGNALS ||
    !candidate.signalIds.every(isSignalId)
  ) {
    return false;
  }
  return new Set(candidate.signalIds).size === candidate.signalIds.length;
}

export function createFavoriteSignals(
  signalIds: readonly string[] = [],
): FavoriteSignalsV1 {
  const uniqueIds = [...new Set(signalIds.filter(isSignalId))].slice(
    0,
    MAX_FAVORITE_SIGNALS,
  );
  return {
    schemaVersion: FAVORITE_SIGNALS_SCHEMA_VERSION,
    signalIds: uniqueIds,
  };
}

export function toggleFavoriteSignal(
  favorites: FavoriteSignalsV1,
  signalId: string,
): FavoriteSignalsV1 {
  if (!isSignalId(signalId)) {
    throw new Error("O identificador do sinal é inválido.");
  }
  if (favorites.signalIds.includes(signalId)) {
    return createFavoriteSignals(
      favorites.signalIds.filter((currentId) => currentId !== signalId),
    );
  }
  if (favorites.signalIds.length >= MAX_FAVORITE_SIGNALS) {
    throw new Error(`Acompanhe no máximo ${MAX_FAVORITE_SIGNALS} sinais.`);
  }
  return createFavoriteSignals([...favorites.signalIds, signalId]);
}

export function orderSignalsByFavorites(
  signals: readonly MarketSignal[],
  favoriteIds: readonly string[],
): readonly MarketSignal[] {
  const favoriteOrder = new Map(
    favoriteIds.map((signalId, index) => [signalId, index]),
  );
  return signals
    .map((signal, originalIndex) => ({ signal, originalIndex }))
    .sort((left, right) => {
      const leftFavorite = favoriteOrder.get(left.signal.id);
      const rightFavorite = favoriteOrder.get(right.signal.id);
      if (leftFavorite !== undefined && rightFavorite !== undefined) {
        return leftFavorite - rightFavorite;
      }
      if (leftFavorite !== undefined) {
        return -1;
      }
      if (rightFavorite !== undefined) {
        return 1;
      }
      return left.originalIndex - right.originalIndex;
    })
    .map(({ signal }) => signal);
}
