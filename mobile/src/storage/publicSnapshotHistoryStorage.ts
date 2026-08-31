import { File, Paths } from "expo-file-system";

import {
  MAX_PUBLIC_SNAPSHOTS,
  PUBLIC_SNAPSHOT_HISTORY_SCHEMA_VERSION,
  PublicSnapshotHistoryV1,
} from "../domain/snapshotHistory";
import { validateLiveSnapshot } from "../data/snapshotProvider";

const HISTORY_FILE = "focuslens-public-history-v1.json";
const HISTORY_TEMP_FILE = "focuslens-public-history-v1.tmp";
const MAX_HISTORY_BYTES = 512 * 1024;

export class PublicSnapshotHistoryStorageError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PublicSnapshotHistoryStorageError";
  }
}

function historyFile(): File {
  return new File(Paths.document, HISTORY_FILE);
}

function temporaryFile(): File {
  return new File(Paths.document, HISTORY_TEMP_FILE);
}

function validateHistoryDocument(
  document: unknown,
): document is PublicSnapshotHistoryV1 {
  if (typeof document !== "object" || document === null || Array.isArray(document)) {
    return false;
  }
  const candidate = document as Record<string, unknown>;
  return (
    candidate.schemaVersion === PUBLIC_SNAPSHOT_HISTORY_SCHEMA_VERSION &&
    Array.isArray(candidate.snapshots) &&
    candidate.snapshots.length <= MAX_PUBLIC_SNAPSHOTS &&
    candidate.snapshots.every(validateLiveSnapshot) &&
    new Set(
      candidate.snapshots.map((snapshot) => snapshot.generatedAt),
    ).size === candidate.snapshots.length
  );
}

export async function loadPublicSnapshotHistory(): Promise<PublicSnapshotHistoryV1 | null> {
  const file = historyFile();
  if (!file.exists) {
    return null;
  }
  if (file.size !== null && file.size > MAX_HISTORY_BYTES) {
    throw new PublicSnapshotHistoryStorageError(
      "O histórico público ultrapassou o limite local.",
    );
  }
  try {
    const document: unknown = JSON.parse(await file.text());
    if (!validateHistoryDocument(document)) {
      throw new PublicSnapshotHistoryStorageError(
        "O histórico público não respeita o contrato v1.",
      );
    }
    return document;
  } catch (error) {
    if (error instanceof PublicSnapshotHistoryStorageError) {
      throw error;
    }
    throw new PublicSnapshotHistoryStorageError(
      "Não foi possível ler a linha do tempo deste aparelho.",
    );
  }
}

export async function savePublicSnapshotHistory(
  document: PublicSnapshotHistoryV1,
): Promise<void> {
  if (!validateHistoryDocument(document)) {
    throw new PublicSnapshotHistoryStorageError(
      "O histórico público não respeita o contrato v1.",
    );
  }
  const encoded = JSON.stringify(document);
  if (encoded.length > MAX_HISTORY_BYTES) {
    throw new PublicSnapshotHistoryStorageError(
      "O histórico público ultrapassou o limite local.",
    );
  }
  const temporary = temporaryFile();
  const destination = historyFile();
  try {
    temporary.create({ overwrite: true });
    temporary.write(encoded);
    await temporary.move(destination, { overwrite: true });
  } catch (error) {
    if (temporary.exists) {
      temporary.delete();
    }
    throw error;
  }
}
