# -*- coding: utf-8 -*-
"""Servidor MCP de datos de cocina en SQLite (caso propio del Taller 6).

Tercera fuente del caso: una base de datos real (`cocina_datos.db`,
SQLite) sembrada por `seed_datos.py` con datos sinteticos y orientativos.
Complementa al corpus de recetas y al servidor de calculo con tres
capacidades de negocio:

- kilocalorias por 100 g de alimentos genericos (tabla `calorias`),
- alergenos mas probables por alimento, segun los 9 grupos mayores de la
  lista de la FDA (tabla `alergias`; orientativo, no un diagnostico),
- la "nevera" del usuario en modo SOLO CONSULTA (tabla `inventario`):
  el servidor no modifica su contenido; el sembrado fija los datos en
  cada corrida y las herramientas solo los leen.

Se usa `FastMCP` con transporte streamable-HTTP en el puerto 9092. Las
entradas son cadenas simples por la misma razon que en los otros dos
servidores: un LLM pequeno invoca menos parametros estructurados.
"""
import sqlite3
from pathlib import Path
from unicodedata import combining, normalize

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DatosCocinaMCP", host="localhost", port=9092)

RUTA_DB = Path(__file__).resolve().parent / "cocina_datos.db"


def normalizar(texto):
    """Minusculas y sin tildes, igual que en los otros servidores."""
    texto = normalize("NFKD", texto.lower())
    return "".join(ch for ch in texto if not combining(ch))


def _conectar():
    return sqlite3.connect(RUTA_DB)


def _sin_tabla():
    return (
        "La base de datos no esta sembrada. Corra el sembrado "
        "(seed_datos.py o la celda del notebook que la crea) antes de "
        "iniciar este servidor."
    )


def _buscar_alimento(tabla, alimento):
    """Match flexible sobre una tabla clave TEXT->columna de datos.

    Coincidencia exacta normalizada primero; si no, contencion en ambos
    sentidos ('queso crema' no existe, pero 'queso' si)."""
    clave = normalizar(alimento).strip()
    filas = _conectar().execute(f"SELECT alimento FROM {tabla}").fetchall()
    claves = {normalizar(a): a for (a,) in filas}
    if clave in claves:
        return claves[clave]
    return next((c for c in claves if c in clave or clave in c), None)


@mcp.tool()
def consultar_calorias(alimento: str) -> str:
    """Kilocalorias por 100 g de un alimento generico desde la base SQLite.

    Args:
        alimento: nombre del alimento, por ejemplo 'arroz', 'queso' o
            'camaron'.

    Returns:
        Las kcal por 100 g segun la tabla sintetica de la base de datos,
        con la advertencia de dato orientativo.
    """
    try:
        clave = _buscar_alimento("calorias", alimento)
    except sqlite3.Error:
        return _sin_tabla()
    if clave is None:
        disponibles = sorted(
            a for (a,) in _conectar().execute("SELECT alimento FROM calorias").fetchall()
        )
        return f"No tengo datos de calorias para '{alimento}'. Disponibles: {', '.join(disponibles)}."
    kcal = _conectar().execute(
        "SELECT kcal_100g FROM calorias WHERE alimento = ?", (clave,)
    ).fetchone()[0]
    return (
        f"{clave}: {kcal:g} kcal por 100 g (tabla sintetica en SQLite; "
        "referencia orientativa tipo USDA)."
    )


@mcp.tool()
def consultar_alergias(alimento: str) -> str:
    """Alergenos mas probables de un alimento, segun la base SQLite.

    Args:
        alimento: nombre del alimento o ingrediente, por ejemplo 'queso',
            'camaron' o 'harina'.

    Returns:
        El grupo de alergeno mayor (lista FDA 'big 9') asociado al
        alimento, o el aviso de que no figura en la tabla. El dato es
        orientativo y no sustituye una consulta medica.
    """
    try:
        clave = _buscar_alimento("alergias", alimento)
    except sqlite3.Error:
        return _sin_tabla()
    if clave is None:
        return (
            f"'{alimento}' no figura en la tabla orientativa de alergenos. "
            "Tabla disponible solo como referencia de los 9 grupos mayores "
            "de la FDA: leche, huevo, pescado, crustaceos, frutos secos del "
            "arbol, mani, trigo/gluten, soja y sesamo."
        )
    grupos = _conectar().execute(
        "SELECT grupos FROM alergias WHERE alimento = ?", (clave,)
    ).fetchone()[0].rstrip(".")
    return (
        f"Alergenos mas probables de {clave}: {grupos}. "
        "(Referencia orientativa de la base de datos; no es un diagnostico.)"
    )


@mcp.tool()
def consultar_inventario() -> str:
    """Lista los ingredientes de la 'nevera' del usuario (tabla inventario).

    Returns:
        Los ingredientes guardados con su cantidad, o el aviso de que el
        inventario esta vacio (todavia no se agrego nada).
    """
    try:
        filas = _conectar().execute(
            "SELECT ingrediente, cantidad FROM inventario ORDER BY ingrediente"
        ).fetchall()
    except sqlite3.Error:
        return _sin_tabla()
    if not filas:
        return "La nevera esta vacia. Agregue ingredientes con la herramienta de agregar."
    lineas = [f"- {ing}: {cant}" for ing, cant in filas]
    return "Inventario de la nevera:\n" + "\n".join(lineas)


if __name__ == "__main__":
    # Servidor HTTP en el puerto 9092 (compatible con Colab).
    mcp.run(transport="streamable-http")