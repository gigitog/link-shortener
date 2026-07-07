import { useTranslation } from 'react-i18next'

const REPO_URL = 'https://github.com/gigitog/link-shortener'

// Namen von Technologien werden nicht übersetzt — deshalb hier statt in de.json.
const STACK = [
  'Python',
  'FastAPI',
  'PostgreSQL',
  'SQLAlchemy',
  'Docker',
  'Caddy',
  'GitHub Actions',
  'Hetzner',
  'React',
  'TypeScript',
  'Tailwind CSS',
]

export function AboutPage() {
  const { t } = useTranslation()

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{t('nav.about')}</h1>

      <div className="flex flex-col gap-3 text-sm text-gray-700 dark:text-gray-300">
        <p>{t('about.intro')}</p>
        <p>{t('about.architecture')}</p>
        <p>{t('about.deployment')}</p>
      </div>

      <section>
        <h2 className="mb-2 text-sm font-semibold text-gray-900 dark:text-gray-100">{t('about.stackTitle')}</h2>
        <div className="flex flex-wrap gap-2">
          {STACK.map((item) => (
            <span
              key={item}
              className="rounded-full border border-gray-300 px-3 py-1 text-xs text-gray-700 dark:border-gray-700 dark:text-gray-300"
            >
              {item}
            </span>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold text-gray-900 dark:text-gray-100">{t('about.roadmapTitle')}</h2>
        <div className="flex flex-col gap-2 text-sm text-gray-700 dark:text-gray-300">
          <p>
            <span className="font-medium text-gray-900 dark:text-gray-100">{t('about.roadmapDone')}:</span>{' '}
            {t('about.roadmapDoneItems')}
          </p>
          <p>
            <span className="font-medium text-gray-900 dark:text-gray-100">{t('about.roadmapNext')}:</span>{' '}
            {t('about.roadmapNextItems')}
          </p>
        </div>
      </section>

      <a href={REPO_URL} target="_blank" rel="noreferrer" className="text-sm underline text-gray-600 dark:text-gray-400">
        {t('about.sourceLink')}
      </a>
    </div>
  )
}
