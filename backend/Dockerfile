FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости:
RUN apt-get update && \
    apt-get install -y libjpeg-dev postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ./wait-for-postgres.sh /usr/local/bin/wait-for-postgres.sh
RUN chmod +x /usr/local/bin/wait-for-postgres.sh

EXPOSE 8000

ENTRYPOINT ["wait-for-postgres.sh", "db"]

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
