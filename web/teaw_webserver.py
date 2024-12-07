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


# Create the Flask app
app = Flask(__name__, template_folder="html", static_folder="") # Tell Flask `static` is the current directory

# Add routes
app.register_blueprint(template_routes)
app.register_blueprint(api_routes)

# Enable logger
log = setup_logger(LOG_FILE, log_level)
log.info("---- Starting TEAW webserver ----")



if __name__ == "__main__":  
    # Run in debug mode if this file is being ran.
    # Otherwise run `app` from a WSGI server.

    log_level = logging.DEBUG
    app.run(debug=True, port=1851)

#waitress-serve --host 127.0.0.1 --port 1851 teaw_website:app 
