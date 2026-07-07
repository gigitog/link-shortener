import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import de from './de.json'

// Пока только немецкий (см. дорожную карту, этап 20 добавит английский —
// вторым JSON-файлом в resources, без единой правки в JSX благодаря тому,
// что компоненты уже сейчас обращаются к текстам через t('namespace.key'),
// а не хардкодят строки).
i18n.use(initReactI18next).init({
  resources: { de: { translation: de } },
  lng: 'de',
  fallbackLng: 'de',
  interpolation: { escapeValue: false }, // React и так экранирует вывод — двойное экранирование не нужно
})

export default i18n
