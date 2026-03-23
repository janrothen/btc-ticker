import logging
import os
import signal
import sys
import traceback

from epaper.config import config

os.environ.setdefault("GPIOZERO_PIN_FACTORY", config().get("gpiozero", {}).get("pin_factory", "pigpio"))

from epaper.display import PriceTicker
from epaper.price.client import BitcoinPriceClient
from epaper.price.extractor import PriceExtractor
from epaper.utils.graceful_shutdown import GracefulShutdown

logging.basicConfig(level=logging.INFO)


def main() -> None:
    price_client = BitcoinPriceClient()
    price_extractor = PriceExtractor("USD", "$")
    ticker = PriceTicker(price_client, price_extractor)
    shutdown = GracefulShutdown()

    try:
        ticker.start()
        while not shutdown.kill_now:
            ticker.tick()
    except Exception as ex:
        logging.error(ex)
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
    finally:
        ticker.stop()


if __name__ == "__main__":
    main()
