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



LOG_LEVEL = logging.DEBUG
FLASK_DEBUG = True                  # IMPORTANT: Set to False when deploying with run.sh
LOG_FILE = "../logs/server.log"


app = Flask(__name__, template_folder="html", static_folder="") # Tell Flask `static` is the current directory


app.register_blueprint(template_routes)
app.register_blueprint(api_routes)


if __name__ == "__main__":
    log = setup_logger(LOG_FILE, LOG_LEVEL)
    app.run(debug=FLASK_DEBUG, port=1851)
