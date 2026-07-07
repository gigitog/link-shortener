import { useState, type FormEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createLink } from '../api/links'
import { ApiError } from '../api/client'
import type { LinkResponse } from '../api/types'
import { ALIAS_RE, isValidUrl } from '../lib/validation'
import { getErrorMessageKey } from '../lib/errors'
import { ErrorMessage } from './ErrorMessage'
import { CopyButton } from './CopyButton'

export function LinkForm() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()

  const [url, setUrl] = useState('')
  const [alias, setAlias] = useState('')
  // Последняя успешно созданная ссылка — показываем её отдельно с кнопкой
  // копирования, т.к. после invalidate она уедет на первую страницу списка
  // ниже, но не обязательно будет видна сразу (например, отфильтрована).
  const [createdLink, setCreatedLink] = useState<LinkResponse | null>(null)

  const urlInvalid = url.length > 0 && !isValidUrl(url)
  const aliasInvalid = alias.length > 0 && !ALIAS_RE.test(alias)

  const mutation = useMutation({
    mutationFn: () => createLink(url, alias),
    onSuccess: (data) => {
      // Список ссылок кэширован под ключами ['links', page] — инвалидируем
      // все страницы сразу (частичный ключ ['links'] matches их все).
      queryClient.invalidateQueries({ queryKey: ['links'] })
      setCreatedLink(data)
      setUrl('')
      setAlias('')
    },
  })

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (urlInvalid || aliasInvalid || !url) return
    mutation.mutate()
  }

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-800">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 sm:flex-row sm:items-start">
        <label className="flex flex-1 flex-col gap-1 text-sm text-gray-700 dark:text-gray-300">
          {t('links.urlLabel')}
          <input
            type="text"
            required
            placeholder={t('links.urlPlaceholder')}
            value={url}
            onChange={(event) => {
              setUrl(event.target.value)
              setCreatedLink(null)
            }}
            className="rounded-md border border-gray-300 px-3 py-2 dark:border-gray-700 dark:bg-gray-900"
          />
          {urlInvalid && <ErrorMessage>{t('links.urlInvalid')}</ErrorMessage>}
        </label>

        <label className="flex flex-col gap-1 text-sm text-gray-700 dark:text-gray-300 sm:w-48">
          {t('links.aliasLabel')}
          <input
            type="text"
            value={alias}
            onChange={(event) => {
              setAlias(event.target.value)
              setCreatedLink(null)
            }}
            className="rounded-md border border-gray-300 px-3 py-2 dark:border-gray-700 dark:bg-gray-900"
          />
          {aliasInvalid && <ErrorMessage>{t('links.aliasInvalid')}</ErrorMessage>}
        </label>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="mt-6 rounded-md bg-gray-900 px-4 py-2 text-white disabled:opacity-50 dark:bg-gray-100 dark:text-gray-900"
        >
          {t('links.createButton')}
        </button>
      </form>

      {mutation.isError && (
        <div className="mt-3">
          <ErrorMessage>
            {t(
              getErrorMessageKey(
                mutation.error instanceof ApiError ? mutation.error.status : 0,
                'createLink',
              ),
            )}
          </ErrorMessage>
        </div>
      )}

      {createdLink && (
        <div className="mt-3 flex items-center gap-3 rounded-md bg-green-50 px-3 py-2 text-sm text-green-700 dark:bg-green-950 dark:text-green-300">
          <span>
            {t('links.createSuccess')}{' '}
            <a href={createdLink.short_url} className="underline" target="_blank" rel="noreferrer">
              {createdLink.short_url}
            </a>
          </span>
          <CopyButton text={createdLink.short_url} />
        </div>
      )}
    </div>
  )
}
