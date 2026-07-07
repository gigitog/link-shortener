import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

// Роут-guard: оборачивает защищённые страницы в router.tsx (см. <Route element={<RequireAuth />}>).
// Нет токена → редирект на /login. Outlet — место, куда react-router
// подставляет вложенный (дочерний) маршрут, если проверка пройдена.
export function RequireAuth() {
  const { token } = useAuth()

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
