# Инфраструктура проекта ВКР

## Запуск

```bash

# 0. Переход в рабочую директорию
cd ./infra/

# 1. Скопировать .env.example → .env и заполнить
cp .env.example .env

# 2. Запустить
docker compose up -d --build

# 3. Проверка

# Статус контейнеров
docker compose ps
# Все должны быть Up (auth, topic, nginx, postgres)

# Health-check сервисов
curl http://localhost/auth/health
curl http://localhost/topic/health
# Должно вернуть {"status":"ok","service":"auth"} и аналогично для topic

# Подключение к БД (через psql)
docker compose exec postgres psql -U postgres -d vkr_main -c "\dt"
# Должна быть хотя бы таблица alembic_version

# Alembic работает
docker compose exec auth-service alembic -c /app/alembic.ini current
# Должен быть вывод без ошибок (хотя бы INFO о контексте)