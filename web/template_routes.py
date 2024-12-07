from flask import Blueprint, render_template

template_routes = Blueprint("templates_blueprint", __name__)

@template_routes.route("/")
def home():
    return render_template("home.html")

# @template_routes.route("/404")
# def about():
#     return render_template("about.html")

# @template_routes.route("/500")
# def about():
#     return render_template("about.html")