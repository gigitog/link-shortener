import { useTranslation } from 'react-i18next'

interface PaginationProps {
  page: number // 1-based — так удобнее показывать пользователю ("Seite 1")
  total: number
  limit: number
  onPageChange: (page: number) => void
}

export function Pagination({ page, total, limit, onPageChange }: PaginationProps) {
  const { t } = useTranslation()
  // max(1, ...) — чтобы при total=0 (список пуст) не показывать "Seite 1 von 0".
  const totalPages = Math.max(1, Math.ceil(total / limit))

  return (
    <div className="flex items-center justify-center gap-4 pt-4 text-sm">
      <button
        type="button"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
        className="rounded-md border border-gray-300 px-3 py-1 disabled:opacity-40 dark:border-gray-700"
      >
        {t('links.paginationPrev')}
      </button>
      <span className="text-gray-600 dark:text-gray-400">
        {t('links.paginationStatus', { page, total: totalPages })}
      </span>
      <button
        type="button"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
        className="rounded-md border border-gray-300 px-3 py-1 disabled:opacity-40 dark:border-gray-700"
      >
        {t('links.paginationNext')}
      </button>
    </div>
  )
}
