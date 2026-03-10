# Docker + Cloudflare Quick Tunnel

## 1. Prepare env

Create a `.env.docker` file from `.env.docker.example` and fill secrets.

On Windows, ensure Docker Desktop is installed and running before continuing.

## 2. Build and run containers

```powershell
docker compose --env-file .env.docker up -d --build
```

Check status:

```powershell
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

App entry:
- Frontend: `http://localhost/`
- API health: `http://localhost/api/health`

## 3. Start Cloudflare Quick Tunnel

Install `cloudflared` on Windows:

```powershell
winget install Cloudflare.cloudflared
```

Start Quick Tunnel to the frontend container entry:

```powershell
cloudflared tunnel --url http://localhost:80
```

It will output a URL like:
- `https://xxxx-xxxx-xxxx.trycloudflare.com`

Share this URL with external users.

## 4. Troubleshooting

- If frontend works but API fails, verify reverse proxy route:
  - `curl http://localhost/api/health`
- If tunnel command fails, ensure port 80 is serving:
  - `docker compose ps`
- If `docker compose` cannot connect to `dockerDesktopLinuxEngine`, start Docker Desktop and wait until it reports the engine is running.
- If browser sees stale JS, hard refresh (`Ctrl+F5`).

## 5. Stop

```powershell
docker compose down
```

To also remove DB volume:

```powershell
docker compose down -v
```
