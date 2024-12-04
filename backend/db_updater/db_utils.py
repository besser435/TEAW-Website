import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

DB_FILE = "db/teaw.db"

# what the fuck is database normalization
def create_tables(db_file=DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
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

    print("Database initialized")


def drop(db_file=DB_FILE, table=None):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        conn.commit()

    print(f"Dropped table {table}")



# DB performance might get slow once we get in the hundreds of thousands range, as we often
# do lookups on the chat table to prevent adding duplicates.
# This will move the chat messages to an archive table, and delete the messages in the chat table.
def archive_chat_table(db_file=DB_FILE):
    # Keep the 1000 most recent messages in the chat table, so that they can still be displayed in the frontend
    pass



if __name__ == "__main__":
    #drop(table="players")
    #drop(table="chat")
    #drop(table="towns")
    #drop(table="nations")
    #drop(table="variables")
    create_tables()

