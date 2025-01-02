from flask import Blueprint, jsonify, send_from_directory, request
from werkzeug.exceptions import NotFound
import sqlite3
import traceback
import time
import bleach
import os
import json
import uuid

from config import log, TEAW_DB_FILE, STATS_DB_FILE, PLAYER_BODY_SKIN_DIR, PLAYER_FACE_SKIN_DIR
from config import SHOWCASE_SUBMISSIONS_DIR, SHOWCASE_IMAGES_DIR

api_routes = Blueprint("api_blueprint", __name__)

ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}


# NOTE: Routes only return the required data for each page, not every column in the database.

# Status
@api_routes.route("/api")
def api():
    return "ok", 200

@api_routes.route("/api/status")
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

        current_time = int(time.time()) * 1000

        players_update_age = (current_time - last_players_update) // 60000
        chat_update_age = (current_time - last_chat_update) // 60000

        if players_update_age < 15 and chat_update_age < 15:
            status = "ok"
        else:
            status = "stale"

        return {
            "status": status,
            "online_players": online_players_count,
            "last_players_update_age": players_update_age,
            "last_chat_update_age": chat_update_age,
        }, 200
    except Exception:
        log.error(f"Internal error getting `status`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500


# Players
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
                    last_online,
                    CASE 
                        WHEN online_duration > 0 AND afk_duration > 0 THEN 'afk'
                        WHEN online_duration > 0 THEN 'online'
                        ELSE 'offline'
                    END AS status
                FROM players
                ORDER BY    -- Online first, then AFK, then offline.
                    CASE 
                        WHEN online_duration > 0 AND afk_duration = 0 THEN 1
                        WHEN online_duration > 0 AND afk_duration > 0 THEN 2
                        ELSE 3
                    END,
                    CASE 
                        WHEN online_duration > 0 AND afk_duration = 0 THEN -online_duration
                        ELSE last_online
                    END DESC
            """)
            players = [dict(row) for row in cursor.fetchall()]

        return jsonify(players), 200
    except Exception:
        log.error(f"Internal error getting `players`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500

@api_routes.route("/api/uuid_to_name/<uuid>")
def get_name_from_uuid(uuid):
    try:
        with sqlite3.connect(TEAW_DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM players WHERE uuid = ?", (uuid,))
            result = cursor.fetchone()

        if result:
            return result[0], 200
        else:
            return "player not found", 404
    except Exception:
        log.error(f"Internal error getting `uuid_to_name`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500

@api_routes.route("/api/players_misc")
def get_players_misc():
    try:
        with sqlite3.connect(TEAW_DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM players")
            total_players = cursor.fetchone()[0]

            # A player is considered active if they've logged in within the last 14 days
            fourteen_days_ago_ms = (int(time.time()) - (14 * 24 * 60 * 60)) * 1000
            cursor.execute("""
                SELECT COUNT(*)
                FROM players
                WHERE last_online >= ?
            """, (fourteen_days_ago_ms,))
            active_players = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(balance) FROM players")
            total_money = int(cursor.fetchone()[0]) or 0

        return {
            "total_players": total_players,
            "active_players": active_players,
            "total_money": total_money,
        }, 200
    except Exception:
        log.error(f"Internal error getting `players_misc`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500


# Towns
@api_routes.route("/api/towns")
def get_all_towns():
    try:
        return "ok", 200
    except Exception:
        log.error(f"Internal error getting `towns`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500


# Chat
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

            chat_messages = []

            for row in cursor.fetchall():   # Prevents HTML injection
                sanitized_message = bleach.clean(row["message"], tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
                chat_messages.append({
                    "id": row["id"],
                    "sender": row["sender"],
                    "sender_uuid": row["sender_uuid"],
                    "message": sanitized_message,
                    "timestamp": row["timestamp"],
                    "type": row["type"],
                })

        chat_messages.reverse()

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



# Skins
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



# Showcase
@api_routes.route("/api/submit_photo", methods=["POST"])
def submit_build():
    try:
        os.makedirs(SHOWCASE_SUBMISSIONS_DIR, exist_ok=True)

        photo_title = request.form.get("photo-title")
        photo_date = request.form.get("photo-date")
        photographer = request.form.get("photographer")

        # Validate form data
        if not photo_title or not photo_date or not photographer:
            return jsonify({"error": "Missing required form data"}), 400

        photo_file = request.files.get("photo-file")
        if not photo_file:
            return jsonify({"error": "No file provided"}), 400

        if len(photo_file.read()) > 10 * 1024 * 1024:  # 10 MB limit
            return jsonify({"error": "File size exceeds limit"}), 400
        photo_file.seek(0)

        # Clean the file name
        extension = os.path.splitext(photo_file.filename)[1].lower()
        sanitized_title = photo_title.replace(" ", "_").strip()
        file_name = f"{sanitized_title}_{photo_date}{extension}"

        # Ensure folder name is unique
        base_folder_name = f"{sanitized_title}_{photo_date}".strip()
        folder_name = base_folder_name
        folder_path = os.path.join(SHOWCASE_SUBMISSIONS_DIR, folder_name)
        while os.path.exists(folder_path):
            folder_name = f"{base_folder_name}_{uuid.uuid4().hex[:8]}"  # autism but it works
            folder_path = os.path.join(SHOWCASE_SUBMISSIONS_DIR, folder_name)

        os.makedirs(folder_path, exist_ok=True)

        # Save the image and metadata
        image_metadata = {
            "photo_title": photo_title,
            "photo_date": photo_date,
            "photographer": photographer,
            "img_src": f"imgs/showcase_imgs/{file_name}"
        }
        with open(os.path.join(folder_path, "data.json"), "w") as json_file:
            json.dump(image_metadata, json_file, indent=4)

        photo_file_path = os.path.join(folder_path, file_name)
        photo_file.save(photo_file_path)

        log.info(f"Submission saved in folder: {folder_name}")

        return jsonify({"message": "Submission successful"}), 200
    except Exception:
        log.error(f"Error processing showcase submission: {traceback.format_exc()}")
        return jsonify({"error": "internal error"}), 500
    
@api_routes.route("/api/showcase_manifest")
def get_showcase_manifest():
    try:
        with open("../db/showcase_imgs/showcase_manifest.json", "r") as file:
            return jsonify(json.load(file)), 200
    except Exception:
        log.error(f"Error getting `showcase_submissions`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500

@api_routes.route("/api/showcase_img/<file_name>")
def get_showcase_img(file_name):
    try:

        print(SHOWCASE_IMAGES_DIR, file_name)
        return send_from_directory(SHOWCASE_IMAGES_DIR, file_name)
    except NotFound:
        print(traceback.format_exc())
        return "not found", 404
        
    except Exception:
        log.error(f"Internal error getting `showcase_img`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500
    

# Fishing
@api_routes.route("/api/fishing_leaderboard")
def get_fishing_leaderboard():
    try:
        with sqlite3.connect(STATS_DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT player_uuid, stat_value
                FROM player_statistics
                WHERE category = 'general' AND stat_key = 'FISH_CAUGHT'
                ORDER BY stat_value DESC
                LIMIT 10
            """)
            leaderboard = [{"uuid": row[0], "fish_caught": row[1]} for row in cursor.fetchall()]

        return jsonify(leaderboard), 200
    except Exception:
        log.error(f"Internal error getting `fishing_leaderboard`: {traceback.format_exc()}")
        return {"error": "internal error"}, 500
