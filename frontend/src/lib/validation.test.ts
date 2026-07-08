import { describe, it, expect } from 'vitest'
import { ALIAS_RE, isValidUrl } from './validation'

describe('isValidUrl', () => {
  it('принимает http и https', () => {
    expect(isValidUrl('http://example.com')).toBe(true)
    expect(isValidUrl('https://example.com/path?query=1')).toBe(true)
  })

  it('отклоняет другие протоколы и мусор', () => {
    expect(isValidUrl('ftp://example.com')).toBe(false)
    expect(isValidUrl('example.com')).toBe(false)
    expect(isValidUrl('asdf')).toBe(false)
    expect(isValidUrl('')).toBe(false)
  })
})

describe('ALIAS_RE', () => {
  it('принимает 3-10 символов из букв/цифр/дефиса/подчёркивания', () => {
    expect(ALIAS_RE.test('abc')).toBe(true)
    expect(ALIAS_RE.test('my_alias-1')).toBe(true)
    expect(ALIAS_RE.test('a1b2c3d4e5')).toBe(true) // ровно 10
  })

  it('отклоняет слишком короткие/длинные и недопустимые символы', () => {
    expect(ALIAS_RE.test('ab')).toBe(false) // 2 символа
    expect(ALIAS_RE.test('a'.repeat(11))).toBe(false) // 11 символов
    expect(ALIAS_RE.test('alias!')).toBe(false)
    expect(ALIAS_RE.test('alias space')).toBe(false)
  })
})
