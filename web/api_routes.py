from flask import Blueprint

api_routes = Blueprint("api_blueprint", __name__)

@api_routes.route("/api")
def home():
    return "ok"
