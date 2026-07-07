// Бэкенд отдаёт detail на русском (см. app/routers/*.py) — это внутренний
// язык кодовой базы, а не то, что должен увидеть немецкоязычный пользователь.
// Локализация самого API — отдельный этап дорожной карты (20), поэтому здесь
// мы просто маппим (статус, контекст запроса) → ключ в de.json, а не
// показываем detail напрямую.

export type ErrorContext = 'login' | 'register' | 'createLink'

export function getErrorMessageKey(status: number, context: ErrorContext): string {
  if (status === 429) return 'errors.tooManyRequests'
  if (status >= 500) return 'errors.serverError'

  if (context === 'login' && status === 401) return 'errors.invalidCredentials'
  if (context === 'register' && status === 409) return 'errors.emailTaken'
  if (context === 'createLink' && status === 409) return 'errors.aliasTaken'
  if (context === 'createLink' && status === 400) return 'errors.aliasReserved'

  return 'errors.generic'
}
