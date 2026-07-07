import { useTranslation } from 'react-i18next'
import type { LinkResponse } from '../api/types'
import { CopyButton } from './CopyButton'

const dateFormatter = new Intl.DateTimeFormat('de-DE', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export function LinkTable({ links }: { links: LinkResponse[] }) {
  const { t } = useTranslation()

  if (links.length === 0) {
    return <p className="py-8 text-center text-sm text-gray-500 dark:text-gray-400">{t('links.empty')}</p>
  }

  return (
    <table className="w-full text-left text-sm">
      <thead>
        <tr className="border-b border-gray-200 text-gray-500 dark:border-gray-800 dark:text-gray-400">
          <th className="py-2 pr-4 font-medium">{t('links.columnShortUrl')}</th>
          <th className="py-2 pr-4 font-medium">{t('links.columnOriginalUrl')}</th>
          <th className="py-2 pr-4 font-medium">{t('links.columnClicks')}</th>
          <th className="py-2 pr-4 font-medium">{t('links.columnCreatedAt')}</th>
          <th className="py-2 font-medium" />
        </tr>
      </thead>
      <tbody>
        {links.map((link) => (
          <tr key={link.id} className="border-b border-gray-100 dark:border-gray-900">
            <td className="py-2 pr-4">
              <a
                href={link.short_url}
                target="_blank"
                rel="noreferrer"
                className="text-gray-900 underline dark:text-gray-100"
              >
                {link.short_url}
              </a>
            </td>
            {/* title показывает полный URL по наведению — сама ячейка обрезается CSS,
                а не substring в JS, так строка не портится и остаётся доступной для копирования. */}
            <td className="max-w-xs truncate py-2 pr-4 text-gray-600 dark:text-gray-400" title={link.original_url}>
              {link.original_url}
            </td>
            <td className="py-2 pr-4 text-gray-600 dark:text-gray-400">{link.clicks_count}</td>
            <td className="py-2 pr-4 text-gray-600 dark:text-gray-400">
              {dateFormatter.format(new Date(link.created_at))}
            </td>
            <td className="py-2">
              <CopyButton text={link.short_url} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
