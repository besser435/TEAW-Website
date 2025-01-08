from flask import Blueprint, jsonify, send_from_directory, request
from werkzeug.exceptions import NotFound
import sqlite3
import traceback
import time
import bleach
import os
import json
import uuid

from config import log, TEAW_DB_FILE, STATS_DB_FILE, PLAYER_FACE_SKIN_DIR

stats_routes = Blueprint("stats_blueprint", __name__)


# Minecraft stores stat values that are machine readable, but not human readable.
# We need to translate things like ticks to hours. These functions will do that.
# Result translations
def count(count):
    return int(count), "quantity"

def ticks_to_hours(ticks):
    return f"{ticks / 20 / 60 / 60:.1f}", "hours"

def cm_to_km(cm):
    return f"{cm / 100_000:.3f}", "kilometers"


# This lists queryable stats, and what translation to use for the result. The comments are what appears in game.
# Note that this is kind of goofy. You will call for a stat key, but the result will be translated into different units.
AVAILABLE_GENERAL_STATS = {
    "DEATHS": count,                        # Number of deaths
    "TIME_SINCE_DEATH": ticks_to_hours,     # Time since last death
    "PLAYER_KILLS": count,                  # Player kills
    "TOTAL_WORLD_TIME": ticks_to_hours,     # Time played
    "PIG_ONE_CM": cm_to_km,                 # Distance by pig
    "ANIMALS_BRED": count,                  # Animals bred
    "CAKE_SLICES_EATEN": count,             # Cake slices eaten
    "CRAFTING_TABLE_INTERACTION": count,    # Interactions with crafting table
    "TRADED_WITH_VILLAGER": count,          # Traded with villagers
    "SLEEP_IN_BED": count                   # Times slept in a bed
}

# AVAILABLE_CUSTOM_STATS = {
#     "PLAYTIME_DEATH_RATIO": count,
#     "TOTAL_BLOCKS_BROKEN": count
# }


# Helper functions
def get_name_and_skin(uuid):
    with sqlite3.connect(TEAW_DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT name FROM players WHERE uuid = ?""", (uuid,))
        name = cursor.fetchone()
        name = name[0] if name else "Unknown"

    skin = 0
    return name, skin


# General stats
@stats_routes.route("/api/get_general_leaderboard/<stat>")
def get_stats_leaderboard(stat):
    try:
        stat = stat.upper()
        if stat not in AVAILABLE_GENERAL_STATS:
            return {"error": "invalid stat key"}, 400

        stat_translation = AVAILABLE_GENERAL_STATS[stat]

        # We should really join the stats.db and teaw.db into one database
        with sqlite3.connect(STATS_DB_FILE) as stats_conn, sqlite3.connect(TEAW_DB_FILE) as teaw_conn:
            stats_cursor = stats_conn.cursor()
            teaw_cursor = teaw_conn.cursor()

            # Query the stats leaderboard
            stats_cursor.execute("""
                SELECT player_uuid, stat_value
                FROM player_statistics
                WHERE category = 'general' AND stat_key = ?
                ORDER BY stat_value DESC
                LIMIT 500
            """, (stat,))

            leaderboard = []
            units = None
            for row in stats_cursor.fetchall():
                player_uuid, stat_value = row
                translated_value, stat_unit = stat_translation(stat_value)
                units = stat_unit

                # Get the player name from the teaw.db players table
                teaw_cursor.execute("""
                    SELECT name
                    FROM players
                    WHERE uuid = ?
                """, (player_uuid,))
                player_name = teaw_cursor.fetchone()
                player_name = player_name[0] if player_name else "Unknown"

                leaderboard.append({
                    "uuid": player_uuid,
                    "name": player_name,
                    "value": translated_value
                })

        return jsonify({"units": units, "leaderboard": leaderboard}), 200
    except Exception:
        log.error(f"Internal error getting `stats_leaderboard` for stat '{stat}': {traceback.format_exc()}")
        return {"error": "internal error"}, 500


# Custom stats
# def get_playtime_death_ratio():
#     return 0

# def get_total_blocks_broken():
#     return 0


# @stats_routes.route("/api/get_custom_stat/<stat>")
# def handle_custom_stat(stat):
#     try:
#         stat = stat.upper()
#         if stat not in AVAILABLE_CUSTOM_STATS:
#             return {"error": "invalid stat key"}, 400
        
#         if stat == "PLAYTIME_DEATH_RATIO":
#             value = get_playtime_death_ratio()
#         elif stat == "TOTAL_BLOCKS_BROKEN":
#             value = get_total_blocks_broken()

#         return jsonify({"value": value}), 200

#     except Exception:
#         log.error(f"Internal error handling custom_stat for stat '{stat}': {traceback.format_exc()}")
#         return {"error": "internal error"}, 500
       


# Fishing (Hosted on USAI.net)
@stats_routes.route("/api/fishing_leaderboard")
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

