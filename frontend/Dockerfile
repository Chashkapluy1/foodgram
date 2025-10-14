FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . ./
RUN npm run build

FROM alpine:latest
COPY --from=builder /app/build /app/build
