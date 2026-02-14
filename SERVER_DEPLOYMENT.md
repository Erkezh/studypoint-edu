# StudyPoint Server Deployment

This guide deploys the project from Git with these runtime ports:
- Backend API: `127.0.0.1:8001`
- Frontend: `127.0.0.1:5174`
- Public entrypoint: Nginx on `:80` (and optional `:443`)

## 1. Install prerequisites (Ubuntu)

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release nginx nodejs npm
```

Install Docker + Compose plugin (official docs are recommended for latest steps), then verify:

```bash
docker --version
docker compose version
node -v
npm -v
nginx -v
```

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
VITE_API_URL=http://127.0.0.1:8001
ENV
npm run build-only
nohup npm run preview -- --host 0.0.0.0 --port 5174 >/tmp/studypoint-frontend.log 2>&1 &
```

Rebuild/restart preview whenever `.env` changes.
This guide uses `npm run build-only` (without `vue-tsc`) to avoid blocking deploy on current TS typing issues.

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

Copy provided config:

```bash
sudo cp /opt/studypoint-edu/deploy/nginx/studypoint.conf /etc/nginx/sites-available/studypoint
sudo ln -sf /etc/nginx/sites-available/studypoint /etc/nginx/sites-enabled/studypoint
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

Now open:
- `http://<server-ip-or-domain>/` -> frontend (`5174`)
- `http://<server-ip-or-domain>/api/v1/...` -> backend (`8001`)
- `http://<server-ip-or-domain>/docs` -> backend Swagger

## 7. Optional: enable HTTPS (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 8. Update flow after `git pull`

```bash
cd /opt/studypoint-edu
git pull

# frontend
npm ci
npm run build-only
pkill -f "vite preview" || true
nohup npm run preview -- --host 0.0.0.0 --port 5174 >/tmp/studypoint-frontend.log 2>&1 &

# backend
cd /opt/studypoint-edu/backend
docker compose up -d --build
docker compose exec api alembic upgrade head
```
