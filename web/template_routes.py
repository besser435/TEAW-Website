from flask import Blueprint, render_template

template_routes = Blueprint("templates_blueprint", __name__)


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

