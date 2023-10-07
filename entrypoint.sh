#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 80
exec "$@"
