import sqlite3
import json
import os
import requests
import time
import sys
import traceback
import logging
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Python not looking in parent directories for common files you might want to use is stupid
sys.path.append("../")
from diet_logger import setup_logger


LOG_LEVEL = logging.DEBUG
LOG_FILE = "../logs/stats_updater.log"
DB_FILE = "../db/stats.db"
TAPI_URL = "https://tapi.toendallwars.org/api"
    


class BadGatewayError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


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


# TODO: 
# Restart the script every 2 hours in case the internet goes out.
# When the internet comes back, it has a bug where it will stop updating.

if __name__ == "__main__":  # autism
    try:
        log = setup_logger(LOG_FILE, LOG_LEVEL)
        log.info("---- Starting Stats Updater ----")

        while True: 
            start_time = time.time()

            response = requests.get(TAPI_URL + "/online_players")
            if response.status_code == 200:
                data = response.json()
                online_players = data.get("online_players", {})

                for uuid, player_data in online_players.items():
                    stats_url = f"{TAPI_URL}/full_player_stats/{uuid}"
                    stats_response = requests.get(stats_url, timeout=20)

                    if stats_response.status_code == 200:
                        stats_json = stats_response.json()
                        insert_statistics(uuid, stats_json)
                        log.debug(f"Updated player stats for {player_data['name']} ({uuid})")
                    elif response.status_code == 404:   # Player logged out before we could fetch stats. This is fine.
                        log.info(f"Attempted to fetch stats for {uuid} who is now offline. Skipping.")
                    else:
                        log.warning(f"Failed to fetch stats for {uuid}. HTTP {stats_response.status_code}")
            elif response.status_code == 502:
                raise BadGatewayError("TAPI server returned 502 Bad Gateway. Is server offline or restarting?")
            else:
                log.warning(f"Failed to fetch online players. HTTP {response.status_code}")

            end_time = time.time()  
            # Print to not fill log file
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Time to update stats DB was {round((end_time - start_time) * 1000, 3)}ms")
            time.sleep(15)

    # This generally isn't a thing anymore, as its now behind Cloudflare. CF will return 502 instead of this throwing an error.
    # This still happens on occasion however, so we still catch it.
    except (BadGatewayError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        # When TEAW restarts, it can rarely cause requests to not be able to reconnect
        # This should restart the script and fix the issue, hopefully.
        # We dont log the error, as its probably just TEAW restarting

        log.info(f"Connection timed out. Restarting in 30s")

        time.sleep(30)

        log.info("Restarting script (timeout)...")
        os.execl(sys.executable, sys.executable, *sys.argv) 

    except Exception:
        log.error(traceback.format_exc())
        time.sleep(30)

        log.info("Restarting script (general exception)...")
        os.execl(sys.executable, sys.executable, *sys.argv) 

    except KeyboardInterrupt:
        pass