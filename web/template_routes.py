from flask import Blueprint, render_template, abort
import requests
import traceback
import datetime

from config import log

template_routes = Blueprint("templates_blueprint", __name__)

last_commit_date = None
def on_start():
    global last_commit_date

    def _add_ordinal_suffix(day):
        return f"{day}{'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')}"
    
    try:
        branch = "prod"
        commits_url = f"https://api.github.com/repos/besser435/TEAW-Website/commits?per_page=1&sha={branch}"
        
        response = requests.get(commits_url)
        response.raise_for_status()
        
        latest_commit = response.json()[0]
        commit_date = datetime.datetime.strptime(latest_commit["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
        day_with_suffix = _add_ordinal_suffix(commit_date.day)
        last_commit_date = commit_date.strftime(f"%B {day_with_suffix}")
        
        log.info(f"Latest commit on {branch} branch: {last_commit_date}")
    except Exception as e:
        last_commit_date = "Error fetching last update"
        log.error(f"Error fetching last update: {e}")
on_start()

@template_routes.context_processor
def inject_lcd():
    return {"last_commit_date": last_commit_date}


@template_routes.route("/")
def home():
    return render_template("home.html")

@template_routes.route("/players")
def players():
    return render_template("/players.html")

@template_routes.route("/chat")
def chat():
    return render_template("chat.html")

@template_routes.route("/towns")
def towns():
    return render_template("towns.html")

@template_routes.route("/map")
def map():
    return render_template("map.html")

@template_routes.route("/showcase")
def showcase():
    return render_template("showcase.html")


@template_routes.app_errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error_message="Page not found", error_code=404), 404

@template_routes.app_errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_message="Internal server error", error_code=500), 500

@template_routes.errorhandler(Exception)
def handle_all_errors(e):
    log.error(traceback.format_exc())
    error_code = getattr(e, "code", 500)
    error_message = "An unexpected error occurred"

    return render_template("error.html", error_message=error_message, error_code=error_code), error_code
