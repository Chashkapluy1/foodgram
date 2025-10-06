### Foodgram: Платформа для обмена рецептами
![Foodgram CI/CD](https://github.com/Chashkapluy1/foodgram/actions/workflows/main.yml/badge.svg)

**Фудграм** — это учебный проект, представляющий собой API для платформы, где пользователи могут публиковать свои кулинарные рецепты, подписываться на других авторов, а также добавлять рецепты в избранное и список покупок.

Проект упакован в Docker-контейнеры и разворачивается на удаленном сервере с помощью CI/CD на базе GitHub Actions.

### Стек технологий
*   **Backend:** Python 3.12, Django, Django REST Framework
*   **Frontend:** React.js
*   **База данных:** PostgreSQL
*   **Веб-сервер:** Nginx
*   **Контейнеризация:** Docker, Docker Compose
*   **CI/CD:** GitHub Actions

### Как развернуть проект
1.  Склонируйте репозиторий на ваш сервер:
    ```bash
    git clone https://github.com/Chashkapluy1/foodgram.git
    ```
2.  Перейдите в папку с файлами инфраструктуры:
    ```bash
    cd foodgram/infra/
    ```
3.  **Создайте и заполните файл `.env`:** В директории `infra/` создайте файл `.env` и заполните его своими данными (см. пример ниже).

4.  Запустите проект с помощью Docker Compose:
    ```bash
    sudo docker compose up -d
    ```
5.  Выполните миграции, соберите статику и загрузите ингредиенты:
    ```bash
    # Применить миграции
    sudo docker compose exec backend python manage.py migrate
    # Собрать статические файлы
    sudo docker compose exec backend python manage.py collectstatic --no-input
    # Загрузить ингредиенты в базу данных
    sudo docker compose exec backend python manage.py load_ingredients
    ```
Проект будет доступен по вашему IP-адресу или доменному имени.

### Заполнение файла .env
Файл `.env` должен находиться в директории `infra/` и содержать следующие переменные:

```env
# Переменные для PostgreSQL (имя БД, пользователь и пароль)
POSTGRES_DB=foodgram_db
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password

# Переменные для подключения Django к БД
# Обратите внимание: DB_HOST=db - это имя сервиса из docker-compose.yml
DB_NAME=foodgram_db
DB_USER=foodgram_user
DB_PASSWORD=foodgram_password
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