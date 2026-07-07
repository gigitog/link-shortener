import { createBrowserRouter } from 'react-router-dom'
import { Layout } from './components/Layout'
import { RequireAuth } from './auth/RequireAuth'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardPage } from './pages/DashboardPage'
import { AboutPage } from './pages/AboutPage'
import { NotFoundPage } from './pages/NotFoundPage'

// Список путей здесь должен совпадать с матчером @spa в docker/Caddyfile (PR 5)
// и с RESERVED_PATHS на бэкенде (app/routers/links.py) — иначе короткая
// ссылка с таким же кодом станет недостижимой или наоборот, SPA перехватит
// путь, который должен был быть коротким кодом.
export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
      { path: '/about', element: <AboutPage /> },
      {
        element: <RequireAuth />,
        children: [{ path: '/dashboard', element: <DashboardPage /> }],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
