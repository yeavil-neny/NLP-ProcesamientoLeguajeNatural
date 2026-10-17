# -*- coding: utf-8 -*-
"""Sembrado de la base de datos SQLite del caso propio del Taller 6.

Crea (y resetea) `cocina_datos.db` junto a este archivo. Es una fuente
de consulta en el mismo problema de negocio (complementar la respuesta
de las recetas) con tres tablas:
- `calorias`: kilocalorias orientativas por 100 g de alimentos genericos.
- `alergias`: grupo de alergeno mas probable por alimento (los 9 grupos
  mayores de la lista de la FDA: leche, huevo, pescado, crustaceos,
  frutos secos, mani, trigo/gluten, soja y sesamo).
- `inventario`: la "nevera" del usuario, en modo SOLO CONSULTA: el
  contenido lo fija este script en cada corrida y el servidor MCP solo
  lo lee; ninguna herramienta escribe sobre la base.

Los datos son SINTETICOS y ORIENTATIVOS (referencias tipo USDA para kcal y
los grupos de la FDA para alergenos); la tabla `meta` deja ese aviso
registrado. La ejecucion es deterministica: cada corrida del notebook
reinicia la base, de modo que los resultados son reproducibles.

Uso: python -I seed_datos.py
"""
import sqlite3
from pathlib import Path

RUTA_DB = Path(__file__).resolve().parent / "cocina_datos.db"

# (alimento, kcal por 100 g) — promedios orientativos tipo USDA.
CALORIAS = [
    ("arroz", 130.0), ("arroz blanco cocido", 130.0), ("pasta", 158.0),
    ("pasta cocida", 158.0), ("pollo", 165.0), ("pechuga de pollo", 165.0),
    ("carne de res", 250.0), ("cerdo", 292.0), ("tocino", 541.0),
    ("chorizo", 459.0), ("jamon", 145.0), ("pescado", 200.0),
    ("atun", 116.0), ("salmon", 208.0), ("camaron", 99.0),
    ("huevo", 143.0), ("frijoles", 132.0), ("lentejas", 116.0),
    ("garbanzos", 164.0), ("queso", 331.0), ("leche", 61.0),
    ("leche entera", 61.0), ("yogurt", 61.0), ("yogurt natural", 61.0),
    ("mantequilla", 717.0), ("aceite", 884.0), ("aceite de oliva", 884.0),
    ("azucar", 387.0), ("harina de trigo", 364.0), ("harina", 364.0),
    ("pan", 265.0), ("pan blanco", 265.0), ("avena", 389.0),
    ("maiz", 96.0), ("papa", 87.0), ("papa cocida", 87.0),
    ("yuca", 191.0), ("yuca cocida", 191.0), ("aguacate", 160.0),
    ("tomate", 18.0), ("cebolla", 40.0), ("zanahoria", 41.0),
    ("pimenton", 31.0), ("ajo", 149.0), ("platano", 122.0),
    ("platano maduro", 122.0), ("banano", 89.0), ("manzana", 52.0),
    ("naranja", 47.0), ("fresas", 32.0), ("mani", 567.0),
    ("chocolate", 546.0), ("nueces", 654.0), ("almendras", 579.0),
    ("pistachos", 560.0), ("camarones cocidos", 99.0),
    ("pulpo", 82.0), ("langosta", 89.0),
]

# (alimento, grupos de alergenos mayores — FDA "big 9" — y notas).
ALERGIAS = [
    ("leche", "Leche (grupo mayor FDA). También derivados: queso, crema, mantequilla."),
    ("queso", "Leche (grupo mayor FDA). Derivado lácteo; los curados concentran más proteína láctea."),
    ("mantequilla", "Leche (grupo mayor FDA). Derivado láctea."),
    ("yogurt", "Leche (grupo mayor FDA). Derivado lácteo."),
    ("huevo", "Huevo (grupo mayor FDA). Presente también en mayonesa y masas horneadas."),
    ("pescado", "Pescado (grupo mayor FDA). No confundir con alergia a crustáceos: son grupos distintos."),
    ("atun", "Pescado (grupo mayor FDA)."),
    ("salmon", "Pescado (grupo mayor FDA)."),
    ("camaron", "Crustaceos/mariscos (grupo mayor FDA). Grupo aparte del de pescado."),
    ("camarones cocidos", "Crustaceos/mariscos (grupo mayor FDA). Grupo aparte del de pescado."),
    ("langosta", "Crustaceos/mariscos (grupo mayor FDA). Grupo aparte del de pescado."),
    ("pulpo", "Moluscos. En la FDA los moluscos es un grupo aparte de crustáceos y de pescado; en la UE figuran como grupo propio."),
    ("mani", "Maní cacahuete (grupo mayor FDA). Alergia persistente; no confundir con frutos secos del árbol."),
    ("nueces", "Frutos secos del árbol (grupo mayor FDA)."),
    ("almendras", "Frutos secos del árbol (grupo mayor FDA)."),
    ("pistachos", "Frutos secos del árbol (grupo mayor FDA)."),
    ("harina", "Trigo/gluten (grupo mayor FDA). Harina de trigo por defecto; verificar si es de otro cereal."),
    ("harina de trigo", "Trigo/gluten (grupo mayor FDA)."),
    ("pan", "Trigo/gluten (grupo mayor FDA). Pan de trigo; puede contener soja y sésamo en la masa."),
    ("pan blanco", "Trigo/gluten (grupo mayor FDA). Pan de trigo; puede contener soja y sésamo en la masa."),
    ("pasta", "Trigo/gluten (grupo mayor FDA). Pasta de trigo."),
    ("pasta cocida", "Trigo/gluten (grupo mayor FDA). Pasta de trigo."),
    ("soya", "Soja (grupo mayor FDA). Presente en salsas asiáticas y aceite de soja refinado (muy bajo riesgo)."),
    ("soja", "Soja (grupo mayor FDA). Presente en salsa de soja, tofu y aceites vegetales."),
    ("sesamo", "Sésamo (grupo mayor FDA). Presente en ajonjolí, tahini y panes artesanales."),
    ("tahini", "Sésamo (grupo mayor FDA)."),
    ("ajo", "Sin alergenos mayores FDA. Reacciones de intolerancia son raras y no cruzan con los 9 grupos."),
    ("cebolla", "Sin alergenos mayores FDA."),
    ("tomate", "Sin alergenos mayores FDA. Intolerancia o alergia al tomate existe, pero no es uno de los 9 grupos."),
    ("papa", "Sin alergenos mayores FDA."),
    ("yuca", "Sin alergenos mayores FDA."),
    ("arroz", "Sin alergenos mayores FDA. Es el cereal que menos reacciones produce."),
    ("maiz", "Sin alergenos mayores FDA (el maíz no figura en la lista big 9; existe alergia específica, poco frecuente)."),
    ("aguacate", "Sin alergenos mayores FDA o síndrome látex-fruta en personas sensibilizadas al látex."),
    ("platano", "Sin alergenos mayores FDA o síndrome látex-fruta en personas sensibilizadas al látex."),
    ("banano", "Sin alergenos mayores FDA o síndrome látex-fruta en personas sensibilizadas al látex."),
    ("maracuya", "Sin alergenos mayores FDA."),
    ("lentejas", "Sin alergenos mayores FDA. Las legumbres (lentejas, garbanzos y frijoles) pueden sensibilizar, sin ser grupo FDA."),
    ("garbanzos", "Sin alergenos mayores FDA. Las legumbres (lentejas, garbanzos y frijoles) pueden sensibilizar, sin ser grupo FDA."),
    ("frijoles", "Sin alergenos mayores FDA. Las legumbres (lentejas, garbanzos y frijoles) pueden sensibilizar, sin ser grupo FDA."),
]

# La "nevera": siembra inicial. Las herramientas de escritura del servidor
# la modifican; el sembrado la reinicia en cada corrida.
INVENTARIO = [
    ("arroz", "1 libra"),
    ("huevo", "6 unidades"),
    ("tomate", "5 unidades"),
    ("leche", "1 litro"),
    ("queso", "250 gramos"),
    ("cebolla", "3 unidades"),
]

AVISO = (
    "Datos sinteticos y orientativos: kcal tipo USDA para ingredientes "
    "genericos; alergenos segun la lista de 9 grupos mayores de la FDA "
    "(leche, huevo, pescado, crustaceos, frutos secos del arbol, mani, "
    "trigo/gluten, soja y sesamo). Es informacion de referencia, no "
    "diagnostico ni consejo medico."
)


def sembrar():
    """Crea la base desde cero: DROP + CREATE + INSERT (reproducible)."""
    con = sqlite3.connect(RUTA_DB)
    try:
        con.executescript("""
            DROP TABLE IF EXISTS meta;
            DROP TABLE IF EXISTS calorias;
            DROP TABLE IF EXISTS alergias;
            DROP TABLE IF EXISTS inventario;

            CREATE TABLE meta (clave TEXT PRIMARY KEY, valor TEXT NOT NULL);

            CREATE TABLE calorias (
                alimento TEXT PRIMARY KEY,
                kcal_100g REAL NOT NULL CHECK (kcal_100g > 0)
            );

            CREATE TABLE alergias (
                alimento TEXT PRIMARY KEY,
                grupos TEXT NOT NULL
            );

            CREATE TABLE inventario (
                ingrediente TEXT PRIMARY KEY,
                cantidad TEXT NOT NULL
            );
        """)
        con.executemany("INSERT INTO calorias VALUES (?, ?)", CALORIAS)
        con.executemany("INSERT INTO alergias VALUES (?, ?)", ALERGIAS)
        con.executemany("INSERT INTO inventario VALUES (?, ?)", INVENTARIO)
        con.executemany("INSERT INTO meta VALUES (?, ?)", (
            ("fuente", AVISO),
            ("sembrado", "deterministico: este script reinicia la base en cada corrida"),
        ))
        con.commit()
    finally:
        con.close()


def main():
    sembrar()
    con = sqlite3.connect(RUTA_DB)
    try:
        conteos = {
            tabla: con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            for tabla in ("calorias", "alergias", "inventario", "meta")
        }
    finally:
        con.close()
    print("Base sembrada en", RUTA_DB, "— filas:", conteos)


if __name__ == "__main__":
    main()