FROM python:3.11-slim as python-base

#Уст рабочего окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Уст Poetry
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    && curl -sSL https://install.python-poetry.org | python - \
    && apt-get purge -y --auto-remove curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Копируем Poetry конфиги
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Уст зависимостей
RUN poetry install --without dev --no-root

COPY . /app/
WORKDIR /app

# Запуск
CMD ["python", "manage.py", "runserver", "0.0.0.0:8008"]