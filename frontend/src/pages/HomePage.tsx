import { Link, Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../auth/AuthContext'

export function HomePage() {
  const { t } = useTranslation()
  const { token } = useAuth()

  // Залогиненному незачем видеть лендинг — сразу на рабочий экран.
  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  // Полноценный лендинг (hero, CTA, ссылка на About) — PR 4.
  return (
    <div className="text-center">
      <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">Link Shortener</h1>
      <div className="mt-6 flex justify-center gap-4 text-sm">
        <Link to="/login" className="underline">
          {t('nav.login')}
        </Link>
        <Link to="/register" className="underline">
          {t('nav.register')}
        </Link>
      </div>
    </div>
  )
}
