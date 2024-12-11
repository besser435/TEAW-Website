import logging
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys.path.append("../")
from diet_logger import setup_logger

# Config
log_level = logging.DEBUG

LOG_FILE = "../logs/webserver.log"
TEAW_DB_FILE = "../db/teaw.db"
STATS_DB_FILE = "../db/stats.db"

# Setup Logger
log = setup_logger(LOG_FILE, log_level)
