export function encodeUtf8(value: string): Uint8Array {
  const bytes: number[] = [];
  for (const character of value) {
    const point = character.codePointAt(0);
    if (point === undefined) {
      continue;
    }
    if (point <= 0x7f) {
      bytes.push(point);
    } else if (point <= 0x7ff) {
      bytes.push(0xc0 | (point >> 6), 0x80 | (point & 0x3f));
    } else if (point <= 0xffff) {
      bytes.push(
        0xe0 | (point >> 12),
        0x80 | ((point >> 6) & 0x3f),
        0x80 | (point & 0x3f),
      );
    } else {
      bytes.push(
        0xf0 | (point >> 18),
        0x80 | ((point >> 12) & 0x3f),
        0x80 | ((point >> 6) & 0x3f),
        0x80 | (point & 0x3f),
      );
    }
  }
  return Uint8Array.from(bytes);
}

function continuation(bytes: Uint8Array, index: number): number {
  const byte = bytes[index];
  if (byte === undefined || (byte & 0xc0) !== 0x80) {
    throw new Error("Sequência UTF-8 inválida.");
  }
  return byte & 0x3f;
}

export function decodeUtf8(bytes: Uint8Array): string {
  const codePoints: number[] = [];
  for (let index = 0; index < bytes.length; ) {
    const first = bytes[index];
    let point: number;
    let width: number;

    if (first <= 0x7f) {
      point = first;
      width = 1;
    } else if (first >= 0xc2 && first <= 0xdf) {
      point = ((first & 0x1f) << 6) | continuation(bytes, index + 1);
      width = 2;
    } else if (first >= 0xe0 && first <= 0xef) {
      point =
        ((first & 0x0f) << 12) |
        (continuation(bytes, index + 1) << 6) |
        continuation(bytes, index + 2);
      width = 3;
      if (point < 0x800 || (point >= 0xd800 && point <= 0xdfff)) {
        throw new Error("Sequência UTF-8 inválida.");
      }
    } else if (first >= 0xf0 && first <= 0xf4) {
      point =
        ((first & 0x07) << 18) |
        (continuation(bytes, index + 1) << 12) |
        (continuation(bytes, index + 2) << 6) |
        continuation(bytes, index + 3);
      width = 4;
      if (point < 0x10000 || point > 0x10ffff) {
        throw new Error("Sequência UTF-8 inválida.");
      }
    } else {
      throw new Error("Sequência UTF-8 inválida.");
    }

    codePoints.push(point);
    index += width;
  }
  let result = "";
  for (let index = 0; index < codePoints.length; index += 4096) {
    result += String.fromCodePoint(...codePoints.slice(index, index + 4096));
  }
  return result;
}
