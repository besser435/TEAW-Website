import sys
import logging
import os

from flask import Flask

from template_routes import template_routes
from api_routes import api_routes

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Python not looking in parent directories for common files you might want to use is stupid
sys.path.append("../")
from diet_logger import setup_logger


# Config
log_level = logging.INFO
LOG_FILE = "../logs/server.log"


# Setup
app = Flask(__name__, template_folder="html", static_folder="") # Tell Flask `static` is the current directory

app.register_blueprint(template_routes)
app.register_blueprint(api_routes)

log = setup_logger(LOG_FILE, log_level)
log.info("---- Starting TEAW Webserver ----")


if __name__ == "__main__":  
    # Run in debug mode if this file is being ran.
    # Otherwise run `app` from a WSGI server.

    log_level = logging.DEBUG
    app.run(debug=True, port=1851)
