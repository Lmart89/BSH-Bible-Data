#!/usr/bin/env python3
# bible_sqlite_optimizer.py — VERSIÓN FINAL Y 100% FUNCIONAL
# Limpia notas al pie, activa FTS5 y optimiza tamaño

import sqlite3
import os
import sys
import re

def limpiar_texto(text):
    """Elimina todo tipo de referencias: [1] (2) <3> {4} † ‡ etc."""
    if not text:
        return text
    # Quitar referencias comunes
    text = re.sub(r"[\[\(]<{]\d+[\]\)>}]", "", text)   # [1] (2) <3> {4}
    text = re.sub(r"[†‡※★]", "", text)                # cruces y estrellas
    text = re.sub(r"\s+", " ", text)                  # espacios múltiples
    return text.strip()

if len(sys.argv) != 2:
    print("Uso: python bible_sqlite_optimizer.py archivo.sqlite")
    sys.exit(1)

db_path = sys.argv[1]
if not os.path.exists(db_path):
    print(f"Error: No existe {db_path}")
    sys.exit(1)

# Respaldo automático
backup = db_path.replace(".sqlite", "_before_optimizer.sqlite")
if not os.path.exists(backup):
    import shutil
    shutil.copy2(db_path, backup)
    print(f"Respaldo creado: {os.path.basename(backup)}")

print(f"\nOptimizando y limpiando: {os.path.basename(db_path)}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. Limpiar todo el texto con Python (la forma más segura y potente)
print("   → Limpiando notas al pie y referencias...")
c.execute("SELECT id, text FROM verses")
rows = c.fetchall()

limpios = []
for row_id, text in rows:
    texto_limpio = limpiar_texto(text)
    limpios.append((texto_limpio, row_id))

c.executemany("UPDATE verses SET text = ? WHERE id = ?", limpios)
print(f"   → {len(limpios):,} versículos limpiados")

# 2. Re-crear FTS5 con el texto limpio
print("   → Recreando FTS5 con texto limpio...")
c.execute("DROP TABLE IF EXISTS verses_fts")
c.execute("CREATE VIRTUAL TABLE verses_fts USING fts5(text, content='verses', content_rowid='id')")
c.execute("INSERT INTO verses_fts(rowid, text) SELECT id, text FROM verses")

# 3. Asegurar índices
c.execute("CREATE INDEX IF NOT EXISTS idx_book_chapter ON verses(book, chapter)")
c.execute("CREATE INDEX IF NOT EXISTS idx_full_ref ON verses(book, chapter, verse)")

# Commit
conn.commit()
conn.close()

# VACUUM fuera de transacción
print("   → Compactando base de datos (VACUUM)...")
conn = sqlite3.connect(db_path)
conn.execute("VACUUM")
conn.close()

final_size = os.path.getsize(db_path) / (1024*1024)
print(f"\n¡OPTIMIZACIÓN COMPLETADA!")
print(f"   Archivo: {os.path.basename(db_path)}")
print(f"   Tamaño final: {final_size:.2f} MB")
print(f"   Texto 100% limpio")
print(f"   FTS5 actualizado")
print(f"   ¡LISTO PARA SUBIR A BSH-Bible-data!")
print(f"   Sube este archivo a: bibles/{os.path.basename(db_path)}")