import os
import json
import sqlite3


STATIONS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "stations"))
QUERY_TABLES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "tables.sql"))
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "stations.db"))

# Purge DB file
if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)

# Connect to SQLite 
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Create tables
with open(QUERY_TABLES_PATH, "r", encoding="utf-8") as f:
    cursor.executescript(f.read())

# Go through all files
for dirpath, dirnames, filenames in os.walk(STATIONS_PATH):
    for filename in [f for f in filenames if f.endswith(".json")]:
        # Read file and parse JSON
        with open(os.path.join(dirpath, filename), "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        # Skip inactive stations
        if data.get('active', False) == False:
            continue
        # Insert into stations
        cursor.execute(
            """INSERT INTO `stations` VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                data['id'],
                data['country'],
                data['region'],
                data['location']['latitude'],
                data['location']['longitude'],
                data['location']['elevation'],
                data['timezone']
            )
        )
        # Insert into stations_name
        [cursor.execute("""INSERT INTO `names` VALUES (?, ?, ?)""", (data['id'], key, value)) for key, value in data['name'].items()]
        # Insert into stations_identifiers
        [cursor.execute("""INSERT INTO `identifiers` VALUES (?, ?, ?)""", (data['id'], key, value)) for key, value in data['identifiers'].items()]

# Commit changes to database     
conn.commit()

# Close connection 
conn.close()