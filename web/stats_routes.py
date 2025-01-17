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


# Helper functions
def count(count):
    return int(count), "quantity"

def ticks_to_hours(ticks):
    return f"{ticks / 20 / 60 / 60:.1f}", "hours"

def cm_to_km(cm):
    return f"{cm / 100_000:.3f}", "kilometers"

def get_name(uuid):
    with sqlite3.connect(TEAW_DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT name FROM players WHERE uuid = ?""", (uuid,))
        name = cursor.fetchone()
        name = name[0] if name else "Unknown"

    return name



# General stats
# This lists queryable stats, and what translation to use for the result. The comments are what appears in game.
# Note that this is kind of goofy. You will call for a stat key, but the result will be translated into different units.
AVAILABLE_GENERAL_STATS = {
    # Key, (stat translation function)
    "DEATHS": count,                        # Number of deaths
    "TIME_SINCE_DEATH": ticks_to_hours,     # Time since last death
    "PLAYER_KILLS": count,                  # Player kills
    "TOTAL_WORLD_TIME": ticks_to_hours,     # Time played
    "PIG_ONE_CM": cm_to_km,                 # Distance by pig
    "ANIMALS_BRED": count,                  # Animals bred
    "CAKE_SLICES_EATEN": count,             # Cake slices eaten
    "CRAFTING_TABLE_INTERACTION": count,    # Interactions with crafting table
    "TRADED_WITH_VILLAGER": count,          # Traded with villagers
    "SLEEP_IN_BED": count,                  # Times slept in a bed
    "FISH_CAUGHT": count                    # Fish caught
}


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
def get_playtime_death_ratio():
    try:
        with sqlite3.connect(STATS_DB_FILE) as stats_conn, sqlite3.connect(TEAW_DB_FILE) as teaw_conn:
            stats_cursor = stats_conn.cursor()
            teaw_cursor = teaw_conn.cursor()
            
            stats_cursor.execute("""
                SELECT p1.player_uuid, 
                       CAST(p1.stat_value AS FLOAT) as playtime, 
                       CAST(COALESCE(p2.stat_value, 0) AS FLOAT) as deaths
                FROM player_statistics p1
                LEFT JOIN player_statistics p2 
                    ON p1.player_uuid = p2.player_uuid 
                    AND p2.category = 'general' 
                    AND p2.stat_key = 'DEATHS'
                WHERE p1.category = 'general' 
                AND p1.stat_key = 'TOTAL_WORLD_TIME'
            """)
            
            player_stats = []
            for row in stats_cursor.fetchall():
                player_uuid, playtime, deaths = row
                
                # Convert ticks to hours
                hours = playtime / 20 / 60 / 60
                
                # If no deaths, ratio is just their playtime
                if deaths == 0:
                    ratio = hours  
                else:
                    ratio = hours / deaths
                
                # Get player name
                teaw_cursor.execute("""
                    SELECT name FROM players WHERE uuid = ?
                """, (player_uuid,))
                player_name = teaw_cursor.fetchone()
                player_name = player_name[0] if player_name else "Unknown"
                
                player_stats.append({
                    "uuid": player_uuid,
                    "name": player_name,
                    "value": f"{ratio:.1f}"
                })
            
            player_stats.sort(key=lambda x: float(x["value"]), reverse=True)
            
            return player_stats
    except Exception:
        log.error(f"Error calculating playtime/death ratio: {traceback.format_exc()}")
        return []


AVAILABLE_CUSTOM_STATS = {
    "PLAYTIME_DEATH_RATIO": (get_playtime_death_ratio, "avg. hours per death")
}

@stats_routes.route("/api/get_custom_stat/<stat>")
def handle_custom_stat(stat):
    try:
        stat = stat.upper()
        if stat not in AVAILABLE_CUSTOM_STATS:
            return {"error": "invalid stat key"}, 400

        stat_function, units = AVAILABLE_CUSTOM_STATS[stat]
        
        leaderboard = stat_function()

        return jsonify({
            "units": units,
            "leaderboard": leaderboard
        }), 200

    except Exception:
        log.error(f"Internal error handling custom_stat for stat '{stat}': {traceback.format_exc()}")
        return {"error": "internal error"}, 500



# Fishing (Hosted on a different website)
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
