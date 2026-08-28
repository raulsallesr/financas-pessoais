import * as DocumentPicker from "expo-document-picker";
import { File, Paths } from "expo-file-system";
import { Platform } from "react-native";

import {
  B3ImportError,
  B3ImportResult,
  MAX_B3_FILE_BYTES,
  parseB3Workbook,
} from "../domain/b3Import";

const XLSX_MIME =
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

export type B3DocumentPickResult =
  | { kind: "cancelled" }
  | { kind: "selected"; fileName: string; result: B3ImportResult };

function safeFileName(value: string): string {
  return value.replace(/[\\/\u0000-\u001f]/g, "").trim().slice(0, 120);
}

function normalizeReadError(error: unknown): B3ImportError {
  if (error instanceof B3ImportError) {
    return error;
  }
  return new B3ImportError(
    "invalid-file",
    "Não foi possível ler a planilha escolhida neste aparelho.",
  );
}

export async function pickAndParseB3Document(): Promise<B3DocumentPickResult> {
  if (Platform.OS === "web") {
    throw new B3ImportError(
      "invalid-file",
      "A importação privada está disponível somente nos apps Android e iOS.",
    );
  }

  const picked = await DocumentPicker.getDocumentAsync({
    copyToCacheDirectory: true,
    multiple: false,
    type: [XLSX_MIME, "application/octet-stream"],
  });
  if (picked.canceled) {
    return { kind: "cancelled" };
  }

  const asset = picked.assets[0];
  if (!asset || !asset.name.toLowerCase().endsWith(".xlsx")) {
    throw new B3ImportError(
      "invalid-file",
      "Escolha a planilha XLSX exportada pela Área do Investidor B3.",
    );
  }
  if (asset.size !== undefined && asset.size > MAX_B3_FILE_BYTES) {
    throw new B3ImportError(
      "file-too-large",
      "A planilha excede o limite de 5 MB para processamento local.",
    );
  }

  const file = new File(asset.uri);
  if (!file.uri.startsWith(Paths.cache.uri)) {
    throw new B3ImportError(
      "invalid-file",
      "Não foi possível criar a cópia temporária privada da planilha.",
    );
  }

  let parsed: B3ImportResult;
  try {
    if (file.size > MAX_B3_FILE_BYTES) {
      throw new B3ImportError(
        "file-too-large",
        "A planilha excede o limite de 5 MB para processamento local.",
      );
    }
    parsed = parseB3Workbook(await file.bytes());
  } catch (error) {
    throw normalizeReadError(error);
  } finally {
    try {
      if (file.exists) {
        file.delete();
      }
    } catch {
      throw new B3ImportError(
        "invalid-file",
        "A cópia temporária da planilha não pôde ser descartada com segurança.",
      );
    }
  }

  return {
    kind: "selected",
    fileName: safeFileName(asset.name) || "posição-b3.xlsx",
    result: parsed,
  };
}
