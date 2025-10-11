FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

# Используем npm INSTALL с флагом для более гибкого разрешения зависимостей
RUN npm install --legacy-peer-deps

COPY . .

# Собираем статику для продакшена
RUN npm run build