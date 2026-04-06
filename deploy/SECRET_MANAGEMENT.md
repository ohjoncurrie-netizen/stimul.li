# Secret Management on a VPS

## Findings from the current setup

1. Real `.env` files were not protected by a repo-level `.gitignore`.
2. Real `.env` files were not excluded from the Docker build context.
3. The app startup path did not validate critical secrets before running migrations and starting the API.

These have now been addressed with:

- `.gitignore`
- `.dockerignore`
- `scripts/validate_env.py`
- `scripts/start.sh` validation before `alembic upgrade head`

## Recommended `.env` handling on a VPS

Store the real environment file on the server only, with restricted permissions:

```bash
cd /opt/stimuli-api
cp .env.production.example .env
chown stimuli:stimuli .env
chmod 600 .env
```

Edit it with your real values:

```bash
sudo -u stimuli nano /opt/stimuli-api/.env
```

Never commit `.env` to Git. Only commit templates like:

- `.env.production.example`

## Verify ignore rules

These files now prevent accidental secret leaks:

- `.gitignore`
- `.dockerignore`

That means:

- `.env` stays out of Git
- `.env` stays out of the Docker image build context

## Manual validation before start

You can validate secrets directly:

```bash
cd /opt/stimuli-api
python scripts/validate_env.py
```

## What the validator checks

- `OPENAI_API_KEY` exists and looks like an OpenAI secret key
- `STRIPE_API_KEY` exists and looks like a Stripe secret key
- `DATABASE_URL` exists and looks like a PostgreSQL SQLAlchemy URL

## Automatic startup validation

Container startup now runs:

```sh
python /app/scripts/validate_env.py
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If required secrets are missing or malformed, the app exits before serving traffic.
