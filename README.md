### Foodgram: Платформа для обмена рецептами
![Foodgram CI/CD](https://github.com/Chashkapluy1/foodgram/actions/workflows/main.yml/badge.svg)

**Фудграм** — это учебный проект, представляющий собой API для платформы, где пользователи могут публиковать свои кулинарные рецепты, подписываться на других авторов, а также добавлять рецепты в избранное и список покупок.

Проект упакован в Docker-контейнеры и разворачивается на удаленном сервере с помощью CI/CD на базе GitHub Actions.

### Стек технологий
*   **Backend:** Python 3.11, Django, Django REST Framework
*   **Frontend:** React.js
*   **База данных:** PostgreSQL (в production-режиме), может применяться SQLite (в режиме разработки)
*   **Веб-сервер:** Nginx
*   **Контейнеризация:** Docker, Docker Compose
*   **CI/CD:** GitHub Actions

### Эндпоинты проекта
*   [Сайт](https://foodgram10.duckdns.org/)
*   [Админ-панель](https://foodgram10.duckdns.org/admin/)
*   [Документация API](https://foodgram10.duckdns.org/api/docs/)

### Развертывание проекта на сервере (Docker)
1.  Склонируйте репозиторий на ваш сервер:
    ```bash
    git clone https://github.com/Chashkapluy1/foodgram.git
    ```
2.  Перейдите в папку с проектом:
    ```bash
    cd foodgram/
    ```
3.  **Создайте и заполните файл `.env`:** В директории `infra/` создайте файл `.env` и заполните его своими данными (см. пример ниже).

4.  Запустите проект с помощью Docker Compose:
    ```bash
    sudo docker compose -f docker-compose.production.yml up -d
    ```
5.  Выполните миграции, соберите статику и загрузите данные:
    ```bash
    # Применить миграции
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    # Собрать статические файлы
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
    # Загрузить ингредиенты в базу данных
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
    # Загрузить теги в базу данных
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_tags
    ```
Проект будет доступен по вашему IP-адресу или доменному имени.

### Локальное развертывание проекта (без Docker)
1.  Склонируйте репозиторий на ваш компьютер:
    ```bash
    git clone https://github.com/Chashkapluy1/foodgram.git
    ```
2.  Перейдите в папку с бэкенд-кодом:
    ```bash
    cd foodgram/backend/
    ```
3.  Создайте и активируйте виртуальное окружение:
    ```bash
    # Для Windows
    python -m venv venv
    source venv/Scripts/activate

    # Для macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
5.  Примените миграции:
    ```bash
    python manage.py migrate
    ```
6.  Загрузите данные в базу:
    ```bash
    python manage.py load_ingredients
    python manage.py load_tags
    ```
7.  Создайте суперпользователя:
    ```bash
    python manage.py createsuperuser
    ```
8.  Запустите сервер для разработки:
    ```bash
    python manage.py runserver
    ```

### Заполнение файла .env
Файл `.env` должен находиться в директории `infra/` и содержать следующие переменные:

```env
# Переменные для PostgreSQL
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_strong_password

# Хост и порт для подключения Django к БД
# DB_HOST=db - это имя сервиса из docker-compose, не меняйте его для Docker-развертывания
DB_HOST=db
DB_PORT=5432

# Секретный ключ и настройки отладки Django 
# ВАЖНО: для рабочего окружения DEBUG должен быть False! 
SECRET_KEY='ваш-очень-сложный-секретный-ключ' 
DEBUG=False

# Разрешенные хосты
ALLOWED_HOSTS='foodgram10.duckdns.org,127.0.0.1,localhost'
```

### Автор
*   **Имя:** Павел Лагерев
*   **GitHub:** [Chashkapluy1](https://github.com/Chashkapluy1)
