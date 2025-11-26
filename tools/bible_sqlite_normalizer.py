#!/usr/bin/env python3
# bible_sqlite_normalizer.py — Versión DEFINITIVA (Windows + MySword)
import sqlite3
import sys
import os
import shutil

if len(sys.argv) != 2:
    print("Uso: python bible_sqlite_normalizer.py archivo.sqlite")
    sys.exit(1)

db_path = sys.argv[1]
if not os.path.exists(db_path):
    print(f"No existe: {db_path}")
    sys.exit(1)

# Respaldo
backup = db_path.replace(".sqlite", "_original.sqlite")
if not os.path.exists(backup):
    shutil.copy2(db_path, backup)
    print(f"Respaldo creado: {os.path.basename(backup)}")

# Copia temporal
temp_db = db_path.replace(".sqlite", "_temp.sqlite")
shutil.copy2(db_path, temp_db)

print("Convirtiendo al formato BSH oficial...\n")
conn = sqlite3.connect(temp_db)
conn.execute("PRAGMA journal_mode = OFF")
conn.execute("PRAGMA synchronous = OFF")
c = conn.cursor()

# Detectar tabla de libros
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%book%'")
book_tables = [row[0] for row in c.fetchall()]
if not book_tables:
    print("ERROR: No se encontró tabla de libros")
    os.remove(temp_db)
    sys.exit(1)

book_table = book_tables[0]
print(f"   → Tabla de libros: {book_table}")

# Detectar columna con número del libro
c.execute(f"PRAGMA table_info({book_table})")
cols = [row[1].lower() for row in c.fetchall()]
possible = ['number', 'booknumber', 'book_number', 'id', 'bookid', 'book_id']
book_num_col = next((col for col in possible if col in cols), None)
if not book_num_col:
    print(f"ERROR: No encontré columna numérica en {book_table}")
    print(f"   Columnas disponibles: {cols}")
    os.remove(temp_db)
    sys.exit(1)

print(f"   → Columna número de libro: {book_num_col}")

# Crear tabla verses BSH
c.execute("DROP TABLE IF EXISTS verses")
c.execute("""
    CREATE TABLE verses (
        id INTEGER PRIMARY KEY,
        book INTEGER NOT NULL,
        chapter INTEGER NOT NULL,
        verse INTEGER NOT NULL,
        text TEXT NOT NULL
    )
""")

# Migrar datos
print("   → Migrando versículos...")
c.execute(f"""
    INSERT INTO verses (book, chapter, verse, text)
    SELECT b.{book_num_col}, v.chapter, v.verse, v.text
    FROM verse v
    JOIN {book_table} b ON v.book_id = b.id
""")
print(f"   → {c.rowcount:,} versículos migrados")

# Índices
c.execute("CREATE INDEX idx_book_chapter ON verses(book, chapter)")
c.execute("CREATE INDEX idx_full_ref ON verses(book, chapter, verse)")

# FTS5
print("   → Activando FTS5...")
c.execute("DROP TABLE IF EXISTS verses_fts")
c.execute("CREATE VIRTUAL TABLE verses_fts USING fts5(text, content='verses', content_rowid='id')")
c.execute("INSERT INTO verses_fts(rowid, text) SELECT id, text FROM verses")

# Commit y cerrar
conn.commit()
conn.close()

# VACUUM fuera de transacción
print("   → Compactando base de datos...")
conn = sqlite3.connect(temp_db)
conn.execute("VACUUM")
conn.close()

# Reemplazar archivo original
os.remove(db_path)
os.rename(temp_db, db_path)

final_size = os.path.getsize(db_path) / (1024*1024)
print(f"\n¡CONVERSIÓN 100% EXITOSA!")
print(f"   Archivo: {os.path.basename(db_path)}")
print(f"   Tamaño final: {final_size:.2f} MB")
print("   Formato BSH: COMPLETO")
print("   Listo para limpieza final con bible_sqlite_optimizer.py")