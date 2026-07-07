import { createContext, useContext, useState, type ReactNode } from 'react'
import { getToken, setToken as persistToken } from '../api/client'

interface AuthContextValue {
  // null = не авторизован. Само значение токена компонентам обычно не нужно —
  // им важен факт наличия (авторизован/нет), но храним и его на случай,
  // если понадобится где-то ещё (например, отладка).
  token: string | null
  login: (token: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  // Функция в useState (а не просто localStorage.getItem(...)) вызывается
  // ровно один раз — при первом рендере. Так мы не лезем в localStorage
  // на каждый ре-рендер компонента, только при монтировании.
  const [token, setToken] = useState<string | null>(() => getToken())

  function login(newToken: string) {
    persistToken(newToken)
    setToken(newToken)
  }

  function logout() {
    persistToken(null)
    setToken(null)
  }

  return <AuthContext.Provider value={{ token, login, logout }}>{children}</AuthContext.Provider>
}

// Хук-обёртка вместо прямого useContext(AuthContext) в компонентах:
// если кто-то забудет обернуть дерево в <AuthProvider>, ошибка будет явной
// («используй внутри провайдера»), а не тихим undefined.
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth должен использоваться внутри <AuthProvider>')
  }
  return ctx
}
