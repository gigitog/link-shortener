import { useTranslation } from 'react-i18next'

const REPO_URL = 'https://github.com/gigitog/link-shortener'

export function Footer() {
  const { t } = useTranslation()
  // В dev VITE_APP_VERSION не задан (реальный git SHA приходит как build-arg
  // Docker-образа только в проде, см. PR 5) — тогда показываем "dev".
  const version = import.meta.env.VITE_APP_VERSION ?? 'dev'

  return (
    <footer className="border-t border-gray-200 px-4 py-4 text-center text-xs text-gray-500 dark:border-gray-800 dark:text-gray-400">
      <p>
        {t('footer.tagline')} —{' '}
        <a href={REPO_URL} target="_blank" rel="noreferrer" className="underline">
          {t('footer.sourceLink')}
        </a>
      </p>
      <p className="mt-1">
        {t('footer.version')}: {version}
      </p>
    </footer>
  )
}
