// Зеркалит валидацию бэкенда (app/schemas/user.py), чтобы пользователь узнавал
// об ошибке сразу в форме, а не после round-trip на сервер и обратно (422).
export const PASSWORD_MIN_LENGTH = 8

// Зеркалит ALIAS_PATTERN + границы длины из app/schemas/link.py.
export const ALIAS_RE = /^[a-zA-Z0-9_-]{3,10}$/

// Грубая проверка на клиенте — бэкенд всё равно проверяет строже (Pydantic
// HttpUrl), это лишь чтобы не гонять на сервер очевидный мусор вроде "asdf".
export function isValidUrl(value: string): boolean {
  return /^https?:\/\/.+/.test(value)
}
