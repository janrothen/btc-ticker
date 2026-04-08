# Bitcoin Price Ticker

Displays the current Bitcoin/USD price on a Waveshare 2.13" e-ink display (epd2in13 V2) connected to a Raspberry Pi. On startup it shows a Bitcoin logo, then enters a loop that refreshes the price every 5 minutes. The background alternates randomly between black and white on each refresh.

## Target environment
- Hardware: Raspberry Pi 4, 8 GB RAM
- OS: Debian GNU/Linux 13 (trixie), aarch64
- Python: 3.13.5

## Structure
```
src/btcticker/          # installable package
  __main__.py        # entry point: python -m btcticker
  display.py         # hardware abstraction (Display)
  price_ticker.py    # orchestration: price updates and rendering (PriceTicker)
  config.py          # config loader (tomllib + config.toml)
  http_client.py     # HTTP wrapper
  price/             # price fetching and formatting
    bitcoin_price_client.py
    price_extractor.py
    mock.py          # test fixture client
  utils/
    graceful_shutdown.py
    watchdog.py      # systemd sd_notify integration
  lib/               # Waveshare display drivers (fallback when pip package unavailable)
  media/             # fonts and images
tests/
deploy/
  systemd/
    btcticker.service   # systemd unit for auto-start on boot
    README.md        # installation instructions
config.toml          # runtime config (service endpoint)
pyproject.toml       # packaging and dependencies
```

## Off-limits files
- `lib/` — vendored Waveshare code (excluded via .claudeignore), treat as a black box.
  Reference the API it exposes but never modify the files.

## Dev/test
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
