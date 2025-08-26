import sqlite3
import requests
import time
from datetime import datetime
import logging
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

TAPI_URL = "https://tapi.toendallwars.org/api"
#TAPI_URL = "http://192.168.0.157:1850/api"
DB_FILE = "../db/teaw.db"

SKIN_TTL_HOURS = 8
BODY_SKIN_API_URL = "https://starlightskins.lunareclipse.studio/render/ultimate/{uuid}/full?capeEnabled=false"
BODY_SKINS_DIR = "../db/player_body_skins"

FACE_SKIN_API_URL = "https://mc-heads.net/avatar/{uuid}/8"   # Should really just use the Mojang API
FACE_SKINS_DIR = "../db/player_face_skins"



class BadGatewayError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


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
        response = requests.get(TAPI_URL + "/online_players", timeout=20)
        log.debug("Got response from TAPI")

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
            log.debug("Executed SQL commands")

            # Offline players should have their online_duration reset to 0
            cursor.execute("""
                UPDATE players
                SET online_duration = 0
                WHERE uuid NOT IN (
                    SELECT value FROM json_each(?)
                )
            """, (json.dumps(list(online_players.keys())),))
            log.debug("Executed SQL commands")

            conn.commit()
            log.debug("Committed SQL commands")

            upsert_variable("last_players_update", int(time.time() * 1000))
            log.debug("Updated last_players_update variable")

        elif response.status_code == 502:
            raise BadGatewayError("TAPI server returned 502 Bad Gateway. Is server offline or restarting?")
        else:
            log.warning(f"Failed to fetch player data: {response.status_code}")

    end_time = time.time()
    log.debug(f"Players table updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time


def update_chat_table() -> None:
    log.debug("Updating chat table...")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        response = requests.get(TAPI_URL + "/chat_history", timeout=20)
        log.debug("Got response from TAPI")

        start_time = time.time()
        
        cursor.execute("SELECT MAX(timestamp) FROM chat")
        last_timestamp = cursor.fetchone()[0] or 0  # Default to 0 if no messages exist

        if response.status_code == 200:
            chat_data = response.json()

            for chat_entry in chat_data:
                sender = chat_entry.get("sender")
                sender_uuid = chat_entry.get("sender_uuid")
                message = chat_entry.get("message")
                timestamp = chat_entry.get("timestamp")
                message_type = chat_entry.get("type")

                if message.lower() == "playerlist": continue

                
                if timestamp > last_timestamp:
                    # TAPI will return the same messages over and over, so we only insert new ones.
                    # Since we rely on milliseconds and not some other key, we need to ensure TAPI has 
                    # precision to the millisecond so the same message isn't inserted multiple times.
                    cursor.execute("""
                        INSERT INTO chat (sender, sender_uuid, message, timestamp, type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (sender, sender_uuid, message, timestamp, message_type))
            log.debug("Executed SQL commands")

            conn.commit()
            log.debug("Committed SQL commands")
            upsert_variable("last_chat_update", int(time.time() * 1000))
        elif response.status_code == 502:
            raise BadGatewayError("TAPI server returned 502 Bad Gateway. Is server offline or restarting?")
        else:
            log.warning(f"Failed to fetch chat data: {response.status_code}")

    end_time = time.time()
    log.debug(f"Chat table updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time


def update_towns_table() -> None:
    log.debug("Updating towns table...")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        response = requests.get(TAPI_URL + "/towny", timeout=20)
        log.debug("Got response from TAPI")

        start_time = time.time()
        if response.status_code == 200:
            data = response.json()
            towns = data.get("towns", {})


            # Purge towns that no longer exist
            api_town_uuids = set(towns.keys())

            cursor.execute("SELECT uuid FROM towns")
            db_town_uuids = {row[0] for row in cursor.fetchall()}

            towns_to_delete = db_town_uuids - api_town_uuids
            if towns_to_delete:
                cursor.executemany("DELETE FROM towns WHERE uuid = ?", [(uuid,) for uuid in towns_to_delete])
                log.info(f"Removed {len(towns_to_delete)} towns no longer present in the API")
            log.debug("Executed SQL commands")

            # Update/insert town data
            for town_uuid, town_data in towns.items():
                resident_tax_percent = town_data.get("resident_tax", 0.0)
                is_active = town_data.get("is_active", False)
                balance = town_data.get("balance", 0.0)
                nation = town_data.get("nation")
                nation_name = town_data.get("nation_name")
                mayor = town_data.get("mayor")
                founder = town_data.get("founder")
                name = town_data.get("name")
                founded = town_data.get("founded")
                claimed_chunks = town_data.get("claimed_chunks", 0)
                color_hex = town_data.get("color_hex")
                tag = town_data.get("tag")
                board = town_data.get("board")
                spawn_loc_x = town_data.get("spawn_loc_x", 0)
                spawn_loc_z = town_data.get("spawn_loc_z", 0)
                spawn_loc_y = town_data.get("spawn_loc_y", 0)

                # Legacy note: TAPI now returns the tax as "resident_tax", but we still store it as "resident_tax_percent".
                # Will rename the column later :tm:
                cursor.execute("""
                    INSERT INTO towns (
                        uuid, name, mayor, founder, balance, nation, nation_name, founded, resident_tax_percent, 
                        is_active, claimed_chunks, color_hex, tag, board, spawn_loc_x, spawn_loc_z, spawn_loc_y
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(uuid) DO UPDATE SET
                        name=excluded.name,
                        mayor=excluded.mayor,
                        founder=excluded.founder,
                        balance=excluded.balance,
                        nation=excluded.nation,
                        nation_name=excluded.nation_name,
                        founded=excluded.founded,
                        resident_tax_percent=excluded.resident_tax_percent,
                        is_active=excluded.is_active,
                        claimed_chunks=excluded.claimed_chunks,
                        color_hex=excluded.color_hex,
                        tag=excluded.tag,
                        board=excluded.board,
                        spawn_loc_x=excluded.spawn_loc_x,
                        spawn_loc_z=excluded.spawn_loc_z,
                        spawn_loc_y=excluded.spawn_loc_y
                """, (town_uuid, name, mayor, founder, balance, nation, nation_name, founded, resident_tax_percent, 
                    is_active, claimed_chunks, color_hex, tag, board, spawn_loc_x, spawn_loc_z, spawn_loc_y))
            log.debug("Executed SQL commands")

            conn.commit()
            log.debug("Committed SQL commands")
            upsert_variable("last_towns_update", int(time.time() * 1000))
        elif response.status_code == 502:
            raise BadGatewayError("TAPI server returned 502 Bad Gateway. Is server offline or restarting?")
        else:
            log.warning(f"Failed to fetch town data: {response.status_code}")

    end_time = time.time()
    log.debug(f"Towns table updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time


def update_nations_table() -> None:
    log.debug("Updating nations table...")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        response = requests.get(TAPI_URL + "/towny", timeout=20)
        log.debug("Got response from TAPI")

        start_time = time.time()
        if response.status_code == 200:
            data = response.json()
            nations = data.get("nations", {})


            # Purge nations that no longer exist
            api_nation_uuids = set(nations.keys())

            cursor.execute("SELECT uuid FROM nations")
            db_nation_uuids = {row[0] for row in cursor.fetchall()}

            nations_to_delete = db_nation_uuids - api_nation_uuids
            if nations_to_delete:
                cursor.executemany("DELETE FROM nations WHERE uuid = ?", [(uuid,) for uuid in nations_to_delete])
                log.info(f"Removed {len(nations_to_delete)} nations no longer present in the API")
            log.debug("Executed SQL commands")

            # Update/insert nation data
            for nation_id, nation_data in nations.items():
                leader = nation_data.get("leader")
                capitol_town = nation_data.get("capitol_town")
                capitol_town_name = nation_data.get("capitol_town_name")
                balance = nation_data.get("balance", 0.0)
                town_tax_dollars = nation_data.get("town_tax_dollars", 0.0)
                name = nation_data.get("name")
                founded = nation_data.get("founded")
                color_hex = nation_data.get("color_hex", "000000")
                tag = nation_data.get("tag")
                board = nation_data.get("board")

                cursor.execute("""
                    INSERT INTO nations (
                        uuid, name, leader, capitol_town, capitol_town_name, balance, 
                        town_tax_dollars, founded, color_hex, tag, board
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(uuid) DO UPDATE SET
                        name=excluded.name,
                        leader=excluded.leader,
                        capitol_town=excluded.capitol_town,
                        capitol_town_name=excluded.capitol_town_name,
                        balance=excluded.balance,
                        town_tax_dollars=excluded.town_tax_dollars,
                        founded=excluded.founded,
                        color_hex=excluded.color_hex,
                        tag=excluded.tag,
                        board=excluded.board
                """, (
                    nation_id, name, leader, capitol_town, capitol_town_name, balance, 
                    town_tax_dollars, founded, color_hex, tag, board
                ))
            log.debug("Executed SQL commands")

            conn.commit()
            log.debug("Committed SQL commands")
            upsert_variable("last_nations_update", int(time.time() * 1000))
        elif response.status_code == 502:
            raise BadGatewayError("TAPI server returned 502 Bad Gateway. Is server restarting?")
        else:
            log.warning(f"Failed to fetch nation data: {response.status_code}")
    

    end_time = time.time()
    log.debug(f"Nations table updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time


def update_skin_dir(type) -> None:
    # Could honestly just store the face image in the players table. They are only about 160 bytes each.
    log.debug(f"Updating {type} skins...")

    start_time = time.time()

    os.makedirs(BODY_SKINS_DIR, exist_ok=True)
    os.makedirs(FACE_SKINS_DIR, exist_ok=True)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT uuid FROM players")
        players = cursor.fetchall()

    current_time = time.time()

    for (uuid,) in players:
        if type == "body": skin_path = os.path.join(BODY_SKINS_DIR, f"{uuid}.png")
        elif type == "face": skin_path = os.path.join(FACE_SKINS_DIR, f"{uuid}.png")

        if os.path.exists(skin_path):
            last_modified_time = os.path.getmtime(skin_path)
            if current_time - last_modified_time < SKIN_TTL_HOURS * 3600:
                continue    # Skip if skin is still fresh

        if type == "body": response = requests.get(BODY_SKIN_API_URL.format(uuid=uuid), timeout=20)
        elif type == "face": response = requests.get(FACE_SKIN_API_URL.format(uuid=uuid), timeout=20)

        if response.status_code == 200:
            with open(skin_path, "wb") as skin_file:
                skin_file.write(response.content)
            log.debug(f"Updated {type} skin for UUID: {uuid}")
        else:
            log.warning(f"Failed to fetch {type} skin for UUID {uuid}: HTTP {response.status_code}")


    end_time = time.time()
    log.debug(f"Player face skins updated in {round((end_time - start_time) * 1000, 3)}ms")   # Includes network request time


def update_server_info_table() -> None:
    log.debug("Updating server info...")

    response = requests.get(TAPI_URL + "/server_info", timeout=20)
    log.debug("Got response from TAPI")

    start_time = time.time()

    if response.status_code == 200:
        data = response.json()
        weather = data.get("weather")
        world_time_24h = data.get("world_time_24h")
        day = data.get("day")

        teaw_system_time = data.get("system_time")
        tapi_version = data.get("tapi_version")
        tapi_build = data.get("tapi_build")

        # because 3 discrete DB operations is better than one, right?
        upsert_variable("weather", weather)
        upsert_variable("world_time_24h", world_time_24h)
        upsert_variable("day", day)
        upsert_variable("teaw_system_time", teaw_system_time)
        upsert_variable("tapi_version", tapi_version)
        upsert_variable("tapi_build", tapi_build)
        log.debug("Updated variables")
    elif response.status_code == 502:
        raise BadGatewayError("TAPI server returned 502 Bad Gateway. Is server offline or restarting?")
    else:
        log.warning(f"Failed to fetch server info: {response.status_code}")

    end_time = time.time()
    log.debug(f"Server info updated in {round((end_time - start_time) * 1000, 3)}ms")   # Does not include network request time

# TODO: 
# Restart the script every 2 hours in case the internet goes out.
# When the internet comes back, it has a bug where it will stop updating.

if __name__ == "__main__":
    try:
        log = setup_logger(LOG_FILE, LOG_LEVEL)
        log.info("---- Starting DB Updater ----")

        while True: 
            """TODO: 
            Should be async, so we can have different intervals for different tasks.
            chat should be updated frequently, but towns only needs to be ran every few minutes.

            Should raise an error if an update takes longer than a few hundred milliseconds
            """

            start_time = time.time()

            update_players_table()
            update_chat_table()
            update_towns_table()
            update_nations_table()
            update_server_info_table()

            try:
                update_skin_dir("body")
                update_skin_dir("face")
            except Exception as e:  # Not super critical, sometimes the APIs go down
                log.warning(f"Failed to update skins: {e}")

            end_time = time.time()

            # Print to not fill log file
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Time to update general DB was {round((end_time - start_time) * 1000, 2)}ms")

            time.sleep(2)


    # This generally isn't a thing anymore, as its now behind Cloudflare. CF will return 502 instead of this throwing an error.
    # This still happens on occasion however, so we still catch it.
    except (BadGatewayError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        # When TEAW restarts, it can rarely cause requests to not be able to reconnect.
        # This should restart the script and fix the issue, hopefully.
        # We dont log the error, as its probably just TEAW restarting.

        # TODO: when the server goes offline (say for maintenance) this will not trigger the website to report
        # an outdated status

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