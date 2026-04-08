# systemd service unit

`btcticker.service` runs the Bitcoin price ticker as a systemd service, enabling auto-start on boot and auto-restart on failure.

## Before installing

Open `btcticker.service` and adjust these three fields to match your setup:

| Field | Example |
|---|---|
| `User` | `pi` |
| `WorkingDirectory` | `/home/pi/raspberry/btc-ticker` |
| `ExecStart` | `/home/pi/raspberry/btc-ticker/.venv/bin/python -m btcticker` |

## Installation

```bash
# Install the service unit
sudo cp deploy/systemd/btcticker.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable (start on boot) and start immediately
sudo systemctl enable --now btcticker

# Check status / logs
systemctl status btcticker
journalctl -u btcticker -f
```

To stop and disable auto-start:

```bash
sudo systemctl disable --now btcticker
```
