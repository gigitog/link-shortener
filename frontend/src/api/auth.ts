import { apiClient } from './client'
import type { Token, UserResponse } from './types'

export function register(email: string, password: string) {
  return apiClient.post<UserResponse>('/auth/register', { email, password }, { authed: false })
}

export function login(email: string, password: string) {
  // Бэкенд принимает OAuth2PasswordRequestForm — это значит form-urlencoded
  // тело с полем "username" (кладём туда email), а НЕ JSON {email, password}.
  // Частая грабля при работе с встроенной OAuth2-авторизацией FastAPI.
  const form = new URLSearchParams({ username: email, password })
  return apiClient.postForm<Token>('/auth/login', form, { authed: false })
}

export function me() {
  return apiClient.get<UserResponse>('/auth/me')
}
