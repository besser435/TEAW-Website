from flask import Blueprint, jsonify, send_from_directory, request
from werkzeug.exceptions import NotFound
import sqlite3
import traceback
import time


from config import TEAW_DB_FILE, STATS_DB_FILE, PLAYER_BODY_SKIN_DIR, PLAYER_FACE_SKIN_DIR, log


api_routes = Blueprint("api_blueprint", __name__)


# NOTE: Routes only return the required data for each page, not every column in the database.

@api_routes.route("/api")
def api():
    return "ok", 200


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
    except Exception:
        log.error(f"Internal error getting `status`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500


@api_routes.route("/api/players")
def get_all_players():
    try:
        with sqlite3.connect(TEAW_DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
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
            
            players = [dict(row) for row in cursor.fetchall()]

        return jsonify(players), 200
    except Exception:
        log.error(f"Internal error getting `players`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500


@api_routes.route("/api/towns")
def get_all_towns():
    try:
        return "ok", 200
    except Exception:
        log.error(f"Internal error getting `towns`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500


@api_routes.route("/api/chat_messages")
def get_chat_messages():
    try:
        oldest_message_id = request.args.get("oldest_message_id", type=int)
        newest_message_id = request.args.get("newest_message_id", type=int)

        if oldest_message_id and newest_message_id:
            return {"error": "invalid request: multiple args present"}, 400

        with sqlite3.connect(TEAW_DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if oldest_message_id:   # Older messages before a certain ID (used when the user scrolls and wants older messages)
                cursor.execute("""
                    SELECT id, sender, sender_uuid, message, timestamp, type
                    FROM chat
                    WHERE id < ?
                    ORDER BY id DESC
                    LIMIT 200
                """, (oldest_message_id,))
            
            elif newest_message_id: # New messages after a certain ID (used for updates)
                cursor.execute("""
                    SELECT id, sender, sender_uuid, message, timestamp, type
                    FROM chat
                    WHERE id > ?
                    ORDER BY id ASC
                    LIMIT 200
                """, (newest_message_id,))
            
            else:   # All of the newest messages (used on page load)
                cursor.execute("""
                    SELECT id, sender, sender_uuid, message, timestamp, type
                    FROM chat
                    ORDER BY id DESC
                    LIMIT 400
                """)

            chat_messages = [dict(row) for row in cursor.fetchall()]

        chat_messages.reverse() # TODO: might not be needed

        return jsonify(chat_messages), 200
    except Exception:
        log.error(f"Internal error getting `chat_messages`: {traceback.format_exc()}")
        return "internal error", 500


@api_routes.route("/api/chat_misc")
def get_chat_misc():
    try:
        with sqlite3.connect(TEAW_DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM chat")
            messages_logged = cursor.fetchone()[0]

            cursor.execute("""
                SELECT variable, value
                FROM variables
                WHERE variable IN ("day", "weather", "world_time_24h")
            """)
            variables = dict(cursor.fetchall())

            days_elapsed = int(variables.get("day", 0))
            world_weather = variables.get("weather", "Unknown")
            world_time = variables.get("world_time_24h", "06:00")

        return {
            "messages_logged": messages_logged,
            "days_elapsed": days_elapsed,
            "world_weather": world_weather,
            "world_time": world_time
        }, 200
    except Exception:
        log.error(f"Internal error getting `chat_misc`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500


@api_routes.route("/api/player_skin/<uuid>")
def get_player_skin(uuid):
    try:
        return send_from_directory(PLAYER_BODY_SKIN_DIR, f"{uuid}.png")
    except NotFound:
        return "player skin not found", 404
    except Exception:
        log.error(f"Internal error getting `player_skin`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500


@api_routes.route("/api/player_face/<uuid>")
def get_player_face(uuid):
    try:
        return send_from_directory(PLAYER_FACE_SKIN_DIR, f"{uuid}.png")
    except NotFound:
        return "player face not found", 404
    except Exception:
        log.error(f"Internal error getting `player_face`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500
