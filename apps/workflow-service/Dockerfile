FROM python:3.12.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY apps/workflow-service/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY apps/workflow-service /app
COPY libs /workspace/libs

EXPOSE 8003

CMD ["sh", "-c", "python manage.py ensure_db_schema --settings=config.settings.local && python manage.py migrate --noinput --settings=config.settings.local && python manage.py runserver 0.0.0.0:8003 --settings=config.settings.local"]
