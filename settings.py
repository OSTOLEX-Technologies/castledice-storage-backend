import os
from db_uri_builders import build_postgres

# Postgres
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

DATABASE_URL = build_postgres(postgres_user=POSTGRES_USER,
                              postgres_password=POSTGRES_PASSWORD,
                              postgres_db=POSTGRES_DB,
                              postgres_host=POSTGRES_HOST,
                              postgres_port=POSTGRES_PORT)
