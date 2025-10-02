# src/logging_config.py
from loguru import logger
import sys
from pathlib import Path
from .config import LOG_LEVEL

LOG_PATH = Path("bot.log")

def configure_logging():
    logger.remove()
    logger.add(sys.stdout, level=LOG_LEVEL, backtrace=True, diagnose=False)
    logger.add(str(LOG_PATH), rotation="10 MB", retention="10 days", enqueue=True)
