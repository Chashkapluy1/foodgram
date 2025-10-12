FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
# Это делается отдельным шагом, чтобы использовать кэш Docker.
# Зависимости переустановятся только если requirements.txt изменится.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта в рабочую директорию
COPY . .

# Команда, которая будет запускаться при старте контейнера.
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
