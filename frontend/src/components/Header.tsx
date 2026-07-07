import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../auth/AuthContext'

export function Header() {
  const { t } = useTranslation()
  const { token, logout } = useAuth()

  return (
    <header className="border-b border-gray-200 dark:border-gray-800">
      <nav className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
        <Link to="/" className="font-semibold text-gray-900 dark:text-gray-100">
          Link Shortener
        </Link>
        <div className="flex items-center gap-4 text-sm">
          <Link to="/about">{t('nav.about')}</Link>
          {token ? (
            <>
              <Link to="/dashboard">{t('nav.dashboard')}</Link>
              {/* Никакого navigate() здесь: logout() стирает токен, а дальше
                  RequireAuth сам уводит со страницы, если она защищённая
                  (см. auth/RequireAuth.tsx). Ручной redirect на "/" отсюда
                  конфликтовал бы с тем, что HomePage при наличии токена
                  сама редиректит на /dashboard — гонка двух редиректов. */}
              <button type="button" onClick={logout} className="cursor-pointer">
                {t('nav.logout')}
              </button>
            </>
          ) : (
            <>
              <Link to="/login">{t('nav.login')}</Link>
              <Link to="/register">{t('nav.register')}</Link>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}
