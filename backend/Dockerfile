FROM python:3.10-slim

# Устанавливаем системную локаль в UTF-8
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    locales \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY wait-for-postgres.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-postgres.sh

RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
