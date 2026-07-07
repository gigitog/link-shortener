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

  return (
    <div className="mx-auto max-w-xl py-12 text-center">
      <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">{t('home.heroTitle')}</h1>
      <p className="mt-4 text-gray-600 dark:text-gray-400">{t('home.heroSubtitle')}</p>

      <div className="mt-8 flex justify-center gap-4">
        <Link
          to="/register"
          className="rounded-md bg-gray-900 px-4 py-2 text-sm text-white dark:bg-gray-100 dark:text-gray-900"
        >
          {t('nav.register')}
        </Link>
        <Link
          to="/login"
          className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-900 dark:border-gray-700 dark:text-gray-100"
        >
          {t('nav.login')}
        </Link>
      </div>

      <Link to="/about" className="mt-6 inline-block text-sm underline text-gray-600 dark:text-gray-400">
        {t('home.aboutLink')}
      </Link>
    </div>
  )
}
