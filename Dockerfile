FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry==1.2.2 --no-cache
RUN poetry config virtualenvs.create false

COPY [ "poetry.toml", "poetry.lock", "pyproject.toml", "./" ]

# We don't want the tests
COPY src/twittergram ./src/twittergram

RUN poetry install --no-dev

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

ENTRYPOINT [ "python", "-m", "twittergram" ]
