import logging 
import os
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# configure logger
logger = logging.getLogger("sastokinmel")
logger.setLevel(logging.INFO)

# file handler with rotation
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10485760,
    backupCount=5
)
file_handler.setLevel(logging.INFO)

# console handler 
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)