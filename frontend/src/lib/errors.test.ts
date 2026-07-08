import { describe, it, expect } from 'vitest'
import { getErrorMessageKey } from './errors'

describe('getErrorMessageKey', () => {
  // 429 и 5xx — общие для любого контекста, проверяем это явно.
  it('429 и 5xx не зависят от контекста', () => {
    expect(getErrorMessageKey(429, 'login')).toBe('errors.tooManyRequests')
    expect(getErrorMessageKey(429, 'createLink')).toBe('errors.tooManyRequests')
    expect(getErrorMessageKey(500, 'register')).toBe('errors.serverError')
    expect(getErrorMessageKey(503, 'login')).toBe('errors.serverError')
  })

  it('login: 401 → неверные учётные данные', () => {
    expect(getErrorMessageKey(401, 'login')).toBe('errors.invalidCredentials')
  })

  it('register: 409 → email уже занят', () => {
    expect(getErrorMessageKey(409, 'register')).toBe('errors.emailTaken')
  })

  it('createLink: 409 → alias занят, 400 → alias зарезервирован', () => {
    expect(getErrorMessageKey(409, 'createLink')).toBe('errors.aliasTaken')
    expect(getErrorMessageKey(400, 'createLink')).toBe('errors.aliasReserved')
  })

  it('неизвестная комбинация статус+контекст → generic', () => {
    expect(getErrorMessageKey(401, 'createLink')).toBe('errors.generic')
    expect(getErrorMessageKey(0, 'login')).toBe('errors.generic')
  })
})
