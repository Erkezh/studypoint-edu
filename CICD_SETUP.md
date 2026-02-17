# CI/CD Setup (GitHub Actions -> Production Server)

Workflow file:
`/.github/workflows/deploy-production.yml`

It runs on every push to `main` and does:
- frontend build check in GitHub Actions
- SSH deploy to server
- backend `docker compose up -d --build` + migrations
- frontend rebuild + restart
- health checks

## 1. One-time server preparation

### 1.1 Ensure fixed frontend port

If you use `studypoint-frontend.service`, keep strict port:

```ini
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 5174 --strictPort
```

### 1.2 Allow passwordless sudo for deploy user

Edit sudoers safely:

```bash
sudo visudo -f /etc/sudoers.d/studypoint-deploy
```

Add:

```text
studypoint ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/systemctl
```

Validate:

```bash
sudo -l -U studypoint
```

## 2. SSH key for GitHub Actions

On your local machine:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/studypoint_actions
```

Add public key to server:

```bash
cat ~/.ssh/studypoint_actions.pub
```

Copy output and append on server to:

```bash
/home/studypoint/.ssh/authorized_keys
```

Fix permissions on server:

```bash
chmod 700 /home/studypoint/.ssh
chmod 600 /home/studypoint/.ssh/authorized_keys
chown -R studypoint:studypoint /home/studypoint/.ssh
```

## 3. GitHub repository secrets

In GitHub -> `Settings` -> `Secrets and variables` -> `Actions`, add:

- `DEPLOY_SSH_HOST` = server IP/host
- `DEPLOY_SSH_PORT` = `22`
- `DEPLOY_SSH_USER` = `studypoint`
- `DEPLOY_SSH_PRIVATE_KEY` = full content of `~/.ssh/studypoint_actions` (private key)
- `DEPLOY_PATH` = `/opt/studypoint-edu` (optional; defaults to this path)
- `DEPLOY_DOMAIN` = `edu.studypoint.kz` (optional; used for final HTTPS check)

## 4. First run

Push to main:

```bash
git checkout main
git add .github/workflows/deploy-production.yml CICD_SETUP.md SERVER_DEPLOYMENT.md
git commit -m "Setup production CI/CD deploy workflow"
git push origin main
```

Then monitor:
- GitHub -> `Actions` -> `Deploy Production`

## 5. Manual trigger

You can run deploy without a new commit:
- GitHub -> `Actions` -> `Deploy Production` -> `Run workflow`

## 6. Notes

- Workflow expects branch name `main`.
- If deploy fails at `sudo -n true`, fix sudoers first.
- If `studypoint-frontend.service` is absent, workflow falls back to restarting `vite preview` via `nohup`.
