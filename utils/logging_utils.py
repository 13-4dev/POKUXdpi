import logging
from config.config import config

def setup_logging():
    if config.debug:
        log_format = 'time="%(asctime)s" level=%(levelname)s msg="%(message)s"'
        date_format = "%Y-%m-%dT%H:%M:%S%z"
        logging.basicConfig(
            format=log_format,
            level=logging.DEBUG,
            datefmt=date_format,
            handlers=[logging.StreamHandler()]
        )
    else:
        logging.disable(logging.CRITICAL)
