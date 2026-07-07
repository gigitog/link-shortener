import { apiClient } from './client'
import type { LinkListResponse, LinkResponse } from './types'

export function getLinks(limit: number, offset: number) {
  return apiClient.get<LinkListResponse>(`/links?limit=${limit}&offset=${offset}`)
}

export function createLink(originalUrl: string, customAlias?: string) {
  return apiClient.post<LinkResponse>('/links', {
    original_url: originalUrl,
    // Пустую строку из формы превращаем в undefined — бэкенд генерирует
    // код сам, если custom_alias не передан (см. app/schemas/link.py).
    custom_alias: customAlias || undefined,
  })
}
