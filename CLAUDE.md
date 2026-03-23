# E-Paper Bitcoin Price Ticker

Displays the current Bitcoin/USD price on a Waveshare 2.13" e-ink display (epd2in13 V2) connected to a Raspberry Pi. On startup it shows a Bitcoin logo, then enters a loop that refreshes the price every 5 minutes. The background alternates randomly between black and white on each refresh.

## Target environment
- Hardware: Raspberry Pi 5, 16 GB RAM
- OS: Debian GNU/Linux 13 (trixie), aarch64
- Python: 3.13.5

## Structure
```
src/epaper/          # installable package
  __main__.py        # entry point: python -m epaper
  display.py         # e-paper display logic (PriceTicker)
  config.py          # config loader (tomllib + config.toml)
  http_client.py     # HTTP wrapper
  price/             # price fetching and formatting
    client.py
    extractor.py
    mock.py          # test fixture client
  utils/
    graceful_shutdown.py
  lib/               # Waveshare display drivers
  media/             # fonts and images
tests/
config.toml          # runtime config (service endpoint)
pyproject.toml       # packaging and dependencies
```

## Install & run
```bash
# On Raspberry Pi (with hardware deps):
python -m venv .venv
source .venv/bin/activate
pip install -e ".[rpi]"
python -m epaper

# Dev/test (no GPIO hardware needed):
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

If you get permission errors on SPI/GPIO devices, add your user to the required groups (then log out and back in):
```bash
sudo usermod -aG spi,gpio $USER
```
