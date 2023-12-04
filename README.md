# castledice-storage-backend

## Create alembic migration (for sqlite)
```bash
make message="migration message" create-migrations-sqlite
```

## Run alembic migration (for sqlite)
```bash
make alembic-upgrade-sqlite
```