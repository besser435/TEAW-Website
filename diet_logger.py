import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_file, log_level) -> logging.Logger:
    """
    Sets up a logger that logs to both the console and a file with rotation.

    `param log_file` Path to the log file.
    `param log_level` Logging level.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger_name = os.path.splitext(os.path.basename(log_file))[0] # Get the logger name from the file name
    logger = logging.getLogger(logger_name)
    
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger