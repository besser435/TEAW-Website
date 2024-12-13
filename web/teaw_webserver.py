import os
from flask import Flask
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from template_routes import template_routes
from api_routes import api_routes
from config import log


log.info("---- Starting TEAW Webserver ----")

app = Flask(__name__, template_folder="html", static_folder="")  # Tell Flask `static` is the current directory

app.register_blueprint(template_routes)
app.register_blueprint(api_routes)


if __name__ == "__main__":
    # Run in debug mode if this file is being run.
    # Otherwise run `app` from a WSGI server.
    app.run(debug=True, port=1851)