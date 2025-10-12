# Этап 1: Сборка приложения
# Называем этот этап 'builder', чтобы потом ссылаться на него
FROM node:18-alpine as builder

WORKDIR /app

# Копируем package.json и package-lock.json (или yarn.lock)
COPY package*.json ./
# Если используешь yarn, то: COPY yarn.lock ./

# Устанавливаем зависимости
RUN npm install
# Если используешь yarn, то: RUN yarn install

# Копируем весь остальной код
COPY . ./

# Запускаем сборку продакшен-версии
RUN npm run build

# Этап 2: Создание финального легковесного образа
# Используем простой alpine, чтобы просто хранить собранные файлы
FROM node:18-alpine

# Копируем собранные файлы из этапа 'builder'
COPY --from=builder /app/build /app/build
