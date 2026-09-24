# AI Industry News Daily — Systemd Automation

This directory contains production-ready systemd service and timer units for 24/7 backend API hosting and autonomous daily editorial generation.

## Files

- **`ainews-backend.service`**: Managed Uvicorn ASGI daemon running the FastAPI backend on `:8000` with `Restart=always` for continuous uptime and auto-recovery.
- **`ainews-editorial.service`**: Oneshot unit that executes the 6-agent autonomous pipeline with `--live --publish` inside the project virtual environment, strictly requiring `ainews-backend.service` to be healthy before starting.
- **`ainews-editorial.timer`**: Daily timer configured for `06:00:00` local time with `Persistent=true` (ensures missed runs execute immediately upon wake if the system was powered off or asleep).
- **`install.sh`**: Helper script that copies unit files to `/etc/systemd/system/`, configures permissions, reloads systemd, and starts both the backend service and editorial timer.
- **`uninstall.sh`**: Helper script that stops, disables, and removes all units from `/etc/systemd/system/`.

---

## Installation

Run the installation script with `sudo`:

```bash
sudo ./systemd/install.sh
```

---

## Verification & Monitoring

### Check Backend Status
To verify the FastAPI backend server is active:

```bash
systemctl status ainews-backend.service
```

### Check Editorial Timer Status
To verify the daily timer is active and see when the next scheduled run will take place:

```bash
systemctl status ainews-editorial.timer
systemctl list-timers --all | grep ainews
```

### Trigger a Test Run Immediately
You can trigger the editorial service right away without waiting for the 06:00 AM timer:

```bash
# Non-blocking launch (returns prompt immediately)
sudo systemctl start --no-block ainews-editorial.service

# Follow live progress
tail -f logs/editorial_cron.log
```

### Inspect Output Logs
```bash
# Backend server logs
tail -f logs/backend.log

# Editorial workflow logs
tail -f logs/editorial_cron.log
```
