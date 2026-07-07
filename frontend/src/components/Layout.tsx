import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Footer } from './Footer'

// Общая рамка страницы: Header/Footer рендерятся один раз, а Outlet —
// это место, куда react-router подставляет текущую страницу-потомка
// (см. router.tsx — Layout оборачивает все маршруты).
export function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
