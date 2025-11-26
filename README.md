# BSH Bible data

Repositorio oficial de datos y herramientas para **Bible Study Hub** (BSH) —  
la aplicación de estudio bíblico minimalista, rápida y optimizada para dispositivos e-ink (y tablets) que estás construyendo como proyecto independiente y stand-alone.

Este repositorio es el hogar definitivo de todos los módulos que usará BSH, así como las herramientas necesarias para crearlos y mantenerlos.

## ¿Qué encontrarás aquí?

| Tipo de contenido                  | Descripción                                                                 | Formato principal       |
|------------------------------------|-----------------------------------------------------------------------------|-------------------------|
| **Biblias completas**              | Versiones limpias, listas para usar en BSH con búsqueda instantánea         | `.sqlite`               |
| **Comentarios bíblicos**           | Matthew Henry, David Guzik, Spurgeon, etc. (próximamente)                  | `.sqlite` o `.lua`      |
| **Diccionarios y léxicos**         | Strong en español, morfología, léxicos hebreo/griego                        | `.sqlite`               |
| **Devocionales diarios**           | Mañana y Noche (Spurgeon), Nuestro Pan Diario, etc.                        | `.lua` por fecha        |
| **Mapas y líneas de tiempo**       | Recursos visuales interactivos                                              | Imágenes + datos `.lua` |
| **Herramientas de conversión**     | Scripts para generar módulos perfectos desde CSV, OSIS, MySword, etc.      | `tools/`                |
| **Documentación y guías**          | Cómo crear e integrar nuevos módulos en BSH                                 | `docs/`                 |

## Biblias disponibles actualmente

| Versión                     | Archivo                 | Tamaño   | Características                         |
|-----------------------------|-------------------------|----------|------------------------------------------|
| Reina-Valera 1960           | `rv1960.sqlite`         | ~4.8 MB  | Texto limpio, FTS5, índices optimizados  |
| Reina-Valera 1909 (Antigua) | `rv1909.sqlite`         | ~4.6 MB  | Texto limpio, FTS5, índices optimizados  |
| (más versiones próximamente)|                         |          |                                          |

## Estructura de carpetas recomendada en BSH (stand-alone)

```text
Bible Study Hub/
 ├─ data/
 │    ├─ bibles/          ← aquí van los .sqlite de Biblias
 │    ├─ commentaries/    ← comentarios (próximamente)
 │    ├─ dictionaries/    ← Strong, léxicos, etc.
 │    └─ devotionals/     ← archivos .lua por fecha
 └─ tools/                ← scripts de este repositorio (opcional)