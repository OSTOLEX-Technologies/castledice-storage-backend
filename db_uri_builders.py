def build_postgres(postgres_user, postgres_password, postgres_db, postgres_host, postgres_port):
    return f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
