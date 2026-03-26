FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY apps/identity-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/identity-service /app

EXPOSE 8001

CMD ["sh", "-c", "python manage.py migrate --noinput --settings=config.settings.local && python scripts/seed_data.py && gunicorn config.wsgi:application --bind 0.0.0.0:8001 --workers 2"]
