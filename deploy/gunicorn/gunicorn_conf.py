import multiprocessing
import os


bind = os.getenv("GUNICORN_BIND", "127.0.0.1:8000")
worker_class = "uvicorn.workers.UvicornWorker"

# Standard production baseline:
# workers = (2 x CPU cores) + 1
cpu_count = multiprocessing.cpu_count()
workers = int(os.getenv("GUNICORN_WORKERS", (cpu_count * 2) + 1))

threads = int(os.getenv("GUNICORN_THREADS", 1))
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", 1000))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 60))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 30))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 2000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 200))

accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

proc_name = "stimuli-api"
daemon = False
preload_app = False

# Gunicorn writes the master PID here so reload scripts can signal it cleanly.
pidfile = os.getenv("GUNICORN_PID_FILE", "/run/stimuli-api/gunicorn.pid")

# Ensure the runtime directory exists before Gunicorn starts.
os.makedirs(os.path.dirname(pidfile), exist_ok=True)
