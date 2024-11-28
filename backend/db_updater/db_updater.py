import sqlite3
import requests
import time
from datetime import datetime
import json
import os
import traceback
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

DB_FILE = "teaw.db"
TAPI_URL = "http://192.168.0.157:1850/api"
ERROR_LOG = "errors.log"


def update_players_table() -> None:
    print("Updating players table")
    start_time = time.time()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    response = requests.get(TAPI_URL + "/online_players")
    if response.status_code == 200:
        data = response.json()
        online_players = data.get("online_players", {})

        for uuid, player_data in online_players.items():
            name = player_data.get("name")
            online_duration = player_data.get("online_duration", 0)
            afk_duration = player_data.get("afk_duration", 0)
            balance = player_data.get("balance", 0.0)
            title = player_data.get("title")
            town_name = player_data.get("town_name")
            nation_name = player_data.get("nation_name")
            last_online = int(time.time() * 1000)   # convert to ms, as that is what we do everywhere

            # NOTE: online_duration and afk_duration can still be non-zero even if the player is offline
            cursor.execute("""
                INSERT INTO players (
                    uuid, name, online_duration, afk_duration, balance, 
                    title, town_name, nation_name, last_online
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                ) ON CONFLICT(uuid) DO UPDATE SET   -- Upsert if the player already exists
                    name = excluded.name,
                    online_duration = excluded.online_duration,
                    afk_duration = excluded.afk_duration,
                    balance = excluded.balance,
                    title = excluded.title,
                    town_name = excluded.town_name,
                    nation_name = excluded.nation_name,
                    last_online = excluded.last_online
            """, (uuid, name, online_duration, afk_duration, balance, title, town_name, nation_name, last_online))

        conn.commit()
    else:
        print(f"Failed to fetch player data: {response.status_code}")
    conn.close()

    end_time = time.time()
    print(f"Players table updated in {round((end_time - start_time) * 1000, 3)}ms\n")


def update_chat_table() -> None:
    print("Updating chat table")
    start_time = time.time()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(timestamp) FROM chat")
    last_timestamp = cursor.fetchone()[0] or 0  # Default to 0 if no messages exist


    response = requests.get(TAPI_URL + "/chat_history")
    if response.status_code == 200:
        chat_data = response.json()

        for chat_entry in chat_data:
            sender = chat_entry.get("sender")
            message = chat_entry.get("message")
            timestamp = chat_entry.get("timestamp")
            message_type = chat_entry.get("type")

            
            if timestamp > last_timestamp:
                # TAPI will return the same messages over and over, so we only insert new ones.
                # Since we rely on milliseconds and not some other key, we need to ensure TAPI has 
                # precision to the millisecond so the same message isn't inserted multiple times.
                cursor.execute("""
                    INSERT INTO chat (sender, message, timestamp, type)
                    VALUES (?, ?, ?, ?)
                """, (sender, message, timestamp, message_type))

        conn.commit()
    else:
        print(f"Failed to fetch chat data: {response.status_code}")
    conn.close()

    end_time = time.time()
    print(f"Chat table updated in {round((end_time - start_time) * 1000, 3)}ms\n")



def log_error(error: str) -> None:
    error_string = f"Error at time {datetime.now()}\n{error}\n\n"
    with open (ERROR_LOG, "a") as f:
        f.write(error_string)

    print(error_string)


if __name__ == "__main__":
    try:
        while True: 
            # TODO: should be async, so we can have different intervals for different tasks.
            # chat should be updated frequently, but towns only needs to be ran every few minutes.
            update_players_table()
            update_chat_table()
            

            time.sleep(5)
    except Exception:
        log_error(traceback.format_exc())

        time.sleep(30)

        # When TEAW restarts, it can rarely cause requests to not be able to reconnect
        # This should restart the script and fix the issue, hopefully
        print("Restarting script...")
        os.execl(sys.executable, sys.executable, *sys.argv) 

    except KeyboardInterrupt:
        pass