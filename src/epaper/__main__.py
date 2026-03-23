import logging
import os
import sys
import traceback

from epaper.config import config

os.environ.setdefault("GPIOZERO_PIN_FACTORY", config().get("gpiozero", {}).get("pin_factory", "pigpio"))

from epaper.display import PriceTicker
from epaper.price.client import BitcoinPriceClient
from epaper.price.extractor import PriceExtractor
from epaper.utils.graceful_shutdown import GracefulShutdown

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    price_client = BitcoinPriceClient()
    price_extractor = PriceExtractor("USD", "$")
    ticker = PriceTicker(price_client, price_extractor)
    shutdown = GracefulShutdown()

    # Wire shutdown signal into the ticker
    original_exit = shutdown._exit

    def _on_signal(signum, frame):
        original_exit(signum, frame)
        ticker.stop()

    import signal
    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    try:
        ticker.start()
    except Exception as ex:
        logging.error(ex)
        ticker.stop()
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
