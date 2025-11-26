#!/usr/bin/env python3
# bible_sqlite_validator.py — Versión visual y profesional
# Validador oficial de módulos de Biblia para Bible Study Hub (stand-alone)

import sqlite3
import os
import sys

# Colores para terminal (opcional pero bonito)
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):    print(f"\n{bcolors.HEADER}{bcolors.BOLD}=== {text} ==={bcolors.ENDC}")
def print_ok(msg):         print(f"{bcolors.OKGREEN}✓ {msg}{bcolors.ENDC}")
def print_warn(msg):       print(f"{bcolors.WARNING}⚠ {msg}{bcolors.ENDC}")
def print_error(msg):      print(f"{bcolors.FAIL}✗ {msg}{bcolors.ENDC}")
def print_info(msg):       print(f"{bcolors.OKBLUE}ℹ {msg}{bcolors.ENDC}")

if len(sys.argv) != 2:
    print_header("Bible Study Hub — Validador de Módulos Bíblicos")
    print("Uso: python bible_sqlite_validator.py <archivo.sqlite>")
    sys.exit(1)

db_path = sys.argv[1]
if not os.path.exists(db_path):
    print_error(f"Archivo no encontrado: {db_path}")
    sys.exit(1)

print_header(f"Validando: {os.path.basename(db_path)}")
print_info(f"Tamaño del archivo: {os.path.getsize(db_path) / (1024*1024):.2f} MB\n")

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
except Exception as e:
    print_error(f"No se pudo abrir la base de datos: {e}")
    sys.exit(1)

# 1. Obtener todas las tablas
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [row[0] for row in c.fetchall()]

# 2. Detectar tabla principal
possible_names = ['verses', 'verse', 'bible', 'text', 'texts', 'scripture', 'biblia', 'Verse', 'Bible', 'Texts']
main_table = None
for name in possible_names:
    if name in tables:
        main_table = name
        break

print_header("1. ESTRUCTURA ACTUAL DE LA BASE DE DATOS")
if tables:
    print_info(f"Tablas encontradas ({len(tables)}): {', '.join(tables)}")
else:
    print_error("No se encontraron tablas → base de datos corrupta o vacía")
    sys.exit(1)

if main_table:
    print_ok(f"Tabla principal detectada: {main_table}")
else:
    print_error("No se encontró tabla de versículos")
    print("   Nombres esperados: verses, bible, text, scripture, etc.")
    main_table = tables[0] if tables else None

if not main_table:
    print_error("Imposible continuar sin tabla principal")
    sys.exit(1)

# Analizar columnas
c.execute(f"PRAGMA table_info({main_table});")
columns_info = c.fetchall()
columns = [row[1] for row in columns_info]
col_lower = [col.lower() for col in columns]

print_info(f"Columnas en '{main_table}': {', '.join(columns)}")

# 3. Requisitos mínimos para BSH
print_header("2. REQUISITOS MÍNIMOS PARA BIBLE STUDY HUB (stand-alone)")

requirements = {
    'book':    'Número del libro (1-66)',
    'chapter': 'Número del capítulo',
    'verse':   'Número del versículo',
    'text':    'Texto del versículo'
}

print("Requerimos al menos estas columnas (no sensibles a mayúsculas):")
for col, desc in requirements.items():
    status = "✓" if col in col_lower else "✗"
    color = bcolors.OKGREEN if col in col_lower else bcolors.FAIL
    print(f"   {color}{status} {col:<8} → {desc}{bcolors.ENDC}")

missing_cols = [col for col in requirements if col not in col_lower]
has_extras = len(columns) > 4

# 4. Conteo de versículos
c.execute(f"SELECT COUNT(*) FROM {main_table}")
total_verses = c.fetchone()[0]

print_header("3. ESTADÍSTICAS DEL CONTENIDO")
print_info(f"Total de versículos: {total_verses:,}")
if total_verses >= 31000:
    print_ok("Cantidad compatible con Biblia completa")
elif total_verses >= 23000:
    print_warn("Posible Antiguo Testamento o Nuevo Testamento")
else:
    print_warn("Menos de 23,000 versículos → probablemente incompleta")

# 5. Muestra de contenido
print_header("4. MUESTRA DE VERSÍCULOS")
c.execute(f"SELECT book, chapter, verse, text FROM {main_table} LIMIT 5")
for i, row in enumerate(c.fetchall(), 1):
    book, ch, v, text = row
    preview = text[:80] + ("..." if len(text) > 80 else "")
    print(f"   {i}. {book}:{ch}:{v} → {preview}")

# 6. Características avanzadas
print_header("5. CARACTERÍSTICAS AVANZADAS DETECTADAS")
fts_tables = [t for t in tables if 'fts' in t.lower()]
if fts_tables:
    print_ok(f"FTS5 detectado → búsqueda instantánea disponible ({', '.join(fts_tables)})")
else:
    print_warn("Sin FTS5 → se puede añadir con bible_sqlite_optimizer.py")

# 7. Reporte final
print_header("REPORTE FINAL — COMPATIBILIDAD CON BIBLE STUDY HUB")

if missing_cols:
    print_error("BASE DE DATOS NO COMPATIBLE")
    print(f"   Faltan columnas obligatorias: {', '.join(missing_cols)}")
    print("   Solución: renombrar columnas o usar un CSV limpio para regenerar")
else:
    print_ok("¡BASE DE DATOS 100% COMPATIBLE CON BSH!")
    print_ok("Puedes usar bible_sqlite_optimizer.py para:")
    print("   • Limpiar notas al pie")
    print("   • Activar FTS5")
    print("   • Reducir tamaño ~40%")
    print("   • Mejorar velocidad en e-ink")

print(f"\n{bcolors.BOLD}Listo para subir a BSH-Bible-data → {'Sí' if not missing_cols else 'No'}{bcolors.ENDC}\n")

conn.close()