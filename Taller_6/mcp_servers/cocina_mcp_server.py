# -*- coding: utf-8 -*-
"""Servidor MCP de utilidades de cocina (caso propio del Taller 6).

Complementa al servidor de documentos con herramientas de cálculo exacto:
equivalencias de unidades de volumen, escalado de cantidades para más o
menos comensales, y kilocalorías aproximadas de los ingredientes más usados.

Se usa `FastMCP` con transporte streamable-HTTP en el puerto 9091. Las
entradas se diseñaron como cadenas simples ("2 tazas", "500 ml", "pollo"...)
porque es lo que un LLM pequeño como llama3.2:3b invoca con menos errores:
los parámetros estructurados complejos los frustra.
"""
import re
from unicodedata import combining, normalize

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CocinaUtilsMCP", host="localhost", port=9091)


def normalizar(texto):
    """Minúsculas y sin tildes: 'Fríjoles' -> 'frijoles', 'Plátano' -> 'platano'."""
    texto = normalize("NFKD", texto.lower())
    return "".join(ch for ch in texto if not combining(ch))


# ----------------------------------------------------------------------------
# Equivalencias de volumen. Una taza estándar tiene 240 ml, la cucharada 15 ml
# y la cucharadita 5 ml; sobre esas tres se apoya toda la conversión.
# ----------------------------------------------------------------------------
TAMANO_ML = {
    "ml": 1.0, "mililitros": 1.0, "cc": 1.0,
    "taza": 240.0, "tazas": 240.0,
    "cucharada": 15.0, "cucharadas": 15.0,
    "cucharadita": 5.0, "cucharaditas": 5.0,
    "vaso": 240.0, "vasos": 240.0,
    "l": 1000.0, "litro": 1000.0, "litros": 1000.0,
    "onzas": 29.57, "onza": 29.57,
}

# Patrones de cantidad: enteros, decimales y frases como "1 1/2" o "media".
NUMERO = r"(\d+[\.,]?\d*)"

# Kilocalorías de referencia por cada 100 g de alimento. Son promedios de
# tablas tipo USDA FoodData Central; se etiquetan siempre como aproximados.
KCAL_POR_100G = {
    "arroz blanco cocido": 130.0, "arroz": 130.0,
    "pasta cocida": 158.0, "pasta": 158.0,
    "pollo": 165.0, "pechuga de pollo": 165.0,
    "carne de res": 250.0, "res": 250.0,
    "cerdo": 292.0, "tocino": 541.0, "chorizo": 459.0, "jamon": 145.0,
    "pescado": 200.0, "atun": 116.0, "salmon": 208.0,
    "camaron": 99.0, "camarones": 99.0,
    "huevo": 143.0, "huevos": 143.0,
    "frijoles": 132.0,
    "lentejas": 116.0, "garbanzos": 164.0,
    "queso": 331.0, "leche entera": 61.0, "leche": 61.0,
    "yogurt natural": 61.0, "yogurt": 61.0,
    "mantequilla": 717.0, "aceite": 884.0, "aceite de oliva": 884.0,
    "azucar": 387.0, "harina de trigo": 364.0, "harina": 364.0,
    "pan blanco": 265.0, "pan": 265.0,
    "avena": 389.0, "maiz": 96.0, "papa cocida": 87.0, "papa": 87.0,
    "yuca cocida": 191.0, "yuca": 191.0,
    "aguacate": 160.0, "tomate": 18.0, "cebolla": 40.0, "zanahoria": 41.0,
    "pimenton": 31.0, "ajo": 149.0,
    "platano maduro": 122.0, "platano": 122.0, "banano": 89.0, "banana": 89.0,
    "manzana": 52.0, "naranja": 47.0, "fresas": 32.0,
    "mani": 567.0, "chocolate": 546.0,
}


def parsear_frase_cantidad(frase):
    """Separa una frase como '2 tazas de leche' en (numero, unidad, resto).

    Devuelve (numero float, unidad str o None, resto de la frase). Si no hay
    número, devuelve None en numero y la frase limpia en resto.
    """
    frase = normalizar(frase).strip()
    m = re.search(NUMERO, frase)
    if not m:
        return None, None, frase
    numero = float(m.group(1).replace(",", "."))
    resto_despues = frase[m.end():].strip()
    unidad = resto_despues.split()[0] if resto_despues else ""
    # La unidad termina en la primera palabra no alfabética o hasta otra cifra.
    if not re.match(r"^[a-z]+", unidad):
        unidad = ""
    return numero, unidad or None, resto_despues


def formato_numero(x):
    """Imprime enteros sin decimal y decimales con hasta 2 cifras."""
    return str(int(round(x))) if abs(x - round(x)) < 1e-9 else f"{x:.2f}".rstrip("0").rstrip(".")


@mcp.tool()
def convertir_volumen(frase: str) -> str:
    """Convierte una cantidad de cocina entre unidades de volumen.

    Args:
        frase: la cantidad con su unidad, por ejemplo '2 tazas de leche',
            '500 ml', '1.5 tazas de harina'.

    Returns:
        La equivalencia entre tazas, mililitros, cucharadas y cucharaditas
        (1 taza = 240 ml, 1 cucharada = 15 ml, 1 cucharadita = 5 ml).
    """
    numero, unidad, _ = parsear_frase_cantidad(frase)
    if numero is None:
        return (
            "No pude leer una cantidad. Formatos aceptados, por ejemplo: "
            "'2 tazas', '500 ml', '3 cucharadas', '0.5 litros', '8 onzas'."
        )
    if unidad not in TAMANO_ML:
        lista = ", ".join(sorted(TAMANO_ML))
        return (
            f"No reconozco la unidad '{unidad}'. Unidades aceptadas: {lista}."
        )
    ml = numero * TAMANO_ML[unidad]
    # Cadena de equivalencias, omitiendo la unidad que ya vino en la frase
    # (no se repite '500 ml ≈ 500 ml').
    destinos = []
    for etiqueta, valor_ml in (("tazas", 240.0), ("cucharadas", 15.0), ("cucharaditas", 5.0)):
        if unidad != etiqueta:
            destinos.append(f"{formato_numero(ml / valor_ml)} {etiqueta}")
    partes = [f"{formato_numero(ml)} ml"] if unidad != "ml" else []
    partes = partes + destinos
    return (
        f"Equivalencia de '{frase.strip()}': "
        + " = ".join(partes)
        + ". (Taza estándar de 240 ml, cucharada de 15 ml, cucharadita de 5 ml.)"
    )


@mcp.tool()
def escalar_cantidad(frase: str, factor: float) -> str:
    """Escala una cantidad de una receta por un factor.

    Args:
        frase: la cantidad original, por ejemplo '500 gramos de masa',
            '4 comensales' o '2 tazas de harina'.
        factor: multiplicador. Para pasar una receta de 4 a 6 comensales,
            el factor es 6/4 = 1.5.

    Returns:
        La cantidad original y su valor escalado, con el mismo formato.
    """
    if factor is None or factor <= 0:
        return "El factor debe ser un número positivo, por ejemplo 1.5 para escalar de 4 a 6 comensales."
    numero, unidad, _ = parsear_frase_cantidad(frase)
    if numero is None:
        return (
            "No pude leer una cantidad en la frase. Formatos aceptados, por "
            "ejemplo: '500 gramos de masa', '4 comensales', '2 tazas'."
        )
    resultado = numero * float(factor)
    etiqueta = unidad if unidad else "unidades"
    return (
        f"Escala de '{frase.strip()}' × {formato_numero(factor)}: "
        f"{formato_numero(numero)} {etiqueta} → {formato_numero(resultado)} {etiqueta}."
    )


@mcp.tool()
def calcular_kcal(gramos: float, alimento: str) -> str:
    """Calcula las kilocalorías aproximadas de una cantidad de alimento.

    Args:
        gramos: peso del alimento en gramos, por ejemplo 200.
        alimento: nombre del alimento, por ejemplo 'pollo', 'queso' o
            'arroz blanco cocido'.

    Returns:
        Las kcal aproximadas del dato recibido, la referencia por cada 100 g
        y una aclaración de que el valor es estimado.
    """
    if gramos is None or gramos <= 0:
        return "El peso en gramos debe ser un número positivo, por ejemplo 200."
    alimento = normalizar(alimento).strip()
    # Coincidencia flexible: el alimento pedido, o la clave de la tabla, debe
    # estar contenida en el otro ('queso crema' no está, pero 'queso' sí).
    clave = next(
        (k for k in KCAL_POR_100G if k in alimento or alimento in k), None
    )
    if clave is None:
        # En el mensaje de error se ocultan las claves que son sinónimo
        # literal de otra ('pan blanco' no se lista aparte de 'pan').
        visibles = sorted(
            k for k in KCAL_POR_100G
            if not any(k in otro and KCAL_POR_100G[otro] == KCAL_POR_100G[k]
                       for otro in KCAL_POR_100G if otro != k)
        )
        return (
            f"No tengo datos para '{alimento}'. Alimentos disponibles: "
            f"{', '.join(visibles)}."
        )
    por_100g = KCAL_POR_100G[clave]
    kcal = por_100g * float(gramos) / 100.0
    return (
        f"{formato_numero(gramos)} g de {clave} ≈ {formato_numero(kcal)} kcal "
        f"(aprox. {formato_numero(por_100g)} kcal por 100 g). "
        "Dato de referencia nutricional (tablas tipo USDA FoodData Central): "
        "puede variar según el corte, marca y preparación."
    )


if __name__ == "__main__":
    # Servidor HTTP en el puerto 9091 (compatible con Colab).
    mcp.run(transport="streamable-http")