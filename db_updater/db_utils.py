import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TEAW_DB_FILE = "../db/teaw.db"
STATS_DB_FILE = "../db/stats.db"


# what the fuck is database normalization
def create_teaw_tables(db_file=TEAW_DB_FILE):
    with sqlite3.connect(TEAW_DB_FILE) as conn:
        cursor = conn.cursor()

        # Create players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                online_duration INTEGER,
                afk_duration INTEGER,
                balance REAL,
                title TEXT,
                town TEXT,           
                town_name TEXT, 
                nation TEXT,    
                nation_name TEXT,              
                last_online INTEGER     -- added by db_updater.py, not TAPI
            )
        """)

        # Create chat table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                sender TEXT NOT NULL,                  
                sender_uuid TEXT,
                message TEXT NOT NULL,                
                timestamp INTEGER NOT NULL,
                type TEXT NOT NULL
            )
        """)

        # Create towns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS towns (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mayor TEXT NOT NULL,
                founder TEXT NOT NULL,
                balance REAL NOT NULL,
                nation TEXT,
                nation_name TEXT,
                founded INTEGER NOT NULL,
                resident_tax_percent REAL NOT NULL,
                is_active BOOLEAN NOT NULL,
                claimed_chunks INTEGER NOT NULL,
                color_hex TEXT NOT NULL,
                tag TEXT,
                board TEXT
            )
        """)

        # Create nations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nations (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                leader TEXT NOT NULL,
                capitol_town TEXT NOT NULL,
                capitol_town_name TEXT,
                balance REAL NOT NULL,
                town_tax_dollars REAL NOT NULL,
                founded INTEGER NOT NULL,
                color_hex TEXT NOT NULL,
                tag TEXT,
                board TEXT
            )
        """)

        # Create misc. variables table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS variables (
                variable TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()

    print("TEAW database initialized")


def create_stats_tables(db_file=STATS_DB_FILE):
    with sqlite3.connect(STATS_DB_FILE) as conn:
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

        conn.commit()

    print("Stats database initialized")


def drop_stats_table(db_file=STATS_DB_FILE, table=None):
    with sqlite3.connect(STATS_DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        conn.commit()

    print(f"Dropped stats table: {table}")


def drop_teaw_table(db_file=TEAW_DB_FILE, table=None):
    with sqlite3.connect(TEAW_DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        conn.commit()

    print(f"Dropped TEAW table: {table}")


def get_stat(player_uuid, category, stat_key):
    with sqlite3.connect(STATS_DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT stat_value
            FROM player_statistics
            WHERE player_uuid = ? AND category = ? AND stat_key = ?
        """, (player_uuid, category, stat_key))

        result = cursor.fetchone()
        return result[0] if result else None
    

def insert_player(
    uuid, name, online_duration=0, afk_duration=0, balance=0.0, 
    title=None, town=None, town_name=None, nation=None, 
    nation_name=None, last_online=None, db_file=TEAW_DB_FILE
):
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO players (
                uuid, name, online_duration, afk_duration, balance, title, 
                town, town_name, nation, nation_name, last_online
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uuid, name, online_duration, afk_duration, balance, title, 
            town, town_name, nation, nation_name, last_online
        ))
        
        conn.commit()

    print(f"Inserted or updated player: {name} ({uuid})")


# DB performance might get slow once we get in the hundreds of thousands range, as we often
# do lookups on the chat table to prevent adding duplicates.
# This will move the chat messages to an archive table, and delete the messages in the chat table.
def archive_chat_table(db_file=TEAW_DB_FILE):
    # Keep the 1000 most recent messages in the chat table, so that they can still be displayed in the frontend
    pass



if __name__ == "__main__":
    #create_teaw_tables()


    insert_player(
        uuid="cbb82a16-fbb8-44ab-b201-5db723494ede", name="josamo8",
        online_duration=0, afk_duration=0, balance=0.0,
        title="", town="", town_name="", nation="",
        nation_name="", last_online=1704517074000
    )

    insert_player(
        uuid="75418e9c-34ef-4926-af64-96d98d10954c", name="brandonusa",
        online_duration=0, afk_duration=0, balance=0.0,
        title="Cowgirl", town="", town_name="", nation="",
        nation_name="", last_online=1704530881000
    )

