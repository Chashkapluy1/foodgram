FROM nginx:1.23.3-alpine

# Копируем конфиг из текущей папки
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем документацию из папки docs (которая будет рядом)
COPY docs/ /usr/share/nginx/html/api/docs/