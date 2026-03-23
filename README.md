# E-Paper Bitcoin Price Ticker

Displays the current Bitcoin/USD price on a Waveshare 2.13" e-ink display (epd2in13 V2) connected to a Raspberry Pi. On startup it shows a Bitcoin logo, then enters a loop that refreshes the price every 5 minutes. The background alternates randomly between black and white on each refresh.

## Requirements

- Raspberry Pi (tested on Pi 5)
- Waveshare 2.13" e-ink display (epd2in13 V2)
- Python 3.9+

## Install & run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[rpi]"
python -m epaper
```

If you get permission errors on SPI/GPIO devices, add your user to the required groups (then log out and back in):
```bash
sudo usermod -aG spi,gpio $USER
```

## Run as a systemd service (auto-start on boot, auto-restart on failure)

```bash
# Install the service unit
sudo cp systemd/epaper.service /etc/systemd/system/
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
