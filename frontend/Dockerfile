# Используем легковесный образ Node.js
FROM node:18-alpine

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Копируем весь код и собираем билд
COPY . ./
RUN npm run build
