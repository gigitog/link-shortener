import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { getLinks } from '../api/links'
import { LinkForm } from '../components/LinkForm'
import { LinkTable } from '../components/LinkTable'
import { Pagination } from '../components/Pagination'
import { Spinner } from '../components/Spinner'
import { ErrorMessage } from '../components/ErrorMessage'

const PAGE_SIZE = 10

export function DashboardPage() {
  const { t } = useTranslation()
  const [page, setPage] = useState(1)

  const query = useQuery({
    queryKey: ['links', page],
    queryFn: () => getLinks(PAGE_SIZE, (page - 1) * PAGE_SIZE),
    // Без этого при переходе на новую страницу список на миг пропадал бы
    // (isLoading=true), пока не придёт ответ — так остаются старые данные.
    placeholderData: keepPreviousData,
  })

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{t('nav.dashboard')}</h1>

      <LinkForm />

      {query.isLoading && <Spinner />}
      {query.isError && <ErrorMessage>{t('errors.generic')}</ErrorMessage>}

      {query.data && (
        <>
          <LinkTable links={query.data.items} />
          <Pagination page={page} total={query.data.total} limit={PAGE_SIZE} onPageChange={setPage} />
        </>
      )}
    </div>
  )
}
