import logging
import sys
from logging.handlers import RotatingFileHandler
import colorlog

EMOJI = {
    "DEBUG": "🐞",
    "INFO": "✨",
    "WARNING": "⚠️",
    "ERROR": "🔥",
    "CRITICAL": "💀",
}


class EmojiColoredFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        emoji = EMOJI.get(record.levelname, "")
        message = super().format(record)
        return f"{emoji} {message}"


def setup_logging(level=logging.INFO, log_file="app.log"):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    # FILE formatter
    file_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # CONSOLE formatter with colored timestamp + emojis
    console_formatter = EmojiColoredFormatter(
        "%(asctime_log_color)s%(asctime)s%(reset)s "
        "%(log_color)s%(levelname)-8s%(reset)s "
        "%(white)s[%(name)s]%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={
            "asctime": {"color": "cyan"},  # timestamp color
        },
    )

    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)

    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
