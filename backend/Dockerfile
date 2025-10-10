FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости:
# - libjpeg-dev для библиотеки Pillow (обработка изображений)
# - postgresql-client для утилиты pg_isready в нашем скрипте ожидания
RUN apt-get update && \
    apt-get install -y libjpeg-dev postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Копируем скрипт ожидания и делаем его исполняемым
COPY ./wait-for-postgres.sh /usr/local/bin/wait-for-postgres.sh
RUN chmod +x /usr/local/bin/wait-for-postgres.sh

# Информационно указываем, что контейнер будет слушать порт 8000
EXPOSE 8000

# ENTRYPOINT выполнится при старте контейнера. Он будет ждать готовности БД.
# 'db' — это имя хоста (сервиса) базы данных из docker-compose.yml.
ENTRYPOINT ["wait-for-postgres.sh", "db"]

# CMD — это команда, которая выполнится ПОСЛЕ успешного завершения ENTRYPOINT.
# Она запустит наше приложение.
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
