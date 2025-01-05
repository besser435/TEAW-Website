import os
from flask import Flask
from flask_cors import CORS

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from template_routes import template_routes
from api_routes import api_routes
from stats_routes import stats_routes
from config import log


log.info("---- Starting TEAW Webserver ----")

app = Flask(__name__, template_folder="html", static_folder="")  # Tell Flask `static` is the current directory
CORS(app, resources={r"/*": {"origins": "https://usa-industries.net"}})

app.register_blueprint(template_routes)
app.register_blueprint(api_routes)
app.register_blueprint(stats_routes)


if __name__ == "__main__":
    # Run in debug mode if this file is being run.
    # Otherwise run `app` from a WSGI server.
    app.run(debug=True, port=1851, host="192.168.0.101")