import sys
import logging
from config import LOG_LEVEL

def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
