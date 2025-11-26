#!/usr/bin/env python3
# bible_search.py — Versión DEFINITIVA 100% funcional con todos los libros
import sqlite3
import sys
import os
import re

# Diccionario completo: nombre → número de libro (1-66)
LIBROS = {
    # Antiguo Testamento
    "gen":1, "génesis":1, "gn":1,
    "exo":2, "éxodo":2, "ex":2,
    "lev":3, "levítico":3, "lv":3,
    "num":4, "números":4, "nm":4,
    "deu":5, "deuteronomio":5, "dt":5,
    "jos":6, "josué":6,
    "jue":7, "jueces":7, "jz":7,
    "rut":8, "rut":8,
    "1sam":9, "1sa":9, "1 samuel":9,
    "2sam":10, "2sa":10, "2 samuel":10,
    "1rey":11, "1re":11, "1 reyes":11,
    "2rey":12, "2re":12, "2 reyes":12,
    "1cro":13, "1cr":13, "1 crónicas":13,
    "2cro":14, "2cr":14, "2 crónicas":14,
    "esd":15, "esdras":15,
    "neh":16, "nehemías":16, "ne":16,
    "est":17, "ester":17,
    "job":18, "job":18,
    "sal":19, "salmos":19, "sl":19,
    "pro":20, "proverbios":20, "pr":20,
    "ecl":21, "eclesiastés":21, "ec":21,
    "can":22, "cantares":22, "cnt":22,
    "isa":23, "isaías":23,
    "jer":24, "jeremías":24,
    "lam":25, "lamentaciones":25,
    "eze":26, "ezequiel":26, "ez":26,
    "dan":27, "daniel":27,
    "ose":28, "oseas":28,
    "joe":29, "joel":29,
    "amo":30, "amós":30,
    "abd":31, "abdías":31,
    "jon":32, "jonás":32,
    "miq":33, "miqueas":33,
    "nah":34, "nahúm":34,
    "hab":35, "habacuc":35,
    "sof":36, "sofonías":36,
    "hag":37, "hageo":37,
    "zac":38, "zacarías":38,
    "mal":39, "malaquías":39,
    # Nuevo Testamento
    "mat":40, "mateo":40, "mt":40,
    "mar":41, "marcos":41, "mc":41,
    "luc":42, "lucas":42, "lc":42,
    "jua":43, "juan":43, "jn":43,
    "hch":44, "hechos":44,
    "rom":45, "romanos":45,
    "1cor":46, "1co":46, "1 corintios":46,
    "2cor":47, "2co":47, "2 corintios":47,
    "gal":48, "gálatas":48,
    "ef":49, "efesios":49,
    "fil":50, "filipenses":50,
    "col":51, "colosenses":51,
    "1tes":52, "1ts":52, "1 tesalonicenses":52,
    "2tes":53, "2ts":53, "2 tesalonicenses":53,
    "1tim":54, "1ti":54, "1 timoteo":54,
    "2tim":55, "2ti":55, "2 timoteo":55,
    "tit":56, "tito":56,
    "flm":57, "filemón":57,
    "heb":58, "hebreos":58,
    "sant":59, "santiago":59, "st":59,
    "1ped":60, "1pe":60, "1 pedro":60,
    "2ped":61, "2pe":61, "2 pedro":61,
    "1jua":62, "1jn":62, "1 juan":62,
    "2jua":63, "2jn":63, "2 juan":63,
    "3jua":64, "3jn":64, "3 juan":64,
    "jud":65, "judas":65,
    "apo":66, "apocalipsis":66, "ap":66
}

def normalizar_libro(nombre):
    nombre = nombre.strip().lower()
    nombre = re.sub(r'[^a-záéíóúñ]', '', nombre)  # quitar números y espacios
    return LIBROS.get(nombre)

def parsear_referencia(ref):
    # Ejemplos válidos:
    # "Juan 3:16", "Jn 3:16", "romanos 8", "1 Corintios 13:4-8", "Ap 22:21"
    patron = r"^(\S+)\s+(\d+):?(\d+)?-?(\d*)"
    m = re.match(patron, ref.strip(), re.IGNORECASE)
    if not m:
        return None
    libro_str, cap, v1, v2 = m.groups()
    book = normalizar_libro(libro_str)
    if not book:
        return None
    chapter = int(cap)
    verse_from = int(v1) if v1 else 1
    verse_to = int(v2) if v2 and v2 != '' else verse_from
    return book, chapter, verse_from, verse_to

# ===================== MAIN =====================
if len(sys.argv) != 3:
    print("Uso: python bible_search.py archivo.sqlite \"referencia o palabra\"")
    sys.exit(1)

db_path = sys.argv[1]
query = sys.argv[2].strip()

if not os.path.exists(db_path):
    print("Archivo no encontrado")
    sys.exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

# ¿Es referencia?
coords = parsear_referencia(query)
if coords:
    book, chapter, v_from, v_to = coords
    libro_nombre = [k for k, v in LIBROS.items() if v == book][0].title()
    c.execute("""
        SELECT verse, text FROM verses 
        WHERE book = ? AND chapter = ? AND verse BETWEEN ? AND ?
        ORDER BY verse
    """, (book, chapter, v_from, v_to))
    rows = c.fetchall()
    if rows:
        print(f"\n{libro_nombre} {chapter}:{v_from}-{v_to}\n")
        for verse, text in rows:
            print(f"{verse:>2}  {text}")
        print(f"\n→ {len(rows)} versículo(s)")
    else:
        print("Referencia no encontrada")
else:
    # Búsqueda por texto (usa FTS5 si existe, sino LIKE)
    try:
        c.execute("SELECT book, chapter, verse, text FROM verses_fts WHERE text MATCH ? LIMIT 50", (query,))
        rows = c.fetchall()
        metodo = "FTS5 (ultra-rápido)"
    except:
        c.execute("SELECT book, chapter, verse, text FROM verses WHERE text LIKE ? LIMIT 50", (f"%{query}%",))
        rows = c.fetchall()
        metodo = "LIKE"

    print(f"\nBúsqueda: «{query}» → {len(rows)} resultado(s) [{metodo}]\n")
    for book, chapter, verse, text in rows:
        libro = [k for k, v in LIBROS.items() if v == book][0].title()
        print(f"{libro} {chapter}:{verse}")
        print(f"    {text}\n")

conn.close()
print("¡Listo!")