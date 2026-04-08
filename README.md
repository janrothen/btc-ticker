# Bitcoin Price Ticker

![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20%7C%20Linux-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=janrothen_btc-ticker&metric=alert_status)](https://sonarcloud.io/project/overview?id=janrothen_btc-ticker)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=janrothen_btc-ticker&metric=bugs)](https://sonarcloud.io/project/overview?id=janrothen_btc-ticker)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=janrothen_btc-ticker&metric=coverage)](https://sonarcloud.io/project/overview?id=janrothen_btc-ticker)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=janrothen_btc-ticker&metric=security_rating)](https://sonarcloud.io/project/overview?id=janrothen_btc-ticker)

Displays the current Bitcoin/USD price on a Waveshare 2.13" e-ink display (epd2in13 V2) connected to a Raspberry Pi. On startup it shows a Bitcoin logo, then enters a loop that refreshes the price every 5 minutes. The background alternates randomly between black and white on each refresh.

## Requirements

**Hardware**
- Raspberry Pi (tested on Pi 4 Model B Rev 1.4)
- Waveshare 2.13" e-ink display (epd2in13 V2)

**Software**
- Python 3.13+
- pip dependencies: `requests`, `Pillow` (see `pyproject.toml`)
- Raspberry Pi extras: `RPi.GPIO`, `spidev`, `pigpio`, `gpiozero`, `numpy`, `waveshare-epd` (installed via `pip install -e ".[rpi]"`)

## Architecture

### Runtime sequence

```mermaid
sequenceDiagram
    participant OS as systemd
    participant Main as __main__
    participant Ticker as PriceTicker
    participant Display
    participant PRICE_API as Bitcoin Price API

    OS->>Main: start process
    Main->>Display: init + clear
    Main->>Ticker: start()
    Ticker->>Display: show(bitcoin logo)
    Ticker-->>Main: (3s pause)
    Main->>OS: sd_notify READY=1

    loop every 5 minutes
        Main->>Ticker: tick()
        Ticker->>PRICE_API: retrieve_data() (up to 3 retries)
        PRICE_API-->>Ticker: {"USD": {"last": 84500}}
        Ticker->>Ticker: format_price → "$84.5k"
        Ticker->>Display: init → show(price) → sleep()
        Main->>OS: sd_notify WATCHDOG=1
    end

    OS->>Main: SIGTERM
    Main->>Ticker: stop()
    Ticker->>Display: init → clear → sleep()
```

## Configuration

All settings live in `config.toml` — there are no secrets or `.env` files required.

```toml
[bitcoin.price]
service_endpoint = "https://blockchain.info/ticker"
currency = "USD"   # currency code returned by the API (e.g. "CHF", "EUR")
symbol = "$"       # symbol shown on the display (e.g. "CHF ", "€")
refresh_interval = 300  # seconds between price refreshes
```

**To display a different currency**, set `currency` to any code the API returns and `symbol` to the label you want shown on screen. For example, to show Swiss francs:

```toml
currency = "CHF"
symbol = "CHF "
```

The `service_endpoint` must return JSON in this shape (the [blockchain.info ticker](https://blockchain.info/ticker) is the default):

```json
{
  "USD": { "last": 84500.0 },
  "CHF": { "last": 75000.0 }
}
```

Any endpoint that returns this structure works as a drop-in replacement.

## Install & run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[rpi]"
python -m btcticker
```

If you get permission errors on SPI/GPIO devices, add your user to the required groups (then log out and back in):

```bash
sudo usermod -aG spi,gpio $USER
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

The mock price client (`src/btcticker/price/mock.py`) is used automatically during tests so no live API or hardware is required to run the test suite.

## Deployment

Run as a systemd service for auto-start on boot and auto-restart on failure.

See [`deploy/systemd/README.md`](deploy/systemd/README.md) for installation instructions.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `ModuleNotFoundError: No module named 'RPi'` | RPi extras not installed — run `pip install -e ".[rpi]"` |
| `PermissionError` on `/dev/spidev` or `/dev/gpiomem` | User not in `spi`/`gpio` groups — run `sudo usermod -aG spi,gpio $USER` and re-login |
| Display stays blank after start | SPI not enabled — run `sudo raspi-config` → Interface Options → SPI → Enable |
| Price shows as `$0` or `N/A` | API unreachable — check network and `service_endpoint` in `config.toml` |
| Service fails to start with `sd_notify` errors | `Type=notify` in the unit file requires systemd watchdog support; verify the unit matches `deploy/systemd/btcticker.service` |
| `waveshare_epd` import fails | Package installed from wrong commit — reinstall with `pip install -e ".[rpi]"` |

## Contributing

Found a bug or have an idea? Open an issue or send a PR.
Run `pytest` before submitting and keep changes focused.

## License

MIT © Jan Rothen — see [LICENSE](LICENSE) for details.
