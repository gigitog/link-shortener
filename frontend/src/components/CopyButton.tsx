import { useState } from 'react'
import { useTranslation } from 'react-i18next'

// Копирование в буфер обмена — Clipboard API асинхронный (требует https или
// localhost). После успеха на 2 секунды меняем подпись на «Kopiert!», чтобы
// дать пользователю обратную связь без модалок и тостов.
export function CopyButton({ text }: { text: string }) {
  const { t } = useTranslation()
  const [copied, setCopied] = useState(false)

  async function handleClick() {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className="rounded-md border border-gray-300 px-2 py-1 text-xs text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
    >
      {copied ? t('links.copied') : t('links.copy')}
    </button>
  )
}
