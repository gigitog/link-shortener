/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Тесты идут через Vitest поверх этого же конфига (тот же react-плагин,
  // тот же resolve) — не нужен отдельный jest.config.
  test: {
    // jsdom эмулирует DOM в Node — без него React Testing Library негде рендерить.
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
  },
  server: {
    proxy: {
      // В деве фронт (порт 5173) и бэкенд (порт 8000) — разные origin,
      // без этого браузер звал бы CORS. Прокси делает вид, что запрос
      // идёт с того же origin, что и страница, а Vite сам пересылает
      // его на uvicorn. Заодно зеркалит боевую схему: в проде Caddy точно
      // так же срезает префикс /api и проксирует остаток пути на app:8000
      // (см. docker/Caddyfile, handle_path /api/*).
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
