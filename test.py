import sqlite3

conn = sqlite3.connect("database/trial_data.db")
cursor = conn.cursor()
cursor.execute("SELECT typeof(monocyte), monocyte FROM cell_counts LIMIT 5")
print(cursor.fetchall())
