from flask import Blueprint
import sqlite3
import os
import time
import json


from config import TEAW_DB_FILE, STATS_DB_FILE, log


api_routes = Blueprint("api_blueprint", __name__)

@api_routes.route("/api")
def home():
    return "ok"


@api_routes.route("/api/status")    # For status indicator in the navbar. Call every 2s
def status():
    # If the chat and players tables were updated within the 
    # last 15 seconds (they update every 5s + however long it takes run)
    # return server status as ok.

    # also return how many players are online.


    # TODO: Should maybe add an is_online column to players


    with sqlite3.connect(TEAW_DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT variable, value
            FROM variables
            WHERE variable IN ('last_players_update', 'last_chat_update')
        """)
        result = dict(cursor.fetchall())

    last_players_update = int(result.get("last_players_update", 0))
    last_chat_update = int(result.get("last_chat_update", 0))

    current_time = int(time.time()) * 1000  # DB time is in ms

    if current_time - last_players_update < 15_000 and current_time - last_chat_update < 15_000:
        status = "ok"
    else:
        status = "stale"

    return dict(status=status, online_players=0)
