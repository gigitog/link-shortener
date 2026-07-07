import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useMutation } from '@tanstack/react-query'
import { login as loginRequest } from '../api/auth'
import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { getErrorMessageKey } from '../lib/errors'
import { ErrorMessage } from '../components/ErrorMessage'

export function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  // useMutation (TanStack Query) вместо ручных useState(loading/error):
  // isPending/isError/error считаются автоматически по ходу запроса.
  const mutation = useMutation({
    mutationFn: () => loginRequest(email, password),
    onSuccess: (data) => {
      login(data.access_token)
      navigate('/dashboard')
    },
  })

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="mb-6 text-2xl font-semibold text-gray-900 dark:text-gray-100">
        {t('auth.loginTitle')}
      </h1>

      {searchParams.get('session_expired') === '1' && (
        <div className="mb-4">
          <ErrorMessage>{t('auth.sessionExpired')}</ErrorMessage>
        </div>
      )}
      {searchParams.get('registered') === '1' && (
        <p className="mb-4 rounded-md bg-green-50 px-3 py-2 text-sm text-green-700 dark:bg-green-950 dark:text-green-300">
          {t('auth.registerSuccess')}
        </p>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm text-gray-700 dark:text-gray-300">
          {t('auth.emailLabel')}
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="rounded-md border border-gray-300 px-3 py-2 dark:border-gray-700 dark:bg-gray-900"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm text-gray-700 dark:text-gray-300">
          {t('auth.passwordLabel')}
          <input
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="rounded-md border border-gray-300 px-3 py-2 dark:border-gray-700 dark:bg-gray-900"
          />
        </label>

        {mutation.isError && (
          <ErrorMessage>
            {t(
              getErrorMessageKey(
                mutation.error instanceof ApiError ? mutation.error.status : 0,
                'login',
              ),
            )}
          </ErrorMessage>
        )}

        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-md bg-gray-900 px-4 py-2 text-white disabled:opacity-50 dark:bg-gray-100 dark:text-gray-900"
        >
          {t('auth.loginButton')}
        </button>
      </form>

      <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        {t('auth.noAccount')}{' '}
        <Link to="/register" className="underline">
          {t('nav.register')}
        </Link>
      </p>
    </div>
  )
}
