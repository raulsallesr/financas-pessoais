import * as SecureStore from "expo-secure-store";

import {
  FavoriteSignalsV1,
  validateFavoriteSignals,
} from "../domain/favorites";

const FAVORITES_KEY = "focuslens.favorite-signals.v1";
const FAVORITES_SERVICE = "focuslens.favorite-signals.v1";

const FAVORITES_OPTIONS: SecureStore.SecureStoreOptions = {
  keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  keychainService: FAVORITES_SERVICE,
};

export class FavoriteSignalsStorageError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "FavoriteSignalsStorageError";
  }
}

export async function isFavoriteSignalsStorageAvailable(): Promise<boolean> {
  return SecureStore.isAvailableAsync();
}

export async function loadFavoriteSignals(): Promise<FavoriteSignalsV1 | null> {
  const encoded = await SecureStore.getItemAsync(FAVORITES_KEY, FAVORITES_OPTIONS);
  if (!encoded) {
    return null;
  }
  try {
    const document: unknown = JSON.parse(encoded);
    if (!validateFavoriteSignals(document)) {
      throw new FavoriteSignalsStorageError(
        "Os favoritos locais não respeitam o contrato v1.",
      );
    }
    return document;
  } catch (error) {
    if (error instanceof FavoriteSignalsStorageError) {
      throw error;
    }
    throw new FavoriteSignalsStorageError(
      "Não foi possível ler os favoritos deste aparelho.",
    );
  }
}

export async function saveFavoriteSignals(
  document: FavoriteSignalsV1,
): Promise<void> {
  if (!validateFavoriteSignals(document)) {
    throw new FavoriteSignalsStorageError(
      "Os favoritos não respeitam o contrato v1.",
    );
  }
  await SecureStore.setItemAsync(
    FAVORITES_KEY,
    JSON.stringify(document),
    FAVORITES_OPTIONS,
  );
}
