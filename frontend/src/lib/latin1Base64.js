// The server decodes the posted program as base64 -> bytes -> latin-1 (legacy
// contract of the jquery.base64 plugin). Characters above U+00FF cannot be sent.
export class UnsupportedCharacterError extends Error {
  constructor(char) {
    super(`unsupported character "${char}"`);
    this.char = char;
  }
}

export function encodeLatin1Base64(text) {
  let binary = '';
  for (const char of text) {
    const code = char.codePointAt(0);
    if (code > 0xff) throw new UnsupportedCharacterError(char);
    binary += String.fromCharCode(code);
  }
  return btoa(binary);
}
