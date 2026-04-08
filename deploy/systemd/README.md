# systemd service unit

`epaper.service` runs the Bitcoin price ticker as a systemd service, enabling auto-start on boot and auto-restart on failure.

## Before installing

Open `epaper.service` and adjust these three fields to match your setup:

| Field | Example |
|---|---|
| `User` | `pi` |
| `WorkingDirectory` | `/home/pi/raspberry/btc-ticker` |
| `ExecStart` | `/home/pi/raspberry/btc-ticker/.venv/bin/python -m epaper` |

## Installation

```bash
# Install the service unit
sudo cp deploy/systemd/epaper.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable (start on boot) and start immediately
sudo systemctl enable --now epaper

# Check status / logs
systemctl status epaper
journalctl -u epaper -f
```

To stop and disable auto-start:

```bash
sudo systemctl disable --now epaper
```
