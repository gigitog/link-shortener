import type { ReactNode } from 'react'

export function ErrorMessage({ children }: { children: ReactNode }) {
  return (
    <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
      {children}
    </p>
  )
}
