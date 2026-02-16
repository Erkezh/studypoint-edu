# StudyPoint Server Deployment

This guide deploys the project from Git with these runtime ports:
- Backend API: `127.0.0.1:8001`
- Frontend: `127.0.0.1:5174`
- Edge entrypoint: shared-domain vhost on `:80/:443` or dedicated upstream proxy port `127.0.0.1:8088`

## 1. Install prerequisites (Ubuntu)

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release nginx
```

Install Node.js 22.x (recommended, required by current Vite/Vue toolchain):

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

Install Docker + Compose plugin (official docs are recommended for latest steps), then verify versions:

```bash
docker --version
docker compose version
node -v
npm -v
nginx -v
```

Node must be `>=22.12.0` (or `20.19.x`). Older versions can fail with:
`[vite:vue] crypto.hash is not a function`.

## 2. Clone project

```bash
cd /opt
sudo git clone <YOUR_GIT_URL> studypoint-edu
sudo chown -R $USER:$USER /opt/studypoint-edu
cd /opt/studypoint-edu
```

## 3. Configure backend env

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set production values at minimum:
- `JWT_SECRET_KEY`
- `POSTGRES_PASSWORD`
- any other secret values you use

Note: Docker Compose now forces internal Docker DNS for DB/Redis (`postgres`, `redis`), so backend startup is safe even if local `localhost` URLs exist in your `.env`.

## 4. Start backend (Docker)

```bash
cd /opt/studypoint-edu/backend
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.seed
```

Check logs:

```bash
docker compose logs -f api
```

API docs should be available at: `http://127.0.0.1:8001/docs`

Optional (recommended) boot-time startup for backend stack:

```bash
sudo tee /etc/systemd/system/studypoint-backend.service >/dev/null <<'UNIT'
[Unit]
Description=StudyPoint Backend Docker Compose
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/studypoint-edu/backend
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now studypoint-backend
sudo systemctl status studypoint-backend
```

## 5. Build and run frontend on 5174

```bash
cd /opt/studypoint-edu
npm ci
cat > /opt/studypoint-edu/.env <<'ENV'
# Keep empty in production to use same-origin proxy (/api via Nginx/NPM gateway)
VITE_API_URL=
ENV
npm run build-only
nohup npm run preview -- --host 0.0.0.0 --port 5174 >/tmp/studypoint-frontend.log 2>&1 &
```

Rebuild/restart preview whenever `.env` changes.
This guide uses `npm run build-only` (without `vue-tsc`) to avoid blocking deploy on current TS typing issues.
Do not set `VITE_API_URL` to `127.0.0.1` or `localhost` in production browser builds.

If install/build fails due Node version:
```bash
node -v
npm run check:node
```

Optional (recommended) process manager with `systemd`:

```bash
sudo tee /etc/systemd/system/studypoint-frontend.service >/dev/null <<'UNIT'
[Unit]
Description=StudyPoint Frontend (Vite Preview)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/studypoint-edu
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 5174
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now studypoint-frontend
sudo systemctl status studypoint-frontend
```

## 6. Configure Nginx reverse proxy

Use one mode that matches your environment.

0) You already use Nginx Proxy Manager (NPM) on `80/443`

If NPM is already serving other projects, do **not** add another host-level Nginx site on `:80/:443`.
Use an internal gateway container and proxy only this new domain to it.

Add this service to your existing NPM `docker-compose.yml`:

```yaml
  studypoint-gateway:
    image: nginx:1.27-alpine
    container_name: studypoint-gateway
    restart: unless-stopped
    volumes:
      - /studypoint-edu/studypoint-edu/deploy/nginx/studypoint-gateway.conf:/etc/nginx/conf.d/default.conf:ro
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - nginx
```

Then apply safely:

```bash
cd /path/to/your/npm-compose
docker compose up -d studypoint-gateway
```

In NPM UI, create a new Proxy Host for your new domain:
- `Forward Hostname / IP`: `studypoint-gateway`
- `Forward Port`: `8080`
- `Scheme`: `http`
- `Websockets Support`: enabled

This will not affect existing proxy hosts/domains.
If frontend gives `403` while backend works, your old gateway config is still mounted.
Update `studypoint-gateway.conf` to set `proxy_set_header Host 127.0.0.1;` in `location /`, then recreate `studypoint-gateway`.

1) Shared Nginx with a new domain (recommended)

```bash
sudo cp /opt/studypoint-edu/deploy/nginx/studypoint.conf /etc/nginx/sites-available/studypoint
sudo ln -sf /etc/nginx/sites-available/studypoint /etc/nginx/sites-enabled/studypoint
sudo nginx -t
sudo systemctl reload nginx
```

Edit `/etc/nginx/sites-available/studypoint` and replace `server_name` with your real domain.

Now open with that domain:
- `http://<server-ip-or-domain>/` -> frontend (`5174`)
- `http://<server-ip-or-domain>/api/v1/...` -> backend (`8001`)
- `http://<server-ip-or-domain>/docs` -> backend Swagger

2) Dedicated upstream port (for another proxy/domain gateway)

```bash
sudo cp /opt/studypoint-edu/deploy/nginx/studypoint-proxy-port.conf /etc/nginx/sites-available/studypoint-proxy-port
sudo ln -sf /etc/nginx/sites-available/studypoint-proxy-port /etc/nginx/sites-enabled/studypoint-proxy-port
sudo nginx -t
sudo systemctl reload nginx
```

Then, in your outer proxy/domain panel, forward your new domain to:
- `http://127.0.0.1:8088` (same server), or
- `http://<server-private-ip>:8088` (if proxy is on another machine)

Use full-host proxying (all paths) and keep/preserve the `Host` header.

## 7. Optional: enable HTTPS (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 8. Update flow after `git pull`

```bash
cd /studypoint-edu/studypoint-edu
git pull

# frontend
npm ci
cat > /studypoint-edu/studypoint-edu/.env <<'ENV'
VITE_API_URL=
ENV
npm run build-only
sudo systemctl restart studypoint-frontend

# backend
cd /studypoint-edu/studypoint-edu/backend
sudo docker compose up -d --build
sudo docker compose run --rm api alembic upgrade head
```

## 9. Optional CI/CD (GitHub Actions)

Use:
- `/Users/nursat/Desktop/Projects/studypoint_edu/studypoint-edu/.github/workflows/deploy-production.yml`
- `/Users/nursat/Desktop/Projects/studypoint_edu/studypoint-edu/CICD_SETUP.md`

After setup, every push to `main` will auto-deploy backend + frontend.
