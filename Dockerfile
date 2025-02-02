FROM python:3.12-slim

ENV POETRY_VERSION=2.0.0

WORKDIR /user_service

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false && \
    ln -s /usr/local/bin/poetry /usr/bin/poetry

COPY pyproject.toml poetry.lock /user_service/

RUN poetry install --no-root --no-interaction --no-ansi

COPY . /user_service

EXPOSE 8000

CMD ["gunicorn", "user_service.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "-w", "4"]
