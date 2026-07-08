# Multi-stage: собираем статику в node-образе, отдаём её лёгким nginx —
# сам Node в финальном образе не нужен (только результат npm run build).

# ---------- Stage 1: build ----------
FROM node:22-alpine AS build
WORKDIR /app

# Сначала только манифесты — как и в бэкендовом Dockerfile: слой npm ci
# зависит лишь от package*.json, поэтому правки в src/ его не инвалидируют.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Версия сборки (короткий git SHA) приходит из deploy.yml как build-arg.
# ENV нужен, чтобы Vite увидел её как import.meta.env.VITE_APP_VERSION —
# ARG сам по себе виден только на этапе сборки, а не в коде приложения.
ARG VITE_APP_VERSION=dev
ENV VITE_APP_VERSION=$VITE_APP_VERSION
RUN npm run build

# ---------- Stage 2: runtime ----------
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
