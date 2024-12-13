from flask import Blueprint, render_template
import requests
import json
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

@template_routes.route("/wars")
def wars():
    return render_template("wars.html")

@template_routes.route("/showcase")
def showcase():
    return render_template("showcase.html")

@template_routes.route("/error")
def error(code):
    return render_template("error.html")

