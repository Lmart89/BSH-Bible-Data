# check_tables.py
import sqlite3
import sys

if len(sys.argv) != 2:
    print("Uso: python check_tables.py archivo.sqlite")
    sys.exit()

db = sys.argv[1]
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
print(f"Tablas en {db}:")
for row in c.fetchall():
    print("   →", row[0])
conn.close()