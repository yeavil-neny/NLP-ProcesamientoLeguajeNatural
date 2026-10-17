# -*- coding: utf-8 -*-
"""Servidor MCP de consulta de productos via API viva (Taller 6).

Complemento del caso: OpenFoodFacts (https://world.openfoodfacts.org),
una base abierta y gratuita de alimentos envasados, sin llave de API. Cubre
lo que la tabla sintetica de SQLite no tiene bien: productos de MARCA con
etiqueta nutricional real.

Diseno a prueba de corrida (leccion de reproducibilidad):
- timeout corto y un solo reintento; la herramienta NUNCA lanza una
  excepcion que mate la celda,
- respaldo en `api_cache.json`: instantanea capturada en la corrida del
  17-oct-2026 (commit inicial); si la API no responde, se contesta desde
  el cache y se rotula como tal.

Se usa `FastMCP` con transporte streamable-HTTP en el puerto 9093.
"""
import json
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from unicodedata import combining, normalize

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AlimentosAPIMCP", host="localhost", port=9093)

BASE = Path(__file__).resolve().parent
RUTA_CACHE = BASE / "api_cache.json"
URL_API = "https://world.openfoodfacts.org/api/v2"
USER_AGENT = "NLP-Course-GrupoDelta/1.0 (proyecto educativo)"
CAMPOS = "code,product_name,brands,categories,nutriments,allergens"


def normalizar(texto):
    """Minusculas y sin tildes, igual que en los otros servidores."""
    texto = normalize("NFKD", texto.lower())
    return "".join(ch for ch in texto if not combining(ch))


def cargar_cache():
    try:
        with open(RUTA_CACHE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {"fuente": "sin cache", "productos": {}}


def guardar_cache(instantanea):
    try:
        with open(RUTA_CACHE, "w", encoding="utf-8") as fh:
            json.dump(instantanea, fh, ensure_ascii=False, indent=2)
    except OSError:
        pass  # en Colab el cache es efimero: no debe abortar la corrida


def _get(url):
    """GET con timeout y un reintento. Devuelve (datos, None) o (None, motivo)."""
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=6) as r:
                return json.load(r), None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            motivo = str(exc)
    return None, motivo


def _resumen(producto):
    return {
        "code": producto.get("code", ""),
        "name": producto.get("product_name", "") or producto.get("product_name_es", ""),
        "brands": producto.get("brands", ""),
        "categories": producto.get("categories", ""),
        "allergens": producto.get("allergens", ""),
        "kcal_100g": (producto.get("nutriments") or {}).get("energy-kcal_100g"),
    }


def _texto(codificado, etiqueta):
    kcal = codificado.get("kcal_100g")
    kcal_txt = f"{kcal:g} kcal por 100 g" if isinstance(kcal, (int, float)) else "sin dato de kcal"
    alergenos = codificado.get("allergens") or "sin alergenos declarados"
    marca = f" | marca: {codificado['brands']}" if codificado.get("brands") else ""
    return (
        f"{etiqueta}\n"
        f"Producto: {codificado['name'] or '(sin nombre)'}{marca}\n"
        f"Nutricion: {kcal_txt}\n"
        f"Alergenos declarados: {alergenos}\n"
        f"Fuente: OpenFoodFacts (API v2)."
    )


@mcp.tool()
def info_producto_api(consulta: str) -> str:
    """Consulta un producto en OpenFoodFacts (API viva, sin API key).

    Args:
        consulta: preferentemente el codigo de barras del producto, por
            ejemplo '3017620422003'; tambien acepta el nombre
            ('nutella'), aunque la busqueda por nombre es la parte menos
            estable del servicio.

    Returns:
        Nombre, marca, kcal por 100 g y alergenos declarados del
        producto, rotulados como 'en vivo' (API disponible) o 'cache
        local' (API no disponible: instantanea guardada). Nunca falla:
        si no hay ni datos vivos ni cache, lo informa y deja que la
        conversacion continúe.
    """
    consulta = (consulta or "").strip()
    if not consulta:
        return "Indique un codigo de barras (preferido) o un nombre de producto, por ejemplo: '3017620422003'."
    instantanea = cargar_cache()
    productos = instantanea.get("productos", {})

    # 1) Codigo de barras: endpoint estable por producto.
    if re.fullmatch(r"\d{6,14}", consulta):
        datos, motivo = _get(f"{URL_API}/product/{consulta}.json?fields={CAMPOS}")
        if datos:
            producto = datos.get("product") or {}
            resumen = _resumen(producto)
            if resumen["name"]:
                productos[consulta] = resumen
                instantanea["productos"] = productos
                guardar_cache(instantanea)
                return _texto(resumen, "consulta en vivo")
        if consulta in productos:
            return _texto(productos[consulta], "cache local (la API no disponible a esta hora)")
        return (
            "No pude completar la consulta en vivo"
            + (f" ({motivo})" if motivo else "")
            + " y la cache local no tiene ese codigo de barras. La "
            "conversacion puede continuar con las otras fuentes."
        )

    # 2) Nombre: busqueda (parte menos estable del servicio) con respuesta
    #    por cache si el servicio no esta disponible.
    termino = urllib.parse.quote(consulta)
    datos, motivo = _get(
        f"{URL_API}/cgi/search.pl?search_terms={termino}&search_simple=1"
        f"&action=process&json=1&page_size=5&fields={CAMPOS}"
    )
    if datos and datos.get("products"):
        for bruto in datos["products"][:3]:
            resumen = _resumen(bruto)
            if resumen["name"] and resumen["code"]:
                productos[resumen["code"]] = resumen
        instantanea["productos"] = productos
        guardar_cache(instantanea)
        resumen = _resumen(datos["products"][0])
        return _texto(resumen, "consulta en vivo")

    # 3) Cache local: coincidencia por nombre normalizado.
    clave = normalizar(consulta)
    for almacenado in productos.values():
        if clave in normalizar(almacenado.get("name", "")) or normalizar(almacenado.get("name", "")) in clave:
            return _texto(almacenado, "cache local (la API no disponible a esta hora)")
    return (
        "La API de OpenFoodFacts no esta disponible en este momento"
        + (f" ({motivo})" if motivo else "")
        + " y la cache local no tiene ese producto. La conversacion puede "
        "continuar con las otras fuentes."
    )


if __name__ == "__main__":
    # Servidor HTTP en el puerto 9093 (compatible con Colab).
    mcp.run(transport="streamable-http")