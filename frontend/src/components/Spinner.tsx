export function Spinner() {
  return (
    <div className="flex justify-center py-8" role="status" aria-label="loading">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900 dark:border-gray-700 dark:border-t-gray-100" />
    </div>
  )
}
