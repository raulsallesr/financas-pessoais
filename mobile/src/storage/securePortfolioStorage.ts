import {
  AESSealedData,
  AESEncryptionKey,
  aesDecryptAsync,
  aesEncryptAsync,
} from "expo-crypto";
import { File, Paths } from "expo-file-system";
import * as SecureStore from "expo-secure-store";

import {
  PrivatePortfolioV1,
  validatePrivatePortfolio,
} from "../domain/privatePortfolio";
import { decodeUtf8, encodeUtf8 } from "../domain/utf8";

const KEY_ALIAS = "focuslens.portfolio.key.v1";
const KEYCHAIN_SERVICE = "focuslens.portfolio.v1";
const PORTFOLIO_FILE = "focuslens-portfolio-v1.enc";
const TEMP_FILE = "focuslens-portfolio-v1.tmp";
const AUTHENTICATED_CONTEXT = "focuslens.private-portfolio.v1";

const SECURE_STORE_OPTIONS: SecureStore.SecureStoreOptions = {
  keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  keychainService: KEYCHAIN_SERVICE,
};

export type SecurePortfolioStorageErrorCode =
  | "unavailable"
  | "missing-key"
  | "corrupted"
  | "invalid-document";

export class SecurePortfolioStorageError extends Error {
  constructor(
    public readonly code: SecurePortfolioStorageErrorCode,
    message: string,
  ) {
    super(message);
    this.name = "SecurePortfolioStorageError";
  }
}

function portfolioFile(): File {
  return new File(Paths.document, PORTFOLIO_FILE);
}

function temporaryFile(): File {
  return new File(Paths.document, TEMP_FILE);
}

function authenticatedContext(): Uint8Array {
  return encodeUtf8(AUTHENTICATED_CONTEXT);
}

async function requireStorage(): Promise<void> {
  if (!(await SecureStore.isAvailableAsync())) {
    throw new SecurePortfolioStorageError(
      "unavailable",
      "O armazenamento seguro não está disponível neste dispositivo.",
    );
  }
}

async function loadKey(): Promise<AESEncryptionKey | null> {
  const encoded = await SecureStore.getItemAsync(KEY_ALIAS, SECURE_STORE_OPTIONS);
  return encoded ? AESEncryptionKey.import(encoded, "hex") : null;
}

async function loadOrCreateKey(): Promise<AESEncryptionKey> {
  const existing = await loadKey();
  if (existing) {
    return existing;
  }

  const generated = await AESEncryptionKey.generate();
  await SecureStore.setItemAsync(
    KEY_ALIAS,
    await generated.encoded("hex"),
    SECURE_STORE_OPTIONS,
  );
  return generated;
}

export async function isSecurePortfolioStorageAvailable(): Promise<boolean> {
  return SecureStore.isAvailableAsync();
}

export async function loadSecurePortfolio(): Promise<PrivatePortfolioV1 | null> {
  await requireStorage();
  const file = portfolioFile();
  if (!file.exists) {
    return null;
  }

  const key = await loadKey();
  if (!key) {
    throw new SecurePortfolioStorageError(
      "missing-key",
      "A carteira existe, mas a chave deste aparelho não está mais disponível.",
    );
  }

  try {
    const sealed = AESSealedData.fromCombined(await file.bytes());
    const plaintext = await aesDecryptAsync(sealed, key, {
      additionalData: authenticatedContext(),
      output: "bytes",
    });
    const document: unknown = JSON.parse(decodeUtf8(plaintext));
    if (!validatePrivatePortfolio(document)) {
      throw new SecurePortfolioStorageError(
        "invalid-document",
        "O conteúdo descriptografado não respeita o contrato privado v1.",
      );
    }
    return document;
  } catch (error) {
    if (error instanceof SecurePortfolioStorageError) {
      throw error;
    }
    throw new SecurePortfolioStorageError(
      "corrupted",
      "Não foi possível autenticar e abrir a carteira local.",
    );
  }
}

export async function saveSecurePortfolio(
  document: PrivatePortfolioV1,
): Promise<void> {
  await requireStorage();
  if (!validatePrivatePortfolio(document)) {
    throw new SecurePortfolioStorageError(
      "invalid-document",
      "A carteira não respeita o contrato privado v1.",
    );
  }

  const key = await loadOrCreateKey();
  const plaintext = encodeUtf8(JSON.stringify(document));
  const sealed = await aesEncryptAsync(plaintext, key, {
    additionalData: authenticatedContext(),
  });
  const encrypted = await sealed.combined();
  const temporary = temporaryFile();
  const destination = portfolioFile();

  try {
    temporary.create({ overwrite: true });
    temporary.write(encrypted);
    await temporary.move(destination, { overwrite: true });
  } catch (error) {
    if (temporary.exists) {
      temporary.delete();
    }
    throw error;
  }
}

export async function clearSecurePortfolio(): Promise<void> {
  await requireStorage();
  const file = portfolioFile();
  const temporary = temporaryFile();
  if (file.exists) {
    file.delete();
  }
  if (temporary.exists) {
    temporary.delete();
  }
  await SecureStore.deleteItemAsync(KEY_ALIAS, SECURE_STORE_OPTIONS);
}
