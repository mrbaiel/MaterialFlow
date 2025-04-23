# Система учёта строительных материалов

## Описание проекта

Веб-приложение для автоматизации учёта строительных материалов на предприятии по производству пескоблоков. Система позволяет вести учёт поставок сырья, производства различных типов пескоблоков, формирования заказов, расчёт заработной платы сотрудников и аналитику продаж и производства.

## ️ Технологический стек

### Бэкенд

- Python 3.9+
- Django 4.2+
- Django REST Framework
- PostgreSQL
- Poetry (управление зависимостями)
- JWT (аутентификация)
- Pandas (обработка данных)
- python-telegram-bot

### Фронтенд

- React 18+
- Redux (управление состоянием)
- Material UI / Ant Design
- Axios
- Recharts (визуализация данных)

### Инфраструктура

- Docker & Docker Compose
- Git

## Основная функциональность

- Учёт поставок сырья (песок, щебень, цемент)
- Учёт ежедневного производства пескоблоков разных типов
- Управление заказами и дополнительными закупками
- Автоматический расчёт заработной платы работников
- Экспорт данных в Excel/CSV
- Базовая аналитика и прогнозирование объёмов
- Telegram-бот для быстрого добавления данных

## Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Git

### Шаги по установке

1. Клонировать репозиторий:

   ```bash
   git clone https://github.com/your-username/building_materials_management.git
   cd building_materials_management

   ```

2. Создать файл .env в корне проекта и заполнить необходимые переменные окружения:

   # Django settings

   DEBUG=True
   SECRET_KEY=your_mysterios_django_secret_key
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database settings

   DB_NAME=emir
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432

3. Запустить проект с помощью Docker Compose:

   ```
   docker-compose up --build
   ```

4. Приложение будет доступно:

   Бэкенд: http://localhost:8000/api/
   Фронтенд: http://localhost:3000/
   API документация: http://localhost:8000/api/docs/

## Структура проекта

    ├── backend/          # Django проект

│ ├── apps/ # Django приложения
│ │ ├── users/ # Пользователи и аутентификация
│ │ ├── materials/ # Учёт материалов
│ │ ├── production/ # Производство пескоблоков
│ │ ├── orders/ # Заказы
│ │ ├── employees/ # Работники
│ │ └── analytics/ # Аналитика и отчёты
│ ├── backend/ # Настройки проекта
│ └── telegram_bot/ # Интеграция с Telegram
├── frontend/ # React приложение
│ ├── public/
│ └── src/
│ ├── components/ # React компоненты
│ ├── pages/ # Страницы приложения
│ ├── services/ # API-клиенты
│ └── store/ # Redux хранилище
├── docker-compose.yml # Настройки Docker
