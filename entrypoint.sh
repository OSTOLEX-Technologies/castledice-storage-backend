#!/bin/sh

if [ "$MODE" = "DEV" ] && [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python alembic upgrade head

if [ "$MODE" = "PRODUCTION" ] || [ "$MODE" = "STAGING" ]
then
  echo "Running production server"
  uvicorn --port 8000 --host 0.0.0.0 --workers 5 main:app
fi

exec "$@"
