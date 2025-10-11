    # Используем СТАРУЮ, СОВМЕСТИМУЮ версию Node.js
    FROM node:16-alpine

    WORKDIR /app

    COPY package*.json ./
        
    # Используем npm ci для надежной установки по lock-файлу
    RUN npm ci --legacy-peer-deps

    COPY . .

    # Собираем production-версию приложения
    RUN npm run build