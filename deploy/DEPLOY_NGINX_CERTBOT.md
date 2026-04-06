# Ubuntu Nginx + Certbot Deployment

This layout assumes:

- FastAPI is listening on `127.0.0.1:8000`
- DNS for `api.stimul.li` already points to the VPS public IP
- Ubuntu with `nginx` and `certbot` installed

## Files

- Global Nginx config: `deploy/nginx/nginx.conf`
- Production site config: `deploy/nginx/api.stimul.li.conf`
- Temporary HTTP-only bootstrap config: `deploy/nginx/certbot-bootstrap.stimul.li.conf`

## 1. Prepare directories

```bash
sudo mkdir -p /var/www/certbot
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled
```

## 2. Install the global Nginx config

Back up the Ubuntu default first:

```bash
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak.$(date +%F-%H%M%S)
sudo cp /root/stimuli-api/deploy/nginx/nginx.conf /etc/nginx/nginx.conf
```

## 3. Bootstrap Certbot over HTTP

Use the temporary config before certificates exist:

```bash
sudo cp /root/stimuli-api/deploy/nginx/certbot-bootstrap.stimul.li.conf /etc/nginx/sites-available/api.stimul.li.conf
sudo ln -sfn /etc/nginx/sites-available/api.stimul.li.conf /etc/nginx/sites-enabled/api.stimul.li.conf
sudo nginx -t
sudo systemctl reload nginx
```

Verify:

```bash
curl http://api.stimul.li/.well-known/acme-challenge/test
curl http://api.stimul.li/
```

The second command should return `certbot bootstrap ready`.

## 4. Issue the Let's Encrypt certificate

If `certbot` is not installed:

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

Request the certificate:

```bash
sudo certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d api.stimul.li \
  --email admin@stimul.li \
  --agree-tos \
  --no-eff-email
```

## 5. Enable the production TLS site config

```bash
sudo cp /root/stimuli-api/deploy/nginx/api.stimul.li.conf /etc/nginx/sites-available/api.stimul.li.conf
sudo ln -sfn /etc/nginx/sites-available/api.stimul.li.conf /etc/nginx/sites-enabled/api.stimul.li.conf
sudo nginx -t
sudo systemctl reload nginx
```

## 6. Validate the deployed site

```bash
curl -I http://api.stimul.li
curl -I https://api.stimul.li
```

Expected:

- HTTP redirects to HTTPS
- HTTPS responds with valid certificate and security headers

## 7. Enable renewal

Check the systemd timer:

```bash
systemctl list-timers | grep certbot
```

Test renewal:

```bash
sudo certbot renew --dry-run
```

## Operational notes

- The Nginx request-size limit is `1m` via `client_max_body_size`.
- The Nginx DDoS guard is `20r/s` with `burst=40`.
- HSTS is enabled with preload semantics. Only use that once you are committed to HTTPS for the domain.
- The API upstream is `127.0.0.1:8000`; keep FastAPI bound to localhost instead of a public interface.
