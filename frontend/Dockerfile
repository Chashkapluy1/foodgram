# Этап 1: Сборка
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . ./
RUN npm run build


# Берем самый маленький образ, так как нам нужно только хранить файлы
FROM alpine:latest

# Копируем собранные файлы из этапа сборки
COPY --from=builder /app/build /app/build