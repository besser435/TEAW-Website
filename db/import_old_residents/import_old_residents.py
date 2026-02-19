import os
import sqlite3

os.chdir(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = "teaw.db"
RESIDENTS_DIR = "residents"


def parse_resident_file(filepath):
    data = {
        "uuid": None,
        "last_online": None,
        "first_joined_date": None,
        "title": "",
        "town_name": ""
    }

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("uuid="):
                data["uuid"] = line.split("=", 1)[1].strip()

            elif line.startswith("lastOnline="):
                value = line.split("=", 1)[1].strip()
                if value.isdigit():
                    data["last_online"] = int(value)

            elif line.startswith("registered="):
                value = line.split("=", 1)[1].strip()
                if value.isdigit():
                    data["first_joined_date"] = int(value)

            elif line.startswith("title="):
                data["title"] = line.split("=", 1)[1].strip()

            elif line.startswith("town="):
                data["town_name"] = line.split("=", 1)[1].strip()

    return data


def main():
    print("Starting import of old residents...")

    exclude_players = ["Plough", "Deployer", "NPC1"]

    if not os.path.isdir(RESIDENTS_DIR):
        print(f"Directory '{RESIDENTS_DIR}' not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    for filename in os.listdir(RESIDENTS_DIR):
        filepath = os.path.join(RESIDENTS_DIR, filename)

        if not os.path.isfile(filepath):
            continue

        name = filename.split(".")[0]

        if name in exclude_players:
            skipped += 1
            continue

        player_data = parse_resident_file(filepath)

        uuid = player_data["uuid"]

        if not uuid:
            skipped += 1
            continue

        # Check if UUID already exists
        cursor.execute("SELECT 1 FROM players WHERE uuid = ?", (uuid,))
        if cursor.fetchone():
            skipped += 1
            continue

        # Default empty values
        town_uuid = ""
        town_name = ""
        nation_uuid = ""
        nation_name = ""

        # Lookup town if provided
        if player_data["town_name"]:
            cursor.execute("""
                SELECT uuid, name, nation, nation_name
                FROM towns
                WHERE name = ?
            """, (player_data["town_name"],))

            town_row = cursor.fetchone()

            if town_row:
                town_uuid = town_row[0] or ""
                town_name = town_row[1] or ""
                nation_uuid = town_row[2] or ""
                nation_name = town_row[3] or ""

        # Insert new player
        cursor.execute("""
            INSERT INTO players (
                uuid,
                name,
                online_duration,
                afk_duration,
                balance,
                title,
                town,
                town_name,
                nation,
                nation_name,
                last_online,
                first_joined_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uuid,
            name,
            0,                      # online_duration
            0,                      # afk_duration
            0.0,                    # balance
            player_data["title"],
            town_uuid,
            town_name,
            nation_uuid,
            nation_name,
            player_data["last_online"],
            player_data["first_joined_date"]
        ))

        inserted += 1

    conn.commit()
    conn.close()

    print("Import complete.")
    print(f"Inserted: {inserted}")
    print(f"Skipped (already exists or invalid): {skipped}")


if __name__ == "__main__":
    main()

