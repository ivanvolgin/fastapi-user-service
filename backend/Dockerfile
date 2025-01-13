FROM python

ENV POETRY_VERSION=2.0.0

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false

COPY ./app/pyproject.toml ./app/poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "-w", "4"]
