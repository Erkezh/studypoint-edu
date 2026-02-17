# CI/CD Setup (GitHub Actions -> Production Server)

Workflow file:
`/.github/workflows/deploy-production.yml`

It runs on every push to `main` and does:
- frontend build check in GitHub Actions
- if actor is not `Nur1sat`, waits for manual approval from `Nur1sat`
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

If you do not want passwordless sudo, the deploy user must at least be able to run:
- `docker compose` without sudo (for example via `docker` group)

Without sudo, workflow will skip `systemctl restart` for `studypoint-frontend` / `studypoint-backend`.

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
- `DEPLOY_SSH_PORT` = `22` (optional; defaults to `22` if empty)
- `DEPLOY_SSH_USER` = `studypoint`
- `DEPLOY_SSH_PRIVATE_KEY` = full content of `~/.ssh/studypoint_actions` (private key), OR use password secret below
- `DEPLOY_SSH_PASSWORD` = SSH password (optional fallback if key auth is not configured)
- `DEPLOY_PATH` = `/opt/studypoint-edu` (optional; if empty workflow also tries `/studypoint-edu/studypoint-edu` and `$HOME/studypoint-edu`)
- `DEPLOY_DOMAIN` = `edu.studypoint.kz` (optional; used for final HTTPS check)

Auth mode rule:
- if `DEPLOY_SSH_PASSWORD` is set, workflow uses password auth
- if `DEPLOY_SSH_PASSWORD` is empty, workflow uses private key auth

Sudo rule:
- workflow first tries passwordless sudo (`sudo -n`)
- if unavailable and `DEPLOY_SSH_PASSWORD` is set, it uses `sudo -S` with that password
- if sudo still unavailable, workflow falls back to non-sudo mode (Docker/systemctl may fail depending on server permissions)

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
- Deploy policy:
  - pushes/workflow runs started by `Nur1sat` deploy automatically
  - runs started by any other user pause and create an approval issue; `Nur1sat` must comment `approve` to continue
