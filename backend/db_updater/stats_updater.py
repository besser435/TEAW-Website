import sqlite3
import json
import os
import requests
import time
import sys
import traceback
import logging

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from diet_logger import setup_logger

LOG_LEVEL = logging.DEBUG
LOG_FILE = "log/stats_updater.log"
DB_FILE = "db/stats.db"
TAPI_URL = "http://192.168.0.157:1850/api"


def create_stats_table(db_file=DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_statistics (
                player_uuid TEXT NOT NULL,         -- UUID of the player
                category TEXT NOT NULL,            -- Category of the statistic (e.g., 'general', 'mob', 'item')
                stat_key TEXT NOT NULL,            -- The name of the statistic (e.g., 'DAMAGE_DEALT', 'KILL_ENTITY:FROG')
                stat_value INTEGER NOT NULL,       -- The value of the statistic
                PRIMARY KEY (player_uuid, category, stat_key)
            )
        """)

    log.info("Created player_statistics table")


def drop(db_file=DB_FILE, table=None):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        conn.commit()

    log.info(f"Dropped table {table}")


def get_stat(player_uuid, category, stat_key):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT stat_value
            FROM player_statistics
            WHERE player_uuid = ? AND category = ? AND stat_key = ?
        """, (player_uuid, category, stat_key))

        result = cursor.fetchone()
        return result[0] if result else None
    

def get_all_stats(player_uuid):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, stat_key, stat_value
            FROM player_statistics
            WHERE player_uuid = ?
        """, (player_uuid,))

        return cursor.fetchall()


def insert_statistics(player_uuid, stats_json):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        for category, stats in stats_json.items():
            if isinstance(stats, dict):
                for key, value in stats.items():
                    if isinstance(value, dict):  # Handle nested keys
                        for sub_key, sub_value in value.items():
                            stat_key = f"{key}:{sub_key}"
                            cursor.execute("""
                                INSERT INTO player_statistics (player_uuid, category, stat_key, stat_value)
                                VALUES (?, ?, ?, ?)
                                ON CONFLICT(player_uuid, category, stat_key) DO UPDATE SET stat_value = excluded.stat_value
                            """, (player_uuid, category, stat_key, sub_value))
                    else:  # Flat key-value pairs
                        cursor.execute("""
                            INSERT INTO player_statistics (player_uuid, category, stat_key, stat_value)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(player_uuid, category, stat_key) DO UPDATE SET stat_value = excluded.stat_value
                        """, (player_uuid, category, key, value))
        conn.commit()


if __name__ == "__main__":  # autism
    try:
        log = setup_logger(LOG_FILE, LOG_LEVEL)
        #drop(table="player_statistics")
        #create_stats_table()
        while True: 
            start_time = time.time()

            response = requests.get(TAPI_URL + "/online_players")
            if response.status_code == 200:
                data = response.json()
                online_players = data.get("online_players", {})

                for uuid, player_data in online_players.items():
                    stats_url = f"{TAPI_URL}/full_player_stats/{uuid}"
                    stats_response = requests.get(stats_url)

                    if stats_response.status_code == 200:
                        stats_json = stats_response.json()
                        insert_statistics(uuid, stats_json)
                        log.debug(f"Updated player stats for {player_data['name']} ({uuid})")
                    else:
                        log.warning(f"Failed to fetch stats for {uuid}. HTTP {stats_response.status_code}")
            else:
                print(f"Failed to fetch online players. HTTP {response.status_code}")

            end_time = time.time()  
            log.debug(f"Player stats updated in {round((end_time - start_time) * 1000, 3)}ms")
            time.sleep(5)
    except requests.exceptions.ConnectTimeout as e:
        # When TEAW restarts, it can rarely cause requests to not be able to reconnect
        # This should restart the script and fix the issue, hopefully.
        # We dont log the error, as its probably just TEAW restarting

        log.info(f"Connection timed out. {e}")

        time.sleep(30)

        log.info("Restarting script...")
        os.execl(sys.executable, sys.executable, *sys.argv) 

    except Exception:
        log.error(traceback.format_exc())
        time.sleep(30)

        log.info("Restarting script...")
        os.execl(sys.executable, sys.executable, *sys.argv) 

    except KeyboardInterrupt:
        pass