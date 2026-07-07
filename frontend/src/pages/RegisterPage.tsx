import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useMutation } from '@tanstack/react-query'
import { register as registerRequest } from '../api/auth'
import { ApiError } from '../api/client'
import { getErrorMessageKey } from '../lib/errors'
import { PASSWORD_MIN_LENGTH } from '../lib/validation'
import { ErrorMessage } from '../components/ErrorMessage'

export function RegisterPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  // Проверяем только когда пользователь начал печатать пароль — не пугаем
  // ошибкой валидации на пустом поле сразу при открытии формы.
  const passwordTooShort = password.length > 0 && password.length < PASSWORD_MIN_LENGTH

  const mutation = useMutation({
    mutationFn: () => registerRequest(email, password),
    // Register не возвращает токен — по API это отдельный шаг, поэтому
    // после успеха ведём на /login (а не сразу авторизуем).
    onSuccess: () => navigate('/login?registered=1'),
  })

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (passwordTooShort) return
    mutation.mutate()
  }

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="mb-6 text-2xl font-semibold text-gray-900 dark:text-gray-100">
        {t('auth.registerTitle')}
      </h1>

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
            minLength={PASSWORD_MIN_LENGTH}
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="rounded-md border border-gray-300 px-3 py-2 dark:border-gray-700 dark:bg-gray-900"
          />
        </label>

        {passwordTooShort && <ErrorMessage>{t('auth.passwordTooShort')}</ErrorMessage>}

        {mutation.isError && (
          <ErrorMessage>
            {t(
              getErrorMessageKey(
                mutation.error instanceof ApiError ? mutation.error.status : 0,
                'register',
              ),
            )}
          </ErrorMessage>
        )}

        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-md bg-gray-900 px-4 py-2 text-white disabled:opacity-50 dark:bg-gray-100 dark:text-gray-900"
        >
          {t('auth.registerButton')}
        </button>
      </form>

      <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        {t('auth.haveAccount')}{' '}
        <Link to="/login" className="underline">
          {t('nav.login')}
        </Link>
      </p>
    </div>
  )
}
