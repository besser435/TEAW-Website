from flask import Blueprint, jsonify, send_from_directory
from werkzeug.exceptions import NotFound
import sqlite3
import os
import time


from config import TEAW_DB_FILE, STATS_DB_FILE, PLAYER_BODY_SKIN_DIR, PLAYER_FACE_SKIN_DIR, log


api_routes = Blueprint("api_blueprint", __name__)

@api_routes.route("/api")
def home():
    return "ok", 200

# TODO
@api_routes.route("/api/status")    # For status indicator in the navbar. Call every 2s
def get_status():
    try:
        with sqlite3.connect(TEAW_DB_FILE) as conn:
            cursor = conn.cursor()

            # Check if the data is up to date
            cursor.execute("""
                SELECT variable, value
                FROM variables
                WHERE variable IN ('last_players_update', 'last_chat_update')
            """)
            result = dict(cursor.fetchall())

            # Count online players (those with online_duration > 0)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM players 
                WHERE online_duration > 0
            """)
            online_players_count = cursor.fetchone()[0]

        last_players_update = int(result.get("last_players_update", 0))
        last_chat_update = int(result.get("last_chat_update", 0))

        current_time = int(time.time()) * 1000  # DB time is in ms

        if (current_time - last_players_update < 15_000) and (current_time - last_chat_update < 15_000):
            status = "ok"
        else:
            status = "stale"

        return dict(status=status, online_players=online_players_count), 200
    except Exception as e:
        log.error(f"Internal error getting `status`: {e}")
        return "internal error", 500


@api_routes.route("/api/players")   # For the players page. Only returns the required data, not every column
def get_all_players():
    try:
        with sqlite3.connect(TEAW_DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    uuid, 
                    name, 
                    online_duration, 
                    afk_duration, 
                    town_name, 
                    nation_name,
                    CASE 
                        WHEN online_duration > 0 AND afk_duration > 0 THEN 'afk'
                        WHEN online_duration > 0 THEN 'online'
                        ELSE 'offline'
                    END AS status
                FROM players
                ORDER BY status, name
            """)
            
            players = [
                {
                    'uuid': row[0],
                    'name': row[1],
                    'online_duration': row[2],
                    'afk_duration': row[3],
                    'town_name': row[4],
                    'nation_name': row[5],
                    'status': row[6]
                }
                for row in cursor.fetchall()
            ]

        return jsonify(players), 200
    except Exception as e:
        log.error(f"Internal error getting `players`: {e}")
        return "internal error", 500


@api_routes.route("/api/towns")     # For the towns page. Only returns the required data, not every column
def get_all_towns():
    try:
        return "ok", 200
    except Exception as e:
        log.error(f"Internal error getting `towns`: {e}")
        return "internal error", 500













@api_routes.route("/api/player_skin/<uuid>")
def get_player_skin(uuid):
    try:
        return send_from_directory(PLAYER_BODY_SKIN_DIR, f"{uuid}.png")
    except NotFound:
        return "player skin not found", 404
    except Exception as e:
        log.error(f"Internal error getting `player_skin`: {e}")
        return "internal error", 500


@api_routes.route("/api/player_face/<uuid>")
def get_player_face(uuid):
    try:
        return send_from_directory(PLAYER_FACE_SKIN_DIR, f"{uuid}.png")
    except NotFound:
        return "player face not found", 404
    except Exception as e:
        log.error(f"Internal error getting `player_face`: {e}")
        return "internal error", 500
