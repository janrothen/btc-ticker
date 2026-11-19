# Bitcoin Price Ticker

![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20%7C%20Linux-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=janrothen_btc-ticker&metric=alert_status)](https://sonarcloud.io/project/overview?id=janrothen_btc-ticker)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=janrothen_btc-ticker&metric=bugs)](https://sonarcloud.io/project/overview?id=janrothen_btc-ticker)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=janrothen_btc-ticker&metric=coverage)](https://sonarcloud.io/project/overview?id=janrothen_btc-ticker)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=janrothen_btc-ticker&metric=security_rating)](https://sonarcloud.io/project/overview?id=janrothen_btc-ticker)
[![GitGuardian](https://img.shields.io/badge/GitGuardian-monitored-blue?logo=gitguardian&logoColor=white)](https://www.gitguardian.com)

Displays the current Bitcoin/USD price on a Waveshare 2.13" e-ink display (epd2in13 V2) connected to a Raspberry Pi. On startup it shows a Bitcoin logo, then enters a loop that refreshes the price every 5 minutes. The background alternates randomly between black and white on each refresh.

![Raspberry Pi 4 with Waveshare e-ink display showing $73.08k](docs/images/assembled.png)

## Requirements

**Hardware**
- Raspberry Pi (tested on Pi 4 Model B Rev 1.4)
- Waveshare 2.13" e-ink display (epd2in13 V2)

The guide [How to connect a Waveshare E-Ink display to a Raspberry Pi](https://janrothen.github.io/btc-ticker/raspberry-pi-waveshare-epaper-bitcoin-ticker.html) shows how to physically connect the Waveshare 2.13" e-ink display to a Raspberry Pi.

**Software**
- Python 3.13+
- pip dependencies: `requests`, `Pillow` (see `pyproject.toml`)
- Raspberry Pi extras: `gpiozero`, `lgpio`, `spidev`, `waveshare-epd` (installed by `deploy/install.sh`)

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

On the Raspberry Pi, as the user the service should run as:

```bash
git clone https://github.com/janrothen/btc-ticker.git
cd btc-ticker
./deploy/install.sh
```

The installer sets up system packages, SPI, the `gpio`/`spi` groups, the Python venv and the `btcticker` systemd service, and is safe to run again. Run `./deploy/install.sh --help` for options.

**Upgrade:** `git pull && ./deploy/install.sh`

btc-ticker uses gpiozero's lgpio backend; no GPIO daemon is required.

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

`./deploy/install.sh` installs and enables the service. See [`deploy/systemd/README.md`](deploy/systemd/README.md) for the manual steps, migrating from pigpio and rollback.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `ModuleNotFoundError` for `waveshare_epd` or `lgpio` | Raspberry Pi extras not installed — run `./deploy/install.sh` |
| Installer fails building `lgpio` (compiler or `Python.h` not found) | Missing build dependencies — run `sudo apt install gcc libc6-dev python3-dev`, then rerun `./deploy/install.sh` |
| `PermissionError` on `/dev/spidev0.0` or `/dev/gpiochip0` | User not in the `spi`/`gpio` groups — rerun `./deploy/install.sh`, which adds them and restarts the service |
| Display stays blank after start | SPI not enabled — run `sudo raspi-config` → Interface Options → SPI → Enable |
| Display blank right after the installer enabled SPI | SPI only takes effect after a reboot — run `sudo reboot`, then rerun `./deploy/install.sh` to start the service and finish the pigpio cleanup |
| Price shows as `$0` or `N/A` | API unreachable — check network and `service_endpoint` in `config.toml` |
| Service fails to start with `sd_notify` errors | `Type=notify` in the unit file requires systemd watchdog support; rerun `./deploy/install.sh` to reinstall the unit |
| Service fails after migrating from pigpio | Check `journalctl -u btcticker -n 50`; to go back, follow [Rollback](deploy/systemd/README.md#rollback) |
| `waveshare_epd` import fails | Package installed from wrong commit — rerun `./deploy/install.sh` |

## Contributing

Found a bug or have an idea? Open an issue or send a PR.
Run `pytest` before submitting and keep changes focused.

## License

MIT © Jan Rothen — see [LICENSE](LICENSE) for details.
