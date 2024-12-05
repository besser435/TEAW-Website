import sqlite3
import requests
import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
import sys
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Python not looking in parent directories for common files you might want to use is stupid
sys.path.append("../")
from diet_logger import setup_logger


LOG_LEVEL = logging.DEBUG
LOG_FILE = "../logs/db_updater.log"

TAPI_URL = "http://192.168.0.157:1850/api"
DB_FILE = "../db/teaw.db"

SKIN_API_URL = "https://starlightskins.lunareclipse.studio/render/ultimate/{uuid}/full"
SKINS_DIR = "../db/player_skins"
SKIN_TTL_HOURS = 8



def upsert_variable(variable: str, value: str) -> None:    # the shitfuck
    """
    Upserts a value in the miscellaneous `variables` table.
    Variable names and values are stored as the `TEXT` type.
    """

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO variables (variable, value)
            VALUES (?, ?)
            ON CONFLICT(variable) DO UPDATE SET 
                value = excluded.value
        """, (str(variable), str(value)))

        conn.commit()


def update_players_table() -> None:
    log.debug("Updating players table...")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        response = requests.get(TAPI_URL + "/online_players")

        start_time = time.time()
        if response.status_code == 200:
            data = response.json()
            online_players = data.get("online_players", {})

            for uuid, player_data in online_players.items():
                name = player_data.get("name")
                online_duration = player_data.get("online_duration", 0)
                afk_duration = player_data.get("afk_duration", 0)
                balance = player_data.get("balance", 0.0)
                title = player_data.get("title")
                town = player_data.get("town")
                town_name = player_data.get("town_name")
                nation = player_data.get("nation")
                nation_name = player_data.get("nation_name")
                last_online = int(time.time() * 1000)   # convert to ms, as that is what we do everywhere

                # NOTE: online_duration and afk_duration can still be non-zero even if the player is offline
                cursor.execute("""
                    INSERT INTO players (
                        uuid, name, online_duration, afk_duration, balance, 
                        title, town, town_name, nation, nation_name, last_online
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?
                    ) ON CONFLICT(uuid) DO UPDATE SET
                        name = excluded.name,
                        online_duration = excluded.online_duration,
                        afk_duration = excluded.afk_duration,
                        balance = excluded.balance,
                        title = excluded.title,
                        town = excluded.town,
                        town_name = excluded.town_name,
                        nation = excluded.nation,
                        nation_name = excluded.nation_name,
                        last_online = excluded.last_online
                """, (uuid, name, online_duration, afk_duration, balance, title, town, town_name, nation, nation_name, last_online))

            conn.commit()
            upsert_variable("last_players_update", int(time.time() * 1000))
        else:
            log.warning(f"Failed to fetch player data: {response.status_code}")

    end_time = time.time()
    log.debug(f"Players table updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time


def update_chat_table() -> None:
    log.debug("Updating chat table...")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        response = requests.get(TAPI_URL + "/chat_history")

        start_time = time.time()
        
        cursor.execute("SELECT MAX(timestamp) FROM chat")
        last_timestamp = cursor.fetchone()[0] or 0  # Default to 0 if no messages exist

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
            upsert_variable("last_chat_update", int(time.time() * 1000))
        else:
            log.warning(f"Failed to fetch chat data: {response.status_code}")

    end_time = time.time()
    log.debug(f"Chat table updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time


def update_towns_table() -> None:
    log.debug("Updating towns table...")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        response = requests.get(TAPI_URL + "/towny")

        start_time = time.time()
        if response.status_code == 200:
            data = response.json()
            towns = data.get("towns", {})

            for town_uuid, town_data in towns.items():
                resident_tax_percent = town_data.get("resident_tax_percent", 0.0)
                is_active = town_data.get("is_active", False)
                balance = town_data.get("balance", 0.0)
                nation = town_data.get("nation")
                nation_name = town_data.get("nation_name")
                mayor = town_data.get("mayor")
                founder = town_data.get("founder")
                name = town_data.get("name")
                founded = town_data.get("founded")
                claimed_chunks = town_data.get("claimed_chunks", 0)
                tag = town_data.get("tag")
                board = town_data.get("board")


                cursor.execute("""
                    INSERT INTO towns (
                        uuid, name, mayor, founder, balance, nation, nation_name, founded, resident_tax_percent, 
                        is_active, claimed_chunks, tag, board
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(uuid) DO UPDATE SET
                        name=excluded.name,
                        mayor=excluded.mayor,
                        founder=excluded.founder,
                        balance=excluded.balance,
                        nation=excluded.nation,
                        founded=excluded.founded,
                        resident_tax_percent=excluded.resident_tax_percent,
                        is_active=excluded.is_active,
                        claimed_chunks=excluded.claimed_chunks,
                        tag=excluded.tag,
                        board=excluded.board
                """, (town_uuid, name, mayor, founder, balance, nation, nation_name, founded, resident_tax_percent, 
                    is_active, claimed_chunks, tag, board))

            conn.commit()
            upsert_variable("last_towns_update", int(time.time() * 1000))
        else:
            log.warning(f"Failed to fetch town data: {response.status_code}")

    end_time = time.time()
    log.debug(f"Towns table updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time


def update_nations_table() -> None:
    log.debug("Updating nations table...")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        response = requests.get(TAPI_URL + "/towny")

        start_time = time.time()
        if response.status_code == 200:
            data = response.json()
            nations = data.get("nations", {})

            for nation_id, nation_data in nations.items():
                leader = nation_data.get("leader")
                capitol_town = nation_data.get("capitol_town")
                capitol_town_name = nation_data.get("capitol_town_name")
                balance = nation_data.get("balance", 0.0)
                town_tax_dollars = nation_data.get("town_tax_dollars", 0.0)
                name = nation_data.get("name")
                founded = nation_data.get("founded")
                tag = nation_data.get("tag")
                board = nation_data.get("board")

                cursor.execute("""
                    INSERT INTO nations (
                        uuid, name, leader, capitol_town, capitol_town_name, balance, 
                        town_tax_dollars, founded, tag, board
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(uuid) DO UPDATE SET
                        name=excluded.name,
                        leader=excluded.leader,
                        capitol_town=excluded.capitol_town,
                        capitol_town_name=excluded.capitol_town_name,
                        balance=excluded.balance,
                        town_tax_dollars=excluded.town_tax_dollars,
                        founded=excluded.founded,
                        tag=excluded.tag,
                        board=excluded.board
                """, (
                    nation_id, name, leader, capitol_town, capitol_town_name, balance, 
                    town_tax_dollars, founded, tag, board
                ))

            conn.commit()
            upsert_variable("last_nations_update", int(time.time() * 1000))
        else:
            log.warning(f"Failed to fetch nation data: {response.status_code}")
    

    end_time = time.time()
    log.debug(f"Nations table updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time


def update_skins_dir() -> None:
    log.debug("Updating player skins...")

    start_time = time.time()

    os.makedirs(SKINS_DIR, exist_ok=True)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT uuid FROM players")
        players = cursor.fetchall()

    current_time = time.time()

    for (uuid,) in players:
        skin_path = os.path.join(SKINS_DIR, f"{uuid}.png")

        if os.path.exists(skin_path):
            last_modified_time = os.path.getmtime(skin_path)
            if current_time - last_modified_time < SKIN_TTL_HOURS * 3600:
                continue    # Skip if skin is still fresh

        response = requests.get(SKIN_API_URL.format(uuid=uuid), timeout=10)

        if response.status_code == 200:
            try:
                response_data = response.json()
                if "error" in response_data:    # stupid fucking API returns 200 even if there is an error
                    log.warning(f"Failed to fetch skin for UUID {uuid}: {response_data['error']}")
                    continue
            except json.JSONDecodeError:
                pass
        
            with open(skin_path, "wb") as skin_file:
                skin_file.write(response.content)
            log.debug(f"Updated skin for UUID: {uuid}")
        else:
            log.warning(f"Failed to fetch skin for UUID {uuid}: HTTP {response.status_code}")


    end_time = time.time()
    log.debug(f"Player skins updated in {round((end_time - start_time) * 1000, 3)}ms")   # Includes network request time


def update_misc_variables() -> None:
    log.debug("Updating server info...")

    response = requests.get(TAPI_URL + "/server_info")

    start_time = time.time()

    if response.status_code == 200:
        data = response.json()
        weather = data.get("weather")
        world_time_24h = data.get("world_time_24h")

        teaw_system_time = data.get("system_time")

        # because 3 discrete DB operations is better than one, right?
        upsert_variable("weather", weather)
        upsert_variable("world_time_24h", world_time_24h)
        upsert_variable("teaw_system_time", teaw_system_time)
    else:
        log.warning(f"Failed to fetch server info: {response.status_code}")

    end_time = time.time()
    log.debug(f"Server info updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time



if __name__ == "__main__":
    try:
        log = setup_logger(LOG_FILE, LOG_LEVEL)
        while True: 
            """TODO: 
            Should be async, so we can have different intervals for different tasks.
            chat should be updated frequently, but towns only needs to be ran every few minutes.

            Should raise an error if an update takes longer than a few hundred milliseconds
            """

            update_players_table()
            update_chat_table()
            update_towns_table()
            update_nations_table()
            update_misc_variables()

            update_skins_dir()

            print(f"Updated info at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            time.sleep(5)
    except requests.exceptions.ConnectTimeout as e:
        # When TEAW restarts, it can rarely cause requests to not be able to reconnect.
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