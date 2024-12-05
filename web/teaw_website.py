import sys
import logging
import os


from flask import (Flask, redirect, render_template, request, abort,
                   send_from_directory, url_for, jsonify, Response)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Python not looking in parent directories for common files you might want to use is stupid
sys.path.append("../")
from diet_logger import setup_logger


LOG_LEVEL = logging.DEBUG
FLASK_DEBUG = True
LOG_FILE = "../logs/server.log"

app = Flask(__name__, template_folder="html", static_folder="") # tell Flask static is the current directory


# NOTE: Pages
@app.route("/")
def home():
    return render_template("base.html")









if __name__ == "__main__":
    log = setup_logger(LOG_FILE, LOG_LEVEL)
    app.run(debug=FLASK_DEBUG, port=1851)