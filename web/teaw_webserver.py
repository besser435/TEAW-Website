import os
import subprocess
import sys
import atexit
import signal
import socket
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


# Manage Sass
def start_sass(app: Flask, watch: bool):
    if watch:
        cmd = ["sass", "--watch", "--poll", "scss:css"]    # Auto-compile mode and verbose CSS files
    else:
        cmd = ["sass", "--style=compressed", "scss:css"]    # Compile once and keep CSS compact

    try:
        if watch:
            # Start sass watcher process
            log.info("Compiling SCSS and starting watcher...")
            app.sass_watcher = subprocess.Popen(    # NOTE: Puts sass_watcher on the app object
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
        else:
            # Run sass once
            log.info("Compiling SCSS...")
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

        log.info("SCSS compiled")

    except FileNotFoundError:
        log.critical("Sass compiler not found or not in PATH")
        sys.exit(1)

    except subprocess.CalledProcessError as e:
        log.error("Sass compilation failed")
        log.error(e.stdout or "")
        log.error(e.stderr or "")

def stop_sass(app: Flask):
    # Prevents orphaned processes for the sass watcher mode
    watcher = getattr(app, "sass_watcher", None)

    if watcher and watcher.poll() is None:
        log.info("Stopping Sass watcher...")
        try:
            if os.name == "nt": # Windows
                watcher.send_signal(signal.CTRL_BREAK_EVENT)
            else:               # Linux
                watcher.terminate()

            watcher.wait(timeout=5)
        except Exception:
            watcher.kill()

atexit.register(lambda: stop_sass(app))
start_sass(app, watch=False)


if __name__ == "__main__":
    # --- Debug Mode Stuff ---

    # Start Sass with watcher mode and verbose files.
    # Yes this will lead the files being compiled again since we call it above for production, 
    # but thats why modern computers are fast (lazy and stupid programmers) :3 
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":   # Only run in the child process for Flask's debug mode.
        start_sass(app, watch=True)

    # So you can access it from other devices on the LAN. Might not always work.
    host_ip = socket.gethostbyname(socket.gethostname())
    log.info(f"Current IP: {host_ip}")

    # Run in debug mode if this file is being run.
    # Otherwise run `app` from a WSGI server.
    app.run(debug=True, host=host_ip, port=1851)