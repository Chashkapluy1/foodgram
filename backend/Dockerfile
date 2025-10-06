   # Используем официальный образ Python
    FROM python:3.11-slim

    # Устанавливаем рабочую директорию внутри контейнера
    WORKDIR /app

    # Копируем файл зависимостей
    COPY requirements.txt .

    # Устанавливаем зависимости
    RUN pip install --no-cache-dir -r requirements.txt

    COPY . .

    EXPOSE 8000

    # Команда, которая будет выполняться при запуске контейнера
    CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
