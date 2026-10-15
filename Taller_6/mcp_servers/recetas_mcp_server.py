# -*- coding: utf-8 -*-
"""Servidor MCP de documentos de recetas (caso propio del Taller 6).

Expone herramientas de consulta sobre el corpus curado `RecetasDeLaAbuela`
(somosnlp, Hackathon #Somos600M). El corpus lo prepara el notebook de
solución antes de arrancar este servidor y lo deja en `recetas_corpus.json`,
junto a este archivo. Cada resultado incluye el identificador de la receta y
la URL de la página web de origen, de manera que el chatbot pueda responder
con referencias verificables.

Se usa `FastMCP` con transporte streamable-HTTP en el puerto 9090, igual que
los servidores guía de la sesión; el transporte HTTP es el más confiable en
Colab y muestra mejor la separación cliente-servidor del protocolo MCP.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from unicodedata import combining, normalize

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("RecetasDocMCP", host="localhost", port=9090)

# Ruta del corpus: se resuelve junto a este archivo para que el servidor
# funcione igual en local y en Colab, sin depender del directorio de trabajo.
CORPUS_PATH = Path(__file__).resolve().parent / "recetas_corpus.json"

# Palabras muy comunes del español que no aportan para la búsqueda.
PALABRAS_VACIAS = {
    "de", "la", "el", "y", "en", "a", "con", "los", "las", "una", "un",
    "se", "del", "por", "para", "que", "al", "o", "sobre", "hasta",
    "como", "muy", "mas", "sino", "esta", "este", "su", "sus", "lo",
    "paso", "pasos", "ingredientes", "receta", "ingrediente",
}


def normalizar(texto):
    """Minúsculas, sin tildes ni diéresis: 'Arroz' -> 'arroz', 'Fríjoles' -> 'frijoles'.

    Al descomponer los acentos (NFKD) y descartar los marca-combinantes, la
    búsqueda ignora diferencias ortográficas sin necesidad de ningún stemmer.
    """
    texto = normalize("NFKD", texto.lower())
    return "".join(ch for ch in texto if not combining(ch))


def canon(token):
    """Variante singular barata: 'arepas' -> 'arepa', 'huevo' -> 'huevo'.

    No es un stemmer completo; solo iguala los plurales regulares en -s para
    que la búsqueda no se pierda por número gramatical.
    """
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def tokenizar(texto):
    """Extrae los tokens útiles de un texto ya normalizado."""
    tokens = re.findall(r"[a-z0-9]{2,}", normalizar(texto))
    return [canon(t) for t in tokens if t not in PALABRAS_VACIAS]


def pesos(texto, peso):
    """Convierte un texto en un contador {token_canonico: peso_repetido}."""
    contador = Counter()
    for token in tokenizar(texto):
        contador[token] += peso
    return contador


def cargar_corpus_e_indice():
    """Lee el corpus JSON y construye el índice invertido token -> [(doc, tf)].

    El peso por campo hace que coincidir en el título cuente 5 veces más que
    coincidir en los pasos, y 2.5 veces más que en los ingredientes, lo que
    mejora la relevancia sin necesitar embeddings.
    """
    with CORPUS_PATH.open(encoding="utf-8") as archivo:
        recetas = json.load(archivo)

    indice = defaultdict(list)
    for doc_id, receta in enumerate(recetas):
        contador = pesos(receta.get("nombre", "") or "", 5.0)
        contador.update(pesos(receta.get("ingredientes", "") or "", 2.0))
        contador.update(pesos(receta.get("pasos", "") or "", 1.0))
        for token, tf in contador.items():
            indice[token].append((doc_id, tf))

    return recetas, indice


CORPUS, INDICE = cargar_corpus_e_indice()


def formato_corto(doc_id):
    """Una línea compacta de resultado, con identificador y URL de la fuente."""
    r = CORPUS[doc_id]
    meta = ", ".join(
        dato for dato in (
            r.get("pais"), r.get("duracion"),
            f"comensales: {r.get('comensales')}" if r.get("comensales") else None,
        ) if dato
    )
    return f"id={r['id']} | {r['nombre']} ({meta}) — Fuente: {r['url']}"


@mcp.tool()
def buscar_recetas(consulta: str, k: int = 3) -> str:
    """Busca recetas de cocina por plato, ingrediente o tipo de platillo.

    Args:
        consulta: lo que se quiere cocinar, por ejemplo 'arepas de queso'
            o 'ceviche de pescado'.
        k: cantidad máxima de resultados (entre 1 y 5).

    Returns:
        Texto con hasta k recetas; cada una incluye su id y la URL de la
        fuente original. Use leer_receta con el id de la mejor para ver la
        receta completa y citar su fuente.
    """
    k = min(max(int(k or 3), 1), 5)
    tokens = [canon(t) for t in tokenizar(consulta)]
    if not tokens:
        return "La consulta no tiene términos de búsqueda útiles. Pruebe con el nombre de un plato o ingrediente."

    # Búsqueda con el índice invertido: cada ocurrencia (ya ponderada por
    # campo) de un token de la consulta suma al puntaje del documento.
    puntajes = Counter()
    for token in set(tokens):
        for doc_id, tf in INDICE.get(token, []):
            puntajes[doc_id] += tf

    if not puntajes:
        return (
            f"No encontré recetas para: '{consulta}'. "
            "Prueba con otro plato o ingrediente, por ejemplo: arepas, ceviche, guacamole, ajiaco, sancocho."
        )

    orden = sorted(puntajes, key=lambda d: (-puntajes[d], d))[:k]
    lineas = [f"Encontré {len(orden)} recetas para '{consulta}':"]
    for puesto, doc_id in enumerate(orden, 1):
        lineas.append(f"[{puesto}] {formato_corto(doc_id)}")
    lineas.append(
        "Sugerencia: llama a leer_receta con el id de la receta que convenga "
        "para ver sus ingredientes, su preparación y la fuente exacta."
    )
    return "\n".join(lineas)


@mcp.tool()
def leer_receta(id: int) -> str:
    """Devuelve la receta completa por su identificador.

    Args:
        id: el identificador numérico que aparece en los resultados de
            buscar_recetas.

    Returns:
        La receta completa con su tabla nutricional aproximada no incluida:
        título, metadatos (país, duración, comensales, dificultad), la URL
        de la fuente original, la lista de ingredientes y la preparación paso a paso.
    """
    id = int(id)
    doc_id = next((i for i, r in enumerate(CORPUS) if r.get("id") == id), None)
    if doc_id is None:
        return f"No existe una receta con id={id}. Use buscar_recetas para ver los ids disponibles."

    r = CORPUS[doc_id]
    partes = [f"RECETA: {r['nombre']} (id={r['id']})"]
    meta = []
    if r.get("pais"):
        meta.append(f"País: {r['pais']}")
    if r.get("duracion"):
        meta.append(f"Duración: {r['duracion']}")
    if r.get("categoria"):
        meta.append(f"Categoría: {r['categoria']}")
    if r.get("comensales"):
        meta.append(f"Comensales: {r['comensales']}")
    if r.get("dificultad"):
        meta.append(f"Dificultad: {r['dificultad']}")
    if meta:
        partes.append(" | ".join(meta))
    # La URL de origen es la clave para que el bot responda 'con referencias':
    # es la página real de la web gastronómica donde se publicó la receta.
    partes.append(f"FUENTE: {r['url']}")
    partes.append(f"\nINGREDIENTES:\n{r.get('ingredientes', '') or '(no disponible)'}")
    partes.append(f"\nPREPARACIÓN:\n{r.get('pasos', '') or '(no disponible)'}")
    return "\n".join(partes)


if __name__ == "__main__":
    # Servidor HTTP en el puerto 9090 (compatible con Colab).
    mcp.run(transport="streamable-http")