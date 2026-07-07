// Тонкая обёртка над fetch — вместо отдельной библиотеки (axios).
// Всё, что нужно: базовый путь /api, JWT в заголовке, разбор ошибок в единый
// формат и различение «ожидаемого» 401 (неверный пароль) от «неожиданного»
// (токен истёк во время работы) — подробности у RequireAuthedRequest ниже.

const BASE = '/api'
const TOKEN_KEY = 'token'

// Единый тип ошибки для всего фронта: что бы ни случилось (сеть, 4xx, 5xx),
// компонент ловит именно ApiError и решает, что показать пользователю
// (см. lib/errors.ts — там status конвертируется в немецкую фразу).
export class ApiError extends Error {
  status: number
  detail: unknown

  constructor(status: number, detail: unknown) {
    super(`API error ${status}`)
    this.status = status
    this.detail = detail
  }
}

interface RequestOptions {
  method?: string
  body?: BodyInit
  headers?: Record<string, string>
  // true = «этот запрос требует токен, и 401 здесь означает — сессия
  // невалидна, разлогинь пользователя». false — для /auth/login и
  // /auth/register, где 401/409 это ОБЫЧНАЯ ошибка формы, а не разлогин
  // (иначе неверный пароль на форме логина сам себя тут же разлогинивал бы).
  authed?: boolean
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, authed = true } = options

  const finalHeaders: Record<string, string> = { ...headers }
  const token = localStorage.getItem(TOKEN_KEY)
  if (authed && token) {
    finalHeaders.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${BASE}${path}`, { method, body, headers: finalHeaders })

  if (!response.ok) {
    if (response.status === 401 && authed) {
      // Токен истёк или стал невалидным посреди работы (access-токен живёт
      // 30 минут, refresh-токена нет) — мягко выкидываем на логин.
      localStorage.removeItem(TOKEN_KEY)
      if (window.location.pathname !== '/login') {
        window.location.assign('/login?session_expired=1')
      }
    }

    // detail от бэкенда — на русском (см. app/routers/*.py); фронт никогда
    // не показывает его напрямую, а маппит по статусу в lib/errors.ts.
    let detail: unknown = null
    try {
      detail = (await response.json()).detail
    } catch {
      // тело не JSON (например, 500 без деталей) — не роняем парсинг
    }
    throw new ApiError(response.status, detail)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return response.json() as Promise<T>
}

export const apiClient = {
  get: <T>(path: string, options?: Partial<RequestOptions>) => request<T>(path, options),

  post: <T>(path: string, body?: unknown, options?: Partial<RequestOptions>) =>
    request<T>(path, {
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
      headers: { 'Content-Type': 'application/json' },
      ...options,
    }),

  // Отдельный метод для form-urlencoded — так вызывающий код (auth.ts)
  // не может случайно забыть про Content-Type для /auth/login.
  postForm: <T>(path: string, form: URLSearchParams, options?: Partial<RequestOptions>) =>
    request<T>(path, {
      method: 'POST',
      body: form,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      ...options,
    }),
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}
