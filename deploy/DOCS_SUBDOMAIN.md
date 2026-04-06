# Hosting API Docs on `docs.stimul.li`

This project exposes branded docs at:

- `/docs` for Swagger UI
- `/reference` for ReDoc
- `/openapi.json` for the raw schema

## Recommended approach

Keep the API app running on `127.0.0.1:8000` and publish the docs through a dedicated Nginx vhost:

- `api.stimul.li` -> normal API traffic
- `docs.stimul.li` -> proxied docs and OpenAPI schema

This avoids mixing your public API hostname with your developer-facing documentation hostname.

## Example Nginx site for `docs.stimul.li`

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name docs.stimul.li;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name docs.stimul.li;

    ssl_certificate /etc/letsencrypt/live/docs.stimul.li/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docs.stimul.li/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/docs.stimul.li/chain.pem;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    location = / {
        return 302 /docs;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /reference {
        proxy_pass http://127.0.0.1:8000/reference;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        root /var/www/stimuli-docs;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }
}
```

## DNS and TLS

1. Create an `A` or `AAAA` record for `docs.stimul.li` pointing to the VPS.
2. Issue a separate Let's Encrypt certificate:

```bash
sudo certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d docs.stimul.li \
  --email admin@stimul.li \
  --agree-tos \
  --no-eff-email
```

## Logo hosting

The FastAPI metadata currently references:

`https://docs.stimul.li/static/stimuli-logo.png`

Host that asset on the VPS, for example:

```bash
sudo mkdir -p /var/www/stimuli-docs/static
sudo cp /path/to/stimuli-logo.png /var/www/stimuli-docs/static/stimuli-logo.png
```

## Operational note

If you want docs to be public but the API to stay partially private, keep `docs.stimul.li` public and restrict sensitive API routes separately with auth and firewall policy. The docs subdomain only changes presentation, not authorization.
