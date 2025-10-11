# Используем базовый образ Node.js
FROM node:18-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json (если он есть)
# Если lock-файла нет, он просто скопирует package.json
COPY package*.json ./

# Устанавливаем зависимости. Эта команда самая надежная.
RUN npm install --legacy-peer-deps

# Копируем остальные файлы приложения
COPY . .

# Собираем статику
RUN npm run build