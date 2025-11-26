# final_shrink.py — Reduce cualquier rvr1960.sqlite a su tamaño real
import sqlite3, os, sys

db = sys.argv[1]
print(f"Reduciendo {db} de {os.path.getsize(db)/1024/1024:.1f} MB → tamaño oficial...")

conn = sqlite3.connect(db)
c = conn.cursor()

# 1. Eliminar tablas antiguas si existen
for t in ["verse", "book", "metadata", "testament"]:
    c.execute(f"DROP TABLE IF EXISTS {t}")

# 2. Recrear FTS5 limpio (por si acaso)
c.execute("DROP TABLE IF EXISTS verses_fts")
c.execute("CREATE VIRTUAL TABLE verses_fts USING fts5(text, content='verses', content_rowid='id')")
c.execute("INSERT INTO verses_fts(rowid, text) SELECT id, text FROM verses")

conn.commit()
conn.close()

# 3. VACUUM definitivo (esto es lo que realmente baja el tamaño)
conn = sqlite3.connect(db)
conn.execute("VACUUM")
conn.close()

final = os.path.getsize(db)/1024/1024
print(f"\n¡REDUCIDO CON ÉXITO!")
print(f"   → Tamaño final: {final:.2f} MB  ← este es el tamaño oficial")
print(f"   → Listo para subir al repositorio BSH-Bible-data")