import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export function NotFoundPage() {
  const { t } = useTranslation()

  return (
    <div className="mx-auto max-w-md py-12 text-center">
      <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">404</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">{t('notFound.message')}</p>
      <Link to="/" className="mt-6 inline-block text-sm underline">
        {t('notFound.backHome')}
      </Link>
    </div>
  )
}
