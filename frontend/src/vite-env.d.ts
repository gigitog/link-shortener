/// <reference types="vite/client" />

// Дополняем встроенный тип Vite своей переменной — без этого TS не знал бы
// про VITE_APP_VERSION при обращении к import.meta.env (см. components/Footer.tsx).
// Значение приходит из build-arg Docker-образа (PR 5); в dev-режиме — undefined.
interface ImportMetaEnv {
  readonly VITE_APP_VERSION?: string
}
