# build env
    FROM node:21.7.1-alpine
    WORKDIR /app
    COPY package*.json ./
    # Используем npm ci для надежной установки
    RUN npm ci
    COPY . ./
    RUN npm run build
