import { useTranslation } from 'react-i18next'

// Витрина для рекрутёра (стек, дорожная карта) — PR 4.
export function AboutPage() {
  const { t } = useTranslation()
  return <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{t('nav.about')}</h1>
}
