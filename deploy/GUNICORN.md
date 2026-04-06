# Gunicorn + UvicornWorker for FastAPI

This deployment mode is intended for multi-core VPS instances where you want:

- one Gunicorn master process;
- multiple worker processes spread across CPU cores;
- ASGI support for FastAPI's async request handling.

## Why `UvicornWorker`

FastAPI is an ASGI application. Gunicorn by itself is only a process manager and does not speak ASGI natively. `uvicorn.workers.UvicornWorker` bridges that gap:

- Gunicorn manages the worker lifecycle, signals, reloads, and process supervision.
- UvicornWorker runs your FastAPI app inside an ASGI server capable of handling asynchronous I/O professionally.
- This lets the app serve many concurrent requests efficiently, especially for I/O-bound workloads such as API calls, DB operations, Redis access, and external AI provider calls.

## Worker sizing

`deploy/gunicorn/gunicorn_conf.py` computes:

```python
workers = (2 * CPU cores) + 1
```

That is a standard baseline for multi-core Linux servers. For example:

- 2 cores -> 5 workers
- 4 cores -> 9 workers
- 8 cores -> 17 workers

Override with environment variables if needed:

```bash
GUNICORN_WORKERS=8
GUNICORN_TIMEOUT=90
GUNICORN_KEEPALIVE=5
```

## Start command

```bash
gunicorn -c /opt/stimuli-api/deploy/gunicorn/gunicorn_conf.py app.main:app
```

## Graceful reloads

Gunicorn supports zero-downtime style reload signaling for config or code refreshes.

The included script:

`deploy/gunicorn/reload_gunicorn.sh`

sends `HUP` to the Gunicorn master PID from the PID file:

```bash
/opt/stimuli-api/deploy/gunicorn/reload_gunicorn.sh
```

Or directly:

```bash
kill -HUP "$(cat /run/stimuli-api/gunicorn.pid)"
```

`HUP` tells Gunicorn to reload configuration and gracefully restart workers. Existing requests are allowed to finish instead of being cut off immediately.

## systemd

Use:

`deploy/systemd/stimuli-api-gunicorn.service`

This unit includes:

- Gunicorn with `UvicornWorker`
- `ExecReload=/bin/kill -HUP $MAINPID`
- runtime directory support for the PID file

## Recommendation

For a production FastAPI service on a VPS:

- Nginx handles TLS, buffering, and public ingress
- Gunicorn manages worker processes
- `UvicornWorker` handles async ASGI traffic

That is the standard professional stack for a high-concurrency Python API behind a reverse proxy.
