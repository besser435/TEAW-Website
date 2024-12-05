from flask import Blueprint, render_template

template_routes = Blueprint("templates_blueprint", __name__)

@template_routes.route("/")
def home():
    return render_template("base.html")
