import { useTranslation } from 'react-i18next'

// Список ссылок, форма создания, пагинация — PR 3.
export function DashboardPage() {
  const { t } = useTranslation()
  return <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{t('nav.dashboard')}</h1>
}
