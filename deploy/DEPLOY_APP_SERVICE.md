# App Service Deployment

This project now includes both deployment styles:

- `systemd` for a Python virtualenv-based install
- Docker Compose for containerized production

Choose one. Do not run both on the same port.

## Option 1: systemd service

Use this when you want the API process managed directly by Ubuntu.

### 1. Prepare the app directory

```bash
sudo mkdir -p /opt/stimuli-api
sudo rsync -av --delete /root/stimuli-api/ /opt/stimuli-api/
sudo chown -R stimuli:stimuli /opt/stimuli-api
```

### 2. Create a virtualenv and install dependencies

```bash
cd /opt/stimuli-api
sudo -u stimuli python3 -m venv .venv
sudo -u stimuli /opt/stimuli-api/.venv/bin/pip install --upgrade pip
sudo -u stimuli /opt/stimuli-api/.venv/bin/pip install -r /opt/stimuli-api/requirements.txt
```

### 3. Install the environment file

```bash
sudo cp /opt/stimuli-api/.env.production.example /opt/stimuli-api/.env
sudo chown stimuli:stimuli /opt/stimuli-api/.env
sudo chmod 600 /opt/stimuli-api/.env
```

Edit `/opt/stimuli-api/.env` with real secrets before starting the service.

### 4. Install the unit

```bash
sudo cp /opt/stimuli-api/deploy/systemd/stimuli-api.service /etc/systemd/system/stimuli-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now stimuli-api
```

### 5. Verify

```bash
systemctl status stimuli-api
journalctl -u stimuli-api -n 100 --no-pager
curl http://127.0.0.1:8000/health
```

## Option 2: Docker Compose production

Use this when you want the API, Postgres, and Redis managed as containers.

### 1. Install the environment file

```bash
cd /root/stimuli-api
cp .env.production.example .env
chmod 600 .env
```

Edit `.env` with real secrets.

### 2. Start the stack

```bash
cd /root/stimuli-api
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 3. Verify

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs api --tail=100
curl http://127.0.0.1:8000/health
```

## Nginx integration

For either option, keep Nginx proxying to:

- `127.0.0.1:8000`

If you use Docker, do not publish port `8000` publicly through a firewall rule. Let Nginx be the only public entrypoint.
