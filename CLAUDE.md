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

## Dev/test
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

---

## Code review session (2026-03-23)

### What we did

Conducted a full code review and fixed all 18 findings across 8 PRs (#15–22), all merged into master:

| PR | Branch | What changed |
|----|--------|-------------|
| #15 | fix/http-timeout-config-stop | HTTP timeout (10s default), `stop()` idempotency, CWD-first config path |
| #16 | fix/graceful-shutdown-wiring | Cleaned up signal handler wiring in `main()` |
| #17 | fix/exception-handling | Accept all 2xx status codes, catch `RequestException`/`JSONDecodeError` in price client, safe `.get()` in extractor |
| #18 | fix/python-version | Raised `requires-python` to `>=3.13`, dropped `tomli` fallback |
| #19 | fix/rpi-dependency-versions | Updated `spidev` 3.4→3.8, `pigpio` 1.44→1.78, relaxed `==` pins to `>=` |
| #20 | fix/monotonic-timing | Replaced counter-based 5-min interval with `time.monotonic()` |
| #21 | fix/center-price-text | Centered price text using Pillow `anchor="mm"` |
| #22 | fix/nice-to-haves | `GracefulShutdown.kill_now` now drives the main loop; `tick()` extracted from `PriceTicker`; `Method` enum removed from `HttpClient`; `math.floor` replaces string splitting; logging changed from DEBUG→INFO; landscape orientation comment added; test currency fixed to uppercase `"USD"` |

### Current state

- 30 tests, all passing under Python 3.13.5
- Clean architecture: display, price fetching, HTTP, config, and shutdown are each in their own module
- `GracefulShutdown.kill_now` drives the main loop in `main()`; `PriceTicker.tick()` handles one refresh iteration
- All dependencies up to date; `requires-python = ">=3.13"` matches target hardware

### Next steps — Top 5 improvements (ranked by criticality × effort)

**1. Pin `waveshare-epd` to a specific git commit** *(Criticality: High, Effort: Very Low)*
The git dependency in `pyproject.toml` points at the tip of the upstream main branch. Any upstream change can silently break the display driver on the next `pip install`. Append the current HEAD commit SHA to the URL.

**2. Retry failed price fetches before showing "N/A"** *(Criticality: High, Effort: Low)*
A single network hiccup causes `"N/A"` for the full 5-minute interval. Add a 2–3 attempt retry loop with a short delay in `BitcoinPriceClient.retrieve_data()`.

**3. Add a fallback price API endpoint** *(Criticality: Medium-High, Effort: Medium)*
`blockchain.info/ticker` is the sole data source. Add an alternative endpoint (e.g. CoinGecko) to `config.toml` and fall back to it in `BitcoinPriceClient` when the primary fails.

**4. Systemd watchdog integration** *(Criticality: Medium, Effort: Medium)*
`Restart=on-failure` only catches crashes. A hung SPI/display call keeps the process alive but frozen — systemd never notices. Add `WatchdogSec=60` to the service unit and call `sd_notify("WATCHDOG=1")` inside `tick()`. Requires `python-systemd` on the Pi.

**5. Replace config singleton with `functools.lru_cache`** *(Criticality: Low, Effort: Very Low)*
Replace the mutable `_config` global with `@lru_cache(maxsize=None)` on `config()`. Same behaviour, thread-safe, idiomatic Python.
