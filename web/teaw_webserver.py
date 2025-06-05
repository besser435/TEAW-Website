import os
from flask import Flask
from flask_cors import CORS

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from template_routes import template_routes
from api_routes import api_routes
from stats_routes import stats_routes
from config import log
import socket


log.info("---- Starting TEAW Webserver ----")

app = Flask(__name__, template_folder="html", static_folder="")  # Tell Flask `static` is the current directory
CORS(app, resources={r"/*": {"origins": "https://usa-industries.net"}})

app.register_blueprint(template_routes)
app.register_blueprint(api_routes)
app.register_blueprint(stats_routes)


if __name__ == "__main__":
    # So you can access it from other devices on the LAN. Might not always work.
    host_ip = socket.gethostbyname(socket.gethostname())
    log.info(f"Current IP: {host_ip}")


    # Run in debug mode if this file is being run.
    # Otherwise run `app` from a WSGI server.
    app.run(debug=True, host=host_ip, port=1851)