# Alembic Migrations

This project uses Alembic to manage schema changes without dropping user data.

## Files

- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/`

## Auto-generate a migration

After changing the SQLAlchemy models in `app/db/models.py`:

```bash
cd /root/stimuli-api
alembic revision --autogenerate -m "describe the schema change"
```

Review the generated migration before applying it.

## Apply migrations

```bash
cd /root/stimuli-api
alembic upgrade head
```

## Docker startup behavior

The container entrypoint is `scripts/start.sh`, which runs:

```sh
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

That means every container start attempts to bring the database schema to the latest migration before the API begins serving traffic.

## Operational note

Running migrations automatically at startup is practical for a single API replica or tightly controlled deploys. If you later run multiple replicas, move migrations into a dedicated one-shot release job so parallel containers do not race during startup.
