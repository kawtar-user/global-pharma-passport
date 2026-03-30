FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY db /app/db
COPY start.sh /app/start.sh

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    chmod +x /app/start.sh

EXPOSE 8000

ENTRYPOINT ["/app/start.sh"]
