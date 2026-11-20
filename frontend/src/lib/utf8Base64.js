// The server receives the program as base64 of its UTF-8 bytes (any Unicode
// character, e.g. Polish letters in comments or strings, is allowed).
export function encodeUtf8Base64(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = '';
  bytes.forEach((byte) => { binary += String.fromCharCode(byte); });
  return btoa(binary);
}
