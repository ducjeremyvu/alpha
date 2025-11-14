import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(level=logging.INFO, log_file="app.log"):
    """Configure global logging for both console and file output."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture everything; handlers decide what to show.

    # Clear old handlers to avoid duplicate logs if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Shared log format
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # --- Console Handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)  # Console only shows level+ (default: INFO)
    console_handler.setFormatter(formatter)

    # --- File Handler (keeps everything, including DEBUG) ---
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5_000_000, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add handlers back
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
