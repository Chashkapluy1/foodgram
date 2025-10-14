FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Копируем скрипт ожидания и даем ему права
COPY wait-for-postgres.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-postgres.sh

# Собираем статику админки прямо при сборке образа
RUN python manage.py collectstatic --no-input

# Entrypoint остается в docker-compose
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]