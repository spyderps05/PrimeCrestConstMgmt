# Getting Started

Three ways to run PrimeCrest. Pick whichever fits your setup.

If a warning or an error shows up on the way, [Installation help](INSTALL_TROUBLESHOOTING.md) explains each one (also [online](https://primecrest.pk/install-help), in [Deutsch](INSTALL_TROUBLESHOOTING.de.md) and [Русский](INSTALL_TROUBLESHOOTING.ru.md)).

## Path A: Desktop App (easiest)

Download the installer for your platform:

- **[primecrest.pk/download](https://primecrest.pk/download)**
- Or grab from the [latest GitHub release](https://github.com/spyderps05/PrimeCrestConstMgmt/releases/latest): Windows `.exe`, macOS `.dmg` (Apple Silicon), Linux `.deb` / `.AppImage`

Run the installer, launch the app. First launch takes about one minute to set up the local database. No Python, no Docker, no terminal required.

On Windows the installer is not code signed yet. If Windows warns about an unknown publisher or Smart App Control blocks the app, see [Windows blocks the app](desktop/WINDOWS_BLOCKED.md).

## Path B: pip install

Requires **Python 3.12+**.

```bash
pip install --upgrade openconstructionerp
openconstructionerp
```

The package ships the FastAPI backend and a pre-built React frontend in a single wheel. On first run it sets up an embedded PostgreSQL instance, loads demo data, and opens your browser at [localhost:8080](http://localhost:8080).

**Demo login:** `demo@openconstructionerp.com` / `DemoPass1234!`

> **Running on a VPS or remote server?** The default binds to localhost only.
> To make the app reachable over the network, start it with:
>
> ```bash
> openconstructionerp serve --host 0.0.0.0
> ```
>
> For a production setup with systemd, see [INSTALL_LINUX.md](INSTALL_LINUX.md).

## Path C: Docker

Download both Compose files and start the stack:

```bash
curl -fsSL https://raw.githubusercontent.com/spyderps05/PrimeCrestConstMgmt/main/docker-compose.quickstart.yml       -o docker-compose.yml
curl -fsSL https://raw.githubusercontent.com/spyderps05/PrimeCrestConstMgmt/main/docker-compose.quickstart.image.yml -o docker-compose.override.yml
echo "POSTGRES_PASSWORD=$(openssl rand -base64 24)" >  .env
echo "JWT_SECRET=$(openssl rand -hex 32)"           >> .env
docker compose pull app
docker compose up -d
```

On Windows, run the same steps in PowerShell. Use `curl.exe`, because `curl` in Windows PowerShell is a different command, and write `.env` with `Set-Content -Encoding ascii`, because a plain `>` writes UTF-16, which Compose cannot read:

```powershell
curl.exe -fsSL https://raw.githubusercontent.com/spyderps05/PrimeCrestConstMgmt/main/docker-compose.quickstart.yml -o docker-compose.yml
curl.exe -fsSL https://raw.githubusercontent.com/spyderps05/PrimeCrestConstMgmt/main/docker-compose.quickstart.image.yml -o docker-compose.override.yml
$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
$pw = New-Object byte[] 24; $rng.GetBytes($pw)
$jwt = New-Object byte[] 32; $rng.GetBytes($jwt)
Set-Content -Path .env -Encoding ascii -Value "POSTGRES_PASSWORD=$([Convert]::ToBase64String($pw))", "JWT_SECRET=$(-join ($jwt | ForEach-Object { $_.ToString('x2') }))"
docker compose pull app
docker compose up -d
```

The app runs at [localhost:8080](http://localhost:8080).

**Demo login:** `demo@openconstructionerp.com` / `DemoPass1234!`

## Prerequisites

| Path | Requirement |
|------|-------------|
| Desktop | None |
| pip | Python 3.12+ |
| Docker | Docker with Compose v2 |
| Source development | Python 3.12+, Node.js 22+, PostgreSQL 16+ |

For building from source, running tests, or contributing, see [DEVELOPING.md](../DEVELOPING.md).
