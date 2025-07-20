FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    build-essential \
    openjdk-17-jdk \
    maven \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_HOME="/opt/poetry" \
    JAVA_HOME="/usr/lib/jvm/java-17-openjdk-arm64" \
    MAVEN_HOME="/usr/share/maven"

RUN pip install poetry==1.8

RUN export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-arm64"

ENV PATH="$POETRY_HOME/bin:$JAVA_HOME/bin:$MAVEN_HOME/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml
COPY ./scripts/kafka_streams_app /app/kafka_streams_app


WORKDIR /app/kafka_streams_app
RUN mvn clean package -DskipTests

WORKDIR /app

RUN poetry install