import sqlite3
conn = sqlite3.connect('campus.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS buildings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    map_url TEXT,
    floor_plan TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS recent_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    destination TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("Database and tables created!")
