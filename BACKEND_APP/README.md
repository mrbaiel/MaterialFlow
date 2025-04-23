cd backend
poetry install   # Установка зависимостей
poetry shell     # Активация виртуального окружения
python manage.py migrate  # Применение миграций
python manage.py runserver  # Запуск сервера разработки