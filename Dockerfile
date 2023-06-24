FROM python:3.11-slim

RUN useradd --system --create-home --home-dir /app -s /bin/bash app
USER app
ENV PATH=$PATH:/app/.local/bin

WORKDIR /app

RUN pip install pipx==1.2.0 --user --no-cache
RUN pipx install poetry==1.5.1
RUN poetry config virtualenvs.create false

COPY [ "poetry.toml", "poetry.lock", "pyproject.toml", "./" ]

# We don't want the tests
COPY src/twittergram ./src/twittergram

RUN poetry install --only=main

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

ENTRYPOINT [ "poetry", "run", "twittergram" ]
