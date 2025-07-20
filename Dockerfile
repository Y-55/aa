FROM python:3.11-slim

RUN apt-get update
RUN apt-get install curl gcc build-essential -y

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_HOME="/opt/poetry"

RUN pip install poetry==1.8

ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml

RUN poetry install

