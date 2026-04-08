import logging
import os
import sys

from btcticker.config import config

# GPIOZERO_PIN_FACTORY must be set before Display is imported, because gpiozero
# reads the env var at import time to select the GPIO backend.
os.environ.setdefault(
    "GPIOZERO_PIN_FACTORY", config().get("gpiozero", {}).get("pin_factory", "pigpio")
)

from btcticker.display import Display
from btcticker.price.bitcoin_price_client import BitcoinPriceClient
from btcticker.price.price_extractor import PriceExtractor
from btcticker.price_ticker import PriceTicker
from btcticker.utils.graceful_shutdown import GracefulShutdown
from btcticker.utils.watchdog import sd_notify

logging.basicConfig(level=logging.INFO)


def main() -> None:
    cfg = config().get("bitcoin", {}).get("price", {})
    currency = cfg.get("currency", "USD")
    symbol = cfg.get("symbol", "$")
    refresh_interval = cfg.get("refresh_interval", 300)

    display = Display()
    price_client = BitcoinPriceClient()
    price_extractor = PriceExtractor(currency, symbol)
    ticker = PriceTicker(display, price_client, price_extractor, refresh_interval)
    shutdown = GracefulShutdown()

    try:
        ticker.start()
        sd_notify("READY=1")
        while not shutdown.kill_now:
            ticker.tick()
            sd_notify("WATCHDOG=1")
    except Exception as ex:
        logging.exception(ex)
        sys.exit(1)
    finally:
        ticker.stop()


if __name__ == "__main__":
    main()
