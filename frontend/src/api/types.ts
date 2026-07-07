// Зеркало Pydantic-схем бэкенда (app/schemas/*.py). Держим типы в одном
// файле, чтобы при изменении API на бэкенде было видно, что править на фронте.

export interface UserResponse {
  id: number
  email: string
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface LinkResponse {
  id: number
  short_code: string
  original_url: string
  short_url: string
  clicks_count: number
  created_at: string
}

export interface LinkListResponse {
  items: LinkResponse[]
  total: number
  limit: number
  offset: number
}
