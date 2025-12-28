# BookWise

Данный проект является учебным.\
Используемые  технологии:
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- MinIO
- Grafana
- Prometheus
- Docker

## Запуск проекта

### Требования:
- Установлен Docker
- Установлен Docker Compose

### Шаги запуска:
1. Склонируйте репозиторий
2. Создайте файл окружения .env на основе примера .env.example
3. Откройте .env и заполните значения
4. Соберите и запустите все сервисы

## Сервисы

- Grafana: ```http://localhost:3000``` (Логин/пароль по умолчанию admin/admin)
- Prometheus: ```http://localhost:9090```
- Приложение: ```http://localhost:<APP_PORT>``` (порт берётся из .env)

