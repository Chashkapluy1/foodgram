FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
    
# Используем npm ci для надежной установки по lock-файлу
RUN npm ci

COPY . .

# Собираем production-версию приложения
RUN npm run build