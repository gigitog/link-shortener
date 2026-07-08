// Подключает jest-dom матчеры (toBeInTheDocument, toBeDisabled, ...) к expect()
// Vitest. Файл подключается один раз перед всеми тестами через vite.config.ts
// (test.setupFiles) — сами тесты его не импортируют явно.
import '@testing-library/jest-dom/vitest'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

// Инициализирует i18next тем же способом, что и main.tsx (side-effect import) —
// без этого useTranslation() в тестируемых компонентах не найдёт переводы.
import './i18n'

// Без globals: true (мы используем явные импорты из 'vitest', а не магические
// globalThis.describe/it) React Testing Library не подключает автоочистку DOM
// между тестами сама — без неё второй render() в том же файле накапливал бы
// элементы поверх предыдущего, и getByText находил бы больше одного совпадения.
afterEach(cleanup)
