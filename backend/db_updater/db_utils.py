import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


DB_FILE = "teaw.db"


# what the fuck is database normalization
def create_tables(db_file=DB_FILE):
    db = sqlite3.connect(db_file)
    cursor = db.cursor()

    # Create players table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            uuid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            online_duration INTEGER,
            afk_duration INTEGER,
            balance REAL,
            title TEXT,
            town_name TEXT,                
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


    # # Create towns table
    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS towns (
                   
    # """)

    # # Create nations table
    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS nations (
                   
    # """)



    print("Database initialized")
    db.commit()
    db.close()

def drop(db_file=DB_FILE, table=None):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {table};")
    print(f"Dropped table {table}")

    conn.commit()
    conn.close()


# DB performance might get slow once we get in the hundreds of thousands range, as we often
# do lookups on the chat table to prevent adding duplicates.
# This will move the chat messages to an archive table, and delete the messages in the chat table.
def archive_chat_table(db_file=DB_FILE):
    pass



if __name__ == "__main__":
    drop(DB_FILE, "players")
    drop(DB_FILE, "chat")
    create_tables()

