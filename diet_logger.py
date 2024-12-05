import logging
from logging.handlers import RotatingFileHandler


def setup_logger(log_file, log_level) -> logging.Logger:
    """
    Sets up a logger that logs to both the console and a file.

    `param log_file` Path to the log file.
    `param log_level` Logging level.
    """

    logger = logging.getLogger("db_updater")
    logger.setLevel(log_level)

    if logger.hasHandlers():
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)  # 10 MB per file, 5 files
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
