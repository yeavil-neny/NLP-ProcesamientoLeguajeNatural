# -*- coding: utf-8 -*-
"""Genera el notebook de solucion del Taller 6: proyecto_mcp_chatbot_recetas.ipynb.

Contenido como lista de (tipo, texto). Los outputs quedan vacios: el notebook
se ejecuata en Colab (Run All) y las narrativas se sincronizan con la corrida
real en un paso posterior (los numeros pendientes estan marcados con
'POR LLENAR').
"""
import json
from pathlib import Path

# Anclado a la ubicacion del script: siempre ../build_solucion.py -> Taller_6/,
# sin importar desde que carpeta se ejecute.
DST = Path(__file__).resolve().parents[1] / "proyecto_mcp_chatbot_recetas.ipynb"

CELLS = []


def md(text):
    CELLS.append(("markdown", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n") + "\n"))


# ==========================================================================
# Portada
# ==========================================================================
md(r"""
# Taller 6 — Mini proyecto MCP con LLM y LangChain

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yeavil-neny/NLP-ProcesamientoLeguajeNatural/blob/main/Taller_6/proyecto_mcp_chatbot_recetas.ipynb)

## Caso propio: asistente culinario conversacional con servidores MCP propios (documentos de recetas + utilidades de cálculo + datos de consulta en SQLite + API viva de productos)
""")

md(r"""
## 1. El problema y el papel del Model Context Protocol (MCP)

El RAG del taller anterior resolvió el conocimiento estático del LLM con una memoria externa citable. Pero quedaba una segunda limitación: **todo el conocimiento tenía que pasar por el vector store**, y el modelo seguía sin poder *actuar*: no podía calcular, convertir unidades ni escalar cantidades sin que se le re-entrenara o se le escribiera lógica ad hoc.

**Model Context Protocol (MCP)** ([specificación, 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)) es el estándar abierto que resuelve esto: un protocolo entre aplicaciones que exponen capacidades (**host**) y los LLM que las consumen, con tres roles bien definidos:

- **Host**: la aplicación con el LLM (aquí, el notebook con el agente de LangChain).
- **Cliente**: el conector que mantiene una sesión `1:1` con un servidor (aquí, `MultiServerMCPClient`, de `langchain-mcp-adapters`).
- **Servidores MCP**: programas pequeños que exponen **herramientas** (tools) con su esquema de entrada, su descripción y su resultado.

La arquitectura del caso propio es:

```text
                        Usuario (Gradio)
                              |
                 Agente LangChain (host) + llama3.2:3b
                              |
              |            |            |            |
        HTTP :9090   HTTP :9091   HTTP :9092   HTTP :9093
      (streamable-http, una sesion MCP por servidor)
              |            |            |            |
   ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌─────────────────┐
   │ RecetasDocMCP  │ │ CocinaUtilsMCP │ │ DatosCocinaMCP │ │ AlimentosAPIMCP │
   │ buscar_recetas │ │ convertir_vol  │ │ kcal por 100g  │ │ info_producto   │
   │ leer_receta    │ │ escalar_cant   │ │ alergenos FDA  │ │ OpenFoodFacts   │
   │ archivo JSON   │ │ tablas en cod. │ │ + nevera (SQL, │ │ API viva, sin   │
   │ -> URL de cita │ │ -> exactitud   │ │ solo lectura)  │ │ cache respaldo  │
   └────────────────┘ └────────────────┘ └────────────────┘ └─────────────────┘
```

### 1.1 ¿Por qué este caso y por qué dos servidores separados?

1. **Documentos con cita obligatoria**: el servidor de recetas devuelve, en cada hit, la URL de la página web de origen; el chatbot puede responder "con referencias a los documentos usados", exactamente lo que se pide en la demo de la entrega (video).
2. **Cómputo exacto, no alucinado**: el LLM es pésimo multiplicando gramos o convirtiendo tazas; una tool MCP determinística lo hace perfecto (igual que el rol de la `calculadora` en los ejemplos guía, aunque aquí con dominio y datos propios).
3. **Separación de responsabilidades**: documentos y cálculo no comparten estado, y separarlos en dos servidores independiente demuestra la propiedad clave de MCP: **un host consume N servidores heterogéneos por el mismo protocolo**, sin cambiar nada del agente.

### 1.2 Aportaciones de autoría propia respecto a las guías de la sesión

Frente a los notebooks guía (que consumen los servidores de ejemplo `weather` y `calculator`, en otro dominio y sin corpus), esta solución añade:

1. **Cuatro servidores MCP diseñados desde cero** (`RecetasDocMCP`, `CocinaUtilsMCP`, `DatosCocinaMCP` y `AlimentosAPIMCP`, FastMCP con transporte streamable-http), en el dominio culinario y con herramientas propias, en vez de las de ejemplo.
2. **Un corpus y un índice construidos por el taller**: 19.249 recetas curadas del Taller 5, serializadas a JSON y servidas mediante un índice invertido propio (pesos por campo, normalización sin tildes y tratamiento del plural) — un conjunto de datos nuevo respecto a la guía, que no consume dataset alguno.
3. **Dos fuentes complementarias en el mismo problema de negocio, cada una de un tipo distinto**: una base de datos real **SQLite** con datos sintéticos honestos (kcal por 100 g, alergenos orientativos de los 9 grupos mayores de la FDA y la nevera del usuario, todos en modo solo lectura) y una **API viva de terceros** (OpenFoodFacts, sin llave) con respaldo en caché para que la corrida nunca se detenga — archivos+SQL+API, las tres formas de conectividad MCP.
4. **Arranque automático y robusto de la infraestructura**: `ollama serve` y los cuatro servidores se lanzan desde el notebook y se esperan con sondeos de salud por puerto, frente al arranque manual pedido en las guías.
5. **Un experimento dirigido de 39 turnos (13 consultas x 3 modos)** con métricas de acierto en la selección de tool, de referencias y de latencia, más gráficos comparativos; y una **batería de validación de las 9 herramientas en 90 turnos** (categoría `tool`: 27 consultas x 3 modos; categoría `todas_las_tools`: 2 mezclas x 3 modos; categoría `sin_datos`: 1 caso x 3 modos), ordenada por categoría de pregunta, tool y modo de ejecución: la guía no hace experimentación ni validación.
6. **Un análisis cualitativo de los fallos**, tanto de la batería de validación (sección 8) como de los turnos fallidos del experimento (sección 9), con sus causas: fallo de invocación, redacción que pierde datos y aritmética que sustituye al resultado de la tool.
7. **La traza MCP visible en la interfaz**: cada respuesta de Gradio muestra el modo, las tools invocadas y la latencia; es la evidencia en pantalla de que el agente consumió los servidores.
""")

# ==========================================================================
# Configuración del entorno
# ==========================================================================
md(r"""
## 2. Configuración del entorno
""")

code(r"""
import warnings

warnings.filterwarnings('ignore')

try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

print('¿Ejecutando en Google Colab?', IN_COLAB)
""")

md(r"""
Se instalan las librerías con las mismas versiones acotadas que en los notebooks guía de la sesión (`mcp>=1.24`, `langchain-mcp-adapters>=0.3`), más las del corpus y el EDA (`datasets`, `pandas`, `matplotlib`, `wordcloud`).
""")

code(r"""
!test '{IN_COLAB}' = 'True' && pip install -q "mcp>=1.24.0,<2.0.0" "langchain-mcp-adapters>=0.3.0,<0.4.0" langchain langchain-core langchain-ollama langgraph httpx gradio ollama datasets pandas matplotlib wordcloud

# En local, instalar con su gestor de paquetes de preferencia.
""")

md(r"""
### 2.1 Servidores MCP propios: obtención de los archivos

Los cuatro servidores MCP del caso propio están en `Taller_6/mcp_servers/` del repositorio del equipo (junto con el sembrador de la base de datos y la caché de respaldo de la API). En Colab, al abrir el notebook desde GitHub, los archivos auxiliares no siempre se descargan, así que hay una celda de *bootstrap* que los trae, igual que en los notebooks guía. En local bastan los archivos del repositorio.
""")

code(r"""
# En Colab se descargan los servidores propios desde el repositorio del equipo,
# porque al abrir un notebook desde GitHub los archivos auxiliares no se bajan.
is_colab = bool(globals().get('IN_COLAB', False))
if is_colab:
    !mkdir -p mcp_servers
    !wget -q -O mcp_servers/recetas_mcp_server.py https://github.com/yeavil-neny/NLP-ProcesamientoLeguajeNatural/raw/refs/heads/main/Taller_6/mcp_servers/recetas_mcp_server.py
    !wget -q -O mcp_servers/cocina_mcp_server.py https://github.com/yeavil-neny/NLP-ProcesamientoLeguajeNatural/raw/refs/heads/main/Taller_6/mcp_servers/cocina_mcp_server.py
    !wget -q -O mcp_servers/datos_mcp_server.py https://github.com/yeavil-neny/NLP-ProcesamientoLeguajeNatural/raw/refs/heads/main/Taller_6/mcp_servers/datos_mcp_server.py
    !wget -q -O mcp_servers/seed_datos.py https://github.com/yeavil-neny/NLP-ProcesamientoLeguajeNatural/raw/refs/heads/main/Taller_6/mcp_servers/seed_datos.py
    !wget -q -O mcp_servers/api_alimentos_mcp_server.py https://github.com/yeavil-neny/NLP-ProcesamientoLeguajeNatural/raw/refs/heads/main/Taller_6/mcp_servers/api_alimentos_mcp_server.py
    !wget -q -O mcp_servers/api_cache.json https://github.com/yeavil-neny/NLP-ProcesamientoLeguajeNatural/raw/refs/heads/main/Taller_6/mcp_servers/api_cache.json
    print('Servidores MCP del caso propio descargados para Colab.')
else:
    print('Entorno local detectado: se usan los archivos del repositorio.')
""")

# ==========================================================================
# Corpus
# ==========================================================================
md(r"""
## 3. El corpus: `RecetasDeLaAbuela` (mismo dominio del taller anterior, ahora como documentos MCP)

Se reutiliza el corpus culinario hispanoamericano `somosnlp/RecetasDeLaAbuela` (versión curada `version_1`, 20.236 recetas raspadas de webs de cocina con título, URL original, ingredientes, pasos y metadatos). La decisión es deliberada: en el Taller 5 estas recetas se *incrustaron* en un índice vectorial y el agente era un RAG monolítico; aquí el mismo contenido encabeza **cuatro servidores MCP con herramientas declaradas** (documentos, utilidades de cálculo, datos de consulta en SQLite y una API viva de productos), lo que permite comparar las dos filosofías sobre datos idénticos. La novedad de datos de este taller va por las fuentes complementarias (SQLite y API), no por reemplazar el corpus: así la comparación T5 vs T6 queda controlada.
""")

code(r"""
# Carga del dataset de Hugging Face y renombrado de columnas a snake_case,
# igual que en el Taller 5, para que la curación sea idéntica entre talleres.
import pandas as pd

pd.set_option('display.max_colwidth', 60)

from datasets import get_dataset_config_names, load_dataset

configs = get_dataset_config_names('somosnlp/RecetasDeLaAbuela')
print('Configuraciones:', configs)

dataset = load_dataset('somosnlp/RecetasDeLaAbuela', 'version_1', split='train')

dataset = dataset.rename_columns({
    'Id': 'id', 'Nombre': 'nombre', 'URL': 'url', 'Ingredientes': 'ingredientes',
    'Pasos': 'pasos', 'Pais': 'pais', 'Duracion': 'duracion', 'Categoria': 'categoria',
    'Comensales': 'comensales', 'Dificultad': 'dificultad',
})
KEEP = ['id', 'nombre', 'url', 'ingredientes', 'pasos', 'pais', 'duracion', 'categoria', 'comensales', 'dificultad']
dataset = dataset.remove_columns([c for c in dataset.column_names if c not in KEEP])
dataset.set_format(type='pandas')
df_raw = dataset.to_pandas()
df_raw.head(10)
""")

md(r"""
### 3.1 EDA compacto del corpus

El EDA completo (nulos, longitudes, léxico, nube de palabras) está en el Taller 5 sobre el mismo dataset; aquí se repiten solo las dos vistas que justifican las decisiones de diseño del servidor MCP: la completitud de los campos citables y la distribución por país.
""")

code(r"""
# Completitud de los campos que el servidor MCP usará para citar y filtrar.
nulls = df_raw.isnull().sum()
print('Recetas crudas:', len(df_raw))
print('\nNulos por columna:')
for col, n in nulls.items():
    print(f'  {col:<12} {n:>6} ({n / len(df_raw):.1%})')
""")

md(r"""
**Observación (corrida real).** Los campos con los que el servidor construye las citas (`id`, `nombre`, `url`) y el contenido técnico (`ingredientes`, `pasos`) llegaron al 100% en las 20.236 recetas crudas, mientras que los metadatos descriptivos concentran los nulos alrededor del 30% (`pais` 27.6%, `duracion` 32.8%, `categoria` 33.3%, `comensales` 32.7%, `dificultad` 31.9%). Consecuencia: la curación puede exigir URL sin perder contenido útil, porque sin fuente no hay cita verificable para el video, y el chatbot no puede prometer atributos (país, duración) que en un tercio del corpus no existen.
""")

code(r"""
# Distribución por país: define qué recetas priorizará el buscador por defecto.
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
(df_raw.pais.value_counts().head(10)).plot.barh(ax=ax[0])
ax[0].set_title('Recetas por país (top 10)')
ax[0].set_xlabel('Recetas')

minutos = df_raw.duracion.dropna().str.split(':').apply(
    lambda p: int(p[0]) * 60 + int(p[1]) if len(p) == 2 else None).dropna()
minutos.hist(ax=ax[1], bins=40)
ax[1].set_title('Duración de la receta (minutos)')
ax[1].set_xlabel('Minutos')
plt.show()
""")

md(r"""
**Observación (corrida real).** El desbalance por país quedó confirmado y es fuerte: España domina con algo más de 9.000 recetas (cerca de la mitad del corpus), seguida de México (~2.100) y Perú (~1.100); los demás países quedan por debajo de los 500 registros y Colombia no llega a los 250. En duraciones, casi todo el corpus declara tiempos inferiores a una hora, con la mayor concentración entre los 10 y los 20 minutos y una cola aislada que llega a unos 490 minutos. Consecuencia práctica: las citas del chatbot provendrán sobre todo de webs gastronómicas de España y México.
""")

md(r"""
### 3.2 Curación y preparación del corpus para el servidor MCP

La misma curación mínima y determinística del Taller 5 (registros vacíos, URLs no válidas, duplicados por URL, longitud mínima de 25 palabras en los pasos), más un paso nuevo: **serializar el corpus curado a JSON** para que el servidor MCP lo consuma. El servidor no conoce Hugging Face ni `pandas`: su única dependencia de datos es el archivo `recetas_corpus.json`.
""")

code(r"""
# Curación idéntica a la del Taller 5, para que ambos talleres sirvan el
# mismo corpus. Filtros: registros vacios, URL no valida, duplicados por URL
# y recetas con menos de 25 palabras de procedimiento.
def curar(df):
    vacios = df.nombre.isna() | df.url.isna() | df.pasos.isna()
    df = df[~vacios].copy()
    df = df[df.url.str.startswith('http')]
    df = df.drop_duplicates(subset='url')
    n_pasos = df.pasos.apply(lambda t: len(t.split()))
    df = df[n_pasos >= 25]
    return df.reset_index(drop=True)

df = curar(df_raw)
print(f'Recetas después de la curación: {len(df)} '
      f'(de {len(df_raw)} crudas, {len(df_raw) - len(df)} eliminadas)')
""")

md(r"""
**Observación (corrida real).** La curación conservó 19.249 de las 20.236 recetas crudas (987 eliminadas, 4.9%), la misma cifra exacta del Taller 5 y de las corridas previas de este notebook: el paso es reproducible entre talleres y entre corridas. El corpus serializado quedó en `mcp_servers/recetas_corpus.json` con 19.249 recetas y 34.0 MB; la siembra SQLite complementaria dejó 58 alimentos, 40 filas de alergenos y 6 ingredientes de la nevera.
""")

code(r"""
# Serialización del corpus curado a JSON para el servidor MCP de recetas.
# El servidor lee este archivo al arrancar y construye su indice invertido.
import json
from pathlib import Path

SERVERS_DIR = Path('mcp_servers') if (Path.cwd() / 'mcp_servers').exists() else Path('Taller_6') / 'mcp_servers'
corpus_path = SERVERS_DIR / 'recetas_corpus.json'

campos = ['id', 'nombre', 'url', 'ingredientes', 'pasos', 'pais', 'duracion', 'categoria', 'comensales', 'dificultad']
registros = []
for fila in df[campos].to_dict(orient='records'):
    limpio = {}
    for col, valor in fila.items():
        if pd.isna(valor):
            limpio[col] = None
        elif hasattr(valor, 'item'):
            limpio[col] = valor.item()  # tipos de numpy -> tipos nativos de Python
        else:
            limpio[col] = valor
    registros.append(limpio)
with corpus_path.open('w', encoding='utf-8') as f:
    json.dump(registros, f, ensure_ascii=False)

peso_mb = corpus_path.stat().st_size / 1e6
print(f'Corpus para el servidor MCP: {corpus_path} '
      f'({len(registros)} recetas, {peso_mb:.1f} MB)')
""")

md(r"""
### 3.3 Siembra de la base de datos complementaria (SQLite, solo consulta)

El tercer tipo de fuente del caso es una base de datos real: **SQLite**, sembrada con datos sintéticos y orientativos en tres tablas (`calorias`: kcal por 100 g de alimentos genéricos; `alergias`: alergenos más probables según los 9 grupos mayores de la lista de la FDA; `inventario`: la nevera del usuario). El sembrado es **determinístico y reproducible**: este script reinicia la base en cada corrida y el servidor MCP que la lee **no tiene herramientas de escritura** — es una fuente de consulta que complementa las respuestas de las recetas, no un estado que el chatbot modifique.
""")

code(r"""
# Siembra determinista de la base SQLite complementaria (cocina_datos.db).
# El script seed_datos.py se descargo con el bootstrap; DROP + CREATE + INSERT.
import subprocess, sys

resultado_seed = subprocess.run(
    [sys.executable, '-I', str(SERVERS_DIR / 'seed_datos.py')],
    capture_output=True, text=True,
)
print(resultado_seed.stdout.strip())
if resultado_seed.returncode != 0:
    print(resultado_seed.stderr)
    raise RuntimeError('El sembrado de la base SQLite fallo.')
""")

# ==========================================================================
# Ollama
# ==========================================================================
md(r"""
## 4. Cargando a Ollama

El mismo modelo local del Taller 5 y de los guías (`llama3.2:3b`, con `temperature=0`) para que la única variable nueva entre talleres sea la arquitectura MCP, no el generador.

A diferencia de los notebooks guía, que piden arrancar `ollama serve` a mano en una terminal embebida, aquí el arranque es **automático y controlado**: se comprueba si el servicio ya responde y, si no, se lanza en segundo plano con `nohup` y se espera con un bucle de sondeo hasta que la API contesta. El **orden importa y es parte de la lección de la corrida del 17-oct-2026 en runtime fresco**: `ollama pull` requiere el servicio atendiendo (la corrida en un Colab recién instalado ejecutó el pull antes de arrancar `ollama serve`, el modelo no se descargó y cada turno devolvió `model not found (404)`). El orden de esta sección queda entonces: (1) instalar Ollama si falta, (2) arrancar el servicio y esperar su salud, (3) descargar el modelo solo si no está presente (la re-ejecución no lo vuelve a bajar). Esto hace el notebook verdaderamente ejecutable de principio a fin (criterio de reproducibilidad de la rúbrica) y evita la lección aprendida en la corrida del Taller 5, donde el servicio se detuvo a mitad de la ejecución.
""")

code(r"""
# Instalación de Ollama en Colab (en local se asume instalado).
!test '{IN_COLAB}' = 'True' && sudo apt install -y zstd
!test '{IN_COLAB}' = 'True' && if ! type ollama > /dev/null; then curl -fsSL https://ollama.com/install.sh | sh; else echo "Ollama ya está instalado."; fi
""")

code(r"""
# Arranque automatico de `ollama serve`: se hace ANTES del pull (el pull
# necesita el servicio atendiendo); solo se lanza si la API todavia no
# responde, y se espera con sondeos cortos hasta que contesta.
import httpx, subprocess, sys, time

def ollama_saludable(url='http://localhost:11434/api/tags'):
    try:
        return httpx.get(url, timeout=2.0).status_code == 200
    except httpx.HTTPError:
        return False

if ollama_saludable():
    print('Ollama ya estaba atendiendo en http://localhost:11434.')
else:
    if IN_COLAB:
        # nohup mantiene el proceso vivo tras terminar la celda; el log queda
        # en /tmp/ollama_serve.log para diagnosticar si algo falla.
        subprocess.Popen(
            ['bash', '-lc',
             'nohup ollama serve > /tmp/ollama_serve.log 2>&1 &'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        print('En local inicie `ollama serve` manualmente si no está corriendo.')
    for _ in range(60):
        if ollama_saludable():
            break
        time.sleep(1)
    print('¿Ollama saludable?', ollama_saludable())
""")

code(r"""
# Descarga del modelo (2.0 GB solo la primera vez): si `ollama list` ya lo
# reporta, la celda no vuelve a descargarlo. Corre DESPUES del arranque del
# servicio, porque el pull requiere el servidor atendiendo.
!ollama list | grep -q llama3.2:3b || ollama pull llama3.2:3b
""")

# ==========================================================================
# Servidores MCP
# ==========================================================================
md(r"""
## 5. Los servidores MCP del caso propio

Los cuatro se escriben con el SDK oficial de Python (`FastMCP`) y se sirven por **transporte streamable-HTTP** en puertos fijos: recetas en `9090`, cocina en `9091`, datos SQLite en `9092` y API de productos en `9093` (puertos distintos a los `9080`/`9081` de los ejemplos guía). La elección del transporte sigue el argumento de la sesión: **stdio** acopla cliente y servidor por descriptores de archivo (frágil en Colab), mientras HTTP hace explícita la separación host-servidor y funciona igual en cualquier entorno.

Cada herramienta se declora con el decorador `@mcp.tool()`; su **docstring es parte del contrato**: es lo que el modelo lee para decidir si y cómo invocarla. Por eso las descripciones explicitan el formato de entrada aceptado — decisivo con un LLM pequeño como llama3.2:3b, que falla con parámetros estructurados complejos y acierta con cadenas simples como `"2 tazas de leche"`.

Las celdas siguientes imprimen el código fuente de los servidores tal como quedaron en `Taller_6/mcp_servers/` del repositorio, para que la implementación sea auditable sin salir del notebook.
""")

code(r"""
# Resolucion de la carpeta con los servidores: en Colab quedan bajados junto
# al notebook; en local, dentro de Taller_6/mcp_servers del repositorio.
from pathlib import Path

candidate_dirs = [
    Path.cwd() / 'mcp_servers',
    Path.cwd() / 'Taller_6' / 'mcp_servers',
]
SERVERS_DIR = next((p for p in candidate_dirs if p.exists()), None)
if SERVERS_DIR is None:
    raise FileNotFoundError(
        'No se encontró mcp_servers. En Colab debe correrse primero la celda de bootstrap; en local, esta celda corre desde la carpeta del taller.'
    )

recetas_server = SERVERS_DIR / 'recetas_mcp_server.py'
cocina_server = SERVERS_DIR / 'cocina_mcp_server.py'
datos_server = SERVERS_DIR / 'datos_mcp_server.py'
api_server = SERVERS_DIR / 'api_alimentos_mcp_server.py'
seed_datos = SERVERS_DIR / 'seed_datos.py'
cache_api = SERVERS_DIR / 'api_cache.json'
FALTAN = [p for p in (recetas_server, cocina_server, datos_server, api_server, seed_datos, cache_api) if not p.exists()]
if FALTAN:
    raise FileNotFoundError(f'Faltan archivos MCP en {SERVERS_DIR}: ' + ', '.join(p.name for p in FALTAN))

print('Servidores MCP del caso propio:')
for p in (recetas_server, cocina_server, datos_server, api_server):
    print(' -', p)
print('Archivos de apoyo:', seed_datos.name, '(sembrador) y', cache_api.name, '(cache de la API).')
""")

code(r"""
# Fuente completa del servidor de documentos de recetas (auditable aqui).
print(recetas_server.read_text(encoding='utf-8'))
""")

code(r"""
# Fuente completa del servidor de utilidades de cocina (auditable aqui).
print(cocina_server.read_text(encoding='utf-8'))
""")

code(r"""
# Fuente completa del servidor de datos de consulta en SQLite (auditable aqui).
print(datos_server.read_text(encoding='utf-8'))
""")

code(r"""
# Fuente completa del servidor de la API de productos (auditable aqui).
print(api_server.read_text(encoding='utf-8'))
""")

md(r"""
### 5.1 Inicio de los servidores como procesos

El notebook levanta los cuatro servidores como `subprocess.Popen` con su bitácora en archivos temporales (`/tmp/*_mcp.log`, y no tuberías, para que el búfer del proceso no se llene) y **sondea los puertos hasta que responden**, en lugar de dormir `time.sleep(2)` a ciegas como en el notebook guía. Si un servidor ya estuviera atendiendo el puerto (re-ejecución de la celda), se reutiliza en lugar de lanzar un duplicado. El servidor de la API no toca la red al arrancar (solo cuando un turno lo invoca), de modo que su arranque no depende de la disponibilidad del servicio externo.
""")

code(r"""
# Inicio de los dos servidores MCP con verificacion de salud por puerto.
import subprocess, time

def proceso_servidor(ruta_archivo, puerto, log):
    return subprocess.Popen(
        ['python', str(ruta_archivo)],
        stdout=open(log, 'w'), stderr=subprocess.STDOUT,
    )

def puerto_arriba(puerto):
    try:
        httpx.get(f'http://localhost:{puerto}/mcp', timeout=1.0)
        return True
    except httpx.HTTPError:
        return False

# (archivo, puerto, log) de cada servidor propio: recetas 9090, cocina 9091,
# datos SQLite 9092 y API de productos 9093.
SERVIDORES = [
    (recetas_server, 9090, '/tmp/recetas_mcp.log'),
    (cocina_server, 9091, '/tmp/cocina_mcp.log'),
    (datos_server, 9092, '/tmp/datos_mcp.log'),
    (api_server, 9093, '/tmp/api_mcp.log'),
]

mcp_procs = {}
for ruta, puerto, log in SERVIDORES:
    if not puerto_arriba(puerto):
        mcp_procs[puerto] = proceso_servidor(ruta, puerto, log)
        print(f'Iniciando {ruta.name} en el puerto {puerto} (log: {log})')
    else:
        print(f'El puerto {puerto} ya estaba atendido; se reutiliza.')

# Sondeo: esperamos hasta 60 s a que ambos puertos respondan.
tope = time.time() + 60
pendientes = [p for _, p, _ in SERVIDORES]
while pendientes and time.time() < tope:
    pendientes = [p for p in pendientes if not puerto_arriba(p)]
    if pendientes:
        time.sleep(1)
print('Puertos MCP saludables:', {p: puerto_arriba(p) for _, p, _ in SERVIDORES})
""")

md(r"""
## 6. Cliente MCP y agente

`MultiServerMCPClient` abre una sesión HTTP con cada servidor y **descubre las herramientas automáticamente**: el cliente pregunta a cada servidor por su lista de tools y las adapta al formato de herramientas de LangChain. `create_agent` (sobre LangGraph) construye entonces el agente ReAct que puede emitir llamadas a herramientas y consumir sus resultados. No hay que registrar nada a mano: lo que se agregue o cambie en los servidores aparecerá aquí sin tocar el código del host.
""")

code(r"""
# Cliente MCP multi-servidor: una entrada por servidor, con su transporte y su URL.
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama

MODEL = 'llama3.2:3b'

client = MultiServerMCPClient(
    {
        'recetas': {
            'transport': 'http',
            'url': 'http://localhost:9090/mcp',  # servidor RecetasDocMCP
        },
        'cocina': {
            'transport': 'http',
            'url': 'http://localhost:9091/mcp',  # servidor CocinaUtilsMCP
        },
        'datos': {
            'transport': 'http',
            'url': 'http://localhost:9092/mcp',  # servidor DatosCocinaMCP (SQLite)
        },
        'api': {
            'transport': 'http',
            'url': 'http://localhost:9093/mcp',  # servidor AlimentosAPIMCP (OpenFoodFacts)
        },
    }
)

mcp_tools = await client.get_tools()  # descubrimiento automatico de tools
print('Herramientas descubiertas por MCP:')
for tool in mcp_tools:
    print(f' - {tool.name}: {tool.description.splitlines()[0]}')
""")

code(r"""
# LLM local y agente ReAct sobre las herramientas MCP descubiertas.
from langchain.agents import create_agent

llm = ChatOllama(model=MODEL, temperature=0)
agent_mcp = create_agent(model=llm, tools=mcp_tools)
print('Agente creado con', len(mcp_tools), 'herramientas MCP:',
      [t.name for t in mcp_tools])
""")

# ==========================================================================
# Orquestación de la respuesta
# ==========================================================================
md(r"""
## 7. Orquestación de la respuesta con tres modos

El chatbot conserva los tres modos del notebook guía, pero la selección de herramienta se adapta al nuevo dominio (recetas vs. cálculo de cocina) y la redacción final queda sujeta a una instrucción de **citas**: cuando la salida de una herramienta contiene una `FUENTE` o URL, la respuesta debe incluirla.

- **Autonomous**: el agente decide libremente qué herramienta usar (o ninguna).
- **Guided** (por defecto): un mensaje de sistema le prioriza la herramienta sugerida por la heurística del host y pide citar fuentes.
- **Deterministic**: el host ejecuta la herramienta directamente y el LLM solo redacta la respuesta final con el resultado; modo sin sorpresas, ideal para la demo.

**Nota sobre la heurística y los modos**: la heurística del host vive en la celda siguiente y los modos la usan de forma distinta — en Guided la convierte en instrucción para el agente, en Deterministic la ejecuta directamente el host sin llamar al agente, y en Autonomous no se aplica en absoluto (el agente decide libremente). Por eso la comparación de modos de la sección 9 es, en sí misma, el test de si la guía del host aporta valor frente a dejar decidir al LLM.

**Garantía mecánica de fuentes**: la línea de "Fuentes:" no depende de que el LLM la redacte bien (en las dos corridas anteriores salió vacía o sin URL cuando el modelo olvidaba copiarla). Al cierre de cada turno, el host `componer_fuentes()` quita las líneas "Fuentes:" que pudo escribir el modelo y anexa una canónica: **las URLs reales** de las salidas de las herramientas cuando las trae; si ninguna trae URL, **la lista de herramientas MCP utilizadas y su servidor**; y si el turno no usó herramientas, el aviso explícito de que fue una respuesta sin base documental. Así, cada respuesta indica si su información proviene de una página, de un servidor o de la memoria del modelo.
""")

code(r'''
# Heuristica del host: a que servidor/tool pertenece la intencion del usuario.
import re, time
from unicodedata import combining, normalize

NOMBRES_TOOLS = {t.name for t in mcp_tools}
TOOL_POR_NOMBRE = {t.name: t for t in mcp_tools}

SENAL_RECETAS = ['receta', 'cocinar', 'prepara', 'como se hace', 'ingredientes',
                 'pasos', 'plato', 'platillo', 'hornea', 'sazona']
SENAL_COCINA = ['taza', 'cucharada', 'mililitro', 'ml', 'litro', 'gramo',
                'kcal', 'caloria', 'calorias', 'escal', 'duplica', 'doble',
                'comensales', 'porciones', 'onza']
SENAL_DATOS = ['alergia', 'alergico', 'alergica', 'alergenos', 'intoleranc',
               'gluten', 'lactosa', 'frutos secos', 'mani', 'sesamo']
SENAL_INV = ['inventario', 'nevera', 'refrigerador', 'en mi cocina']
SENAL_API = ['openfoodfacts', 'codigo de barras', 'etiqueta', 'embotellado', 'envase']
SENAL_LEER = ['identificador', 'receta completa', 'numero de receta', 'receta numero', 'contenido de la receta']

def minusculas_sin_tildes(texto):
    """Minusculas sin tildes, para que las senales no dependan del acento."""
    texto = normalize('NFKD', texto.lower())
    return ''.join(ch for ch in texto if not combining(ch))

def detectar_tool(pregunta: str, preferida: str) -> str | None:
    """Devuelve el nombre de la tool sugerida, o None si no hay senal clara."""
    if preferida and preferida != 'Auto':
        return preferida
    texto = minusculas_sin_tildes(pregunta)
    # 1) API: un codigo de barras (8-13 digitos) o una senal de producto de marca.
    if re.search(r'\b\d{8,13}\b', texto) or 'codigo de barras' in texto:
        return 'info_producto_api'
    if any(s in texto for s in SENAL_API):
        return 'info_producto_api'
    if any(s in texto for s in SENAL_LEER):
        return 'leer_receta'
    # 2) Datos SQLite: alergias, nevera o tabla de kcal por 100 g.
    if any(s in texto for s in SENAL_DATOS):
        return 'consultar_alergias'
    if any(s in texto for s in SENAL_INV):
        return 'consultar_inventario'
    if 'por 100' in texto and ('kcal' in texto or 'caloria' in texto):
        return 'consultar_calorias'
    # 3) Cocina: equivalencias, escalado o kcal de una cantidad concreta.
    if any(s in texto for s in SENAL_COCINA):
        # Desempate dentro del servidor de cocina segun el patron dominante.
        if re.search(r'\d+\s*(taza|cucharad|mililitro|ml|litro|onza)', texto):
            return 'convertir_volumen'
        if 'kcal' in texto or 'caloria' in texto:
            return 'calcular_kcal'
        return 'escalar_cantidad'
    # 4) Documentos de recetas.
    if any(s in texto for s in SENAL_RECETAS):
        return 'buscar_recetas'
    return None

def mensajes_del_historial(pregunta, historial):
    """Reconstruye los mensajes (rol, contenido) incluyendo el historial de chat."""
    mensajes = []
    for item in (historial or []):
        if item.get('role') in ('user', 'assistant') and item.get('content') is not None:
            mensajes.append((item['role'], item['content']))
    mensajes.append(('user', pregunta))
    return mensajes

def normalizar(texto):
    """Aplana a texto plano cualquier salida (str, lista, dict, ToolMessage)."""
    if texto is None:
        return ''
    if isinstance(texto, str):
        return texto
    if isinstance(texto, (list, tuple)):
        return '\n'.join(p for p in (normalizar(x) for x in texto) if p)
    if isinstance(texto, dict):
        for clave in ('text', 'content', 'result'):
            if clave in texto and texto[clave] is not None:
                return normalizar(texto[clave])
        return str(texto)
    for atributo in ('text', 'content', 'result'):
        valor = getattr(texto, atributo, None)
        if valor is not None:
            return normalizar(valor)
    return str(texto)

def tools_usadas(messages):
    """Nombres de las herramientas que aparecieron en la conversacion."""
    return [getattr(m, 'name', '?') for m in messages if getattr(m, 'type', '') == 'tool']

# De cada tool a la fuente que la sustenta (para la linea canonica de
# Fuentes cuando la salida de la tool no trae URL).
FUENTE_SERVIDOR = {
    'buscar_recetas': 'RecetasDocMCP (archivo JSON con URL de origen)',
    'leer_receta': 'RecetasDocMCP (archivo JSON con URL de origen)',
    'convertir_volumen': 'CocinaUtilsMCP (tablas de equivalencia en codigo)',
    'escalar_cantidad': 'CocinaUtilsMCP (reglas de escalado en codigo)',
    'calcular_kcal': 'CocinaUtilsMCP (tabla nutricional en codigo)',
    'consultar_calorias': 'DatosCocinaMCP (SQLite, tabla calorias)',
    'consultar_alergias': 'DatosCocinaMCP (SQLite, tabla alergias orientativa)',
    'consultar_inventario': 'DatosCocinaMCP (SQLite, tabla inventario)',
    'info_producto_api': 'AlimentosAPIMCP (OpenFoodFacts, API viva sin llave)',
}

def componer_fuentes(respuesta, salidas_tool, tools_usadas_turno):
    """Garantiza la linea de Fuentes despues de la redaccion del LLM.

    Quita la(s) linea(s) "Fuentes:" que pudieron escribir el modelo (a veces
    vacia, a veces sin URL, a veces al inicio de la respuesta) y anexa una
    canonica: con las URLs reales de las salidas de las tools; si ninguna
    trae URL, con las herramientas y su servidor; y si el turno no uso
    herramientas, con el aviso de respuesta sin base documental.
    """
    texto = re.sub(r'(?m)^[ \t]*Fuentes:[^\n]*\n?', '', (respuesta or '').strip()).strip()
    urls = []
    for salida in salidas_tool:
        urls += re.findall(r'https?://\S+', normalizar(salida))
        # La salida ya es texto plano (str): los URLs aparecen igual; este
        # paso tambien cubre listas anidadas aplanadas por normalizar.
    urls = list(dict.fromkeys(urls))
    if urls:
        return texto + '\n\nFuentes:\n' + '\n'.join(f'- {u}' for u in urls)
    if tools_usadas_turno:
        etiquetas = '; '.join(
            f"`{t}` ({FUENTE_SERVIDOR.get(t, 'servidor MCP')})" for t in tools_usadas_turno
        )
        return texto + '\n\nFuentes: herramientas MCP — ' + etiquetas + '.'
    return texto + '\n\nFuentes: respuesta del modelo sin herramientas MCP (sin base documental).'

CITA_SISTEMA = (
    'Responde en español, de forma breve. Cuando la salida de una herramienta contenga '
    'una URL o la palabra FUENTE, incluye esa referencia al final de tu respuesta en una '
    'linea que empiece por "Fuentes: ". No cites URLs que no aparezcan en la salida.'
)

# Payloads deterministicos: extraer el argumento exacto para cada tool.
def construir_payload(tool_name: str, pregunta: str) -> dict:
    if tool_name == 'buscar_recetas':
        return {'consulta': pregunta, 'k': 3}
    if tool_name == 'leer_receta':
        # El host extrae el identificador de la pregunta (la tool exige un id).
        m = re.search(r'\b(\d+)\b', pregunta)
        if not m:
            raise ValueError('Para leer_receta necesito el identificador de la receta.')
        return {'id': int(m.group(1))}
    if tool_name == 'convertir_volumen':
        return {'frase': pregunta}
    if tool_name == 'calcular_kcal':
        m = re.search(r'(\d+[\.,]?\d*)\s*(?:g|gramos?)\s*(?:de|del|d)\s+([a-záéíóúñ ]+)', pregunta, re.I)
        if m:
            return {'gramos': float(m.group(1).replace(',', '.')), 'alimento': m.group(2).strip()}
        return {'gramos': 100.0, 'alimento': pregunta}
    if tool_name == 'escalar_cantidad':
        m = re.search(r'(?:de|para)\s+(\d+)\s+a\s+(\d+)', pregunta)
        factor = float(m.group(2)) / float(m.group(1)) if m else 2.0
        return {'frase': pregunta, 'factor': factor}
    if tool_name == 'consultar_calorias':
        return {'alimento': pregunta}  # la tool hace coincidencia flexible
    if tool_name == 'consultar_alergias':
        return {'alimento': pregunta}
    if tool_name == 'consultar_inventario':
        return {}
    if tool_name == 'info_producto_api':
        m = re.search(r'\b\d{8,13}\b', pregunta)
        return {'consulta': m.group(0) if m else pregunta}
    raise ValueError(f'Tool no soportada: {tool_name}')

async def ejecutar_tool(tool_name: str, pregunta: str):
    tool = TOOL_POR_NOMBRE.get(tool_name)
    if tool is None:
        raise ValueError(f'Herramienta no encontrada: {tool_name}')
    return await tool.ainvoke(construir_payload(tool_name, pregunta))

async def redactar_herramienta(pregunta, tool_name, salida_tool):
    """Redaccion final por el LLM con instruccion de cita, o fallback si Ollama cae."""
    salida = normalizar(salida_tool)
    try:
        sintesis = llm.invoke([
            ('system', CITA_SISTEMA),
            ('user', f"Pregunta: {pregunta}\n\nSalida de la herramienta {tool_name}:\n{salida}\n\nRedacta la respuesta final clara, con su línea de Fuentes si hay URL."),
        ])
        return normalizar(sintesis.content)
    except Exception as exc:
        if 'connection' in str(exc).lower() or 'refused' in str(exc).lower():
            return f"Resultado directo de la herramienta {tool_name}:\n{salida}\n\n(Nota: no hubo conexión con Ollama para redactar la respuesta.)"
        raise

async def responder(pregunta, modo='Guided', preferida='Auto', historial=None,
                    fallback_guided=True):
    """Un turno completo: devuelve (respuesta, traza, segundos).

    La traza deja por escrito el comportamiento MCP del turno, que es lo que
    se usa tanto para la UI como para el experimento comparativo.
    """
    inicio = time.perf_counter()
    seleccionada = detectar_tool(pregunta, preferida)
    traza = {
        'modo': modo, 'tool_seleccionada': seleccionada,
        'tools_usadas': [], 'fallback_guided': False, 'error': None,
    }
    try:
        if modo == 'Deterministic':
            if seleccionada is None:
                return ("No pude inferir una herramienta desde tu mensaje. "
                        "Selecciona una herramienta o reformula la pregunta.", traza, time.perf_counter() - inicio)
            salida = await ejecutar_tool(seleccionada, pregunta)
            traza['tools_usadas'] = [seleccionada]
            answer = await redactar_herramienta(pregunta, seleccionada, salida)
            answer = componer_fuentes(answer, [salida], traza['tools_usadas'])

        elif modo == 'Guided':
            mensajes = mensajes_del_historial(pregunta, historial)
            if seleccionada is not None:
                mensajes = [('system', CITA_SISTEMA + f' Prioriza usar la herramienta {seleccionada} si la pregunta la requiere.')] + mensajes
            resultado = await agent_mcp.ainvoke({'messages': mensajes})
            usadas = tools_usadas(resultado['messages'])
            traza['tools_usadas'] = usadas
            salidas_tool = [normalizar(getattr(m, 'content', '')) for m in resultado['messages']
                            if getattr(m, 'type', '') == 'tool']
            answer = normalizar(resultado['messages'][-1].content)
            answer = componer_fuentes(answer, salidas_tool, usadas)
            if fallback_guided and (not usadas) and seleccionada is not None:
                salida = await ejecutar_tool(seleccionada, pregunta)
                answer = await redactar_herramienta(pregunta, seleccionada, salida)
                traza['tools_usadas'] = [seleccionada]
                traza['fallback_guided'] = True
                answer = componer_fuentes(answer, [salida], traza['tools_usadas'])

        else:  # Autonomous
            resultado = await agent_mcp.ainvoke({'messages': mensajes_del_historial(pregunta, historial)})
            usadas = tools_usadas(resultado['messages'])
            traza['tools_usadas'] = usadas
            salidas_tool = [normalizar(getattr(m, 'content', '')) for m in resultado['messages']
                            if getattr(m, 'type', '') == 'tool']
            answer = normalizar(resultado['messages'][-1].content)
            answer = componer_fuentes(answer, salidas_tool, usadas)
    except Exception as exc:
        traza['error'] = str(exc)
        answer = f"Ocurrió un error: {exc}"
    return normalizar(answer), traza, time.perf_counter() - inicio
''')

# ==========================================================================
# Ejemplos
# ==========================================================================
md(r"""
## 8. Validación del asistente por categoría de pregunta, herramienta y modo de ejecución (90 turnos)

Con las herramientas del protocolo descritas y el agente creado, esta única sección valida el funcionamiento de la solución con el doble orden que fija la estrategia de ejecución: **por categoría de pregunta** (cada una con su tool y su servidor) y, dentro de cada consulta, **por estrategia o modo de ejecución del agente** (Guided, Autonomous, Deterministic). Cada caso corre una sola vez — sin consultas repetidas — y cada turno imprime su salida completa (encabezado, tools usadas y latencia, respuesta final del asistente y línea de "Fuentes" garantizada por el host) para que la entrega sea analizable pregunta por pregunta.

- **Categoría `tool`** (81 turnos): para cada una de las 9 tools se plantean **3 consultas**, y cada consulta corre en los 3 modos. El chequeo pasa si la tool esperada es la invocada. Las 9 tools cubren los cuatro comportamientos de negocio del asistente:

| Comportamiento | Tools (servidor) |
| --- | --- |
| documentos con cita de la fuente | `buscar_recetas`, `leer_receta` (RecetasDocMCP, JSON) |
| cálculo exacto de cocina | `convertir_volumen`, `escalar_cantidad`, `calcular_kcal` (CocinaUtilsMCP) |
| datos de consulta complementarios | `consultar_calorias`, `consultar_alergias`, `consultar_inventario` (DatosCocinaMCP, SQLite) |
| producto envasado por API viva | `info_producto_api` (AlimentosAPIMCP, OpenFoodFacts) |

- **Categoría `todas_las_tools`** (6 turnos): 2 consultas mezcla que cruzan varias tools y varios servidores en un solo turno; cada mezcla corre en los 3 modos. En Guided y Autonomous el chequeo pasa si la cadena completa de tools se produjo; en Deterministic el host solo ejecuta la tool inferida (se registra esa conducta, no un fallo).
- **Categoría `sin_datos`** (3 turnos): 1 consulta con información que no existe ni en el corpus ni en las tools, en los 3 modos — la expectativa correcta es que el agente **no invoque ninguna herramienta** y admita que no puede responder (reproducción honesta del riesgo de alucinacion que MCP evita cuando la herramienta sí responde).

Total de la batería: **90 turnos**. El chequeo y la latencia quedan en `filas_bateria` y se agregan en las tablas de resumen del final.
""")

code(r"""
# Bateria de validacion: 3 consultas por cada una de las 9 tools del caso.
# La celda se autoabastece de MODOS (asi corren celdas sueltas sin haber
# ejecutado antes la seccion 9 del experimento, donde tambien se define).
MODOS = ['Guided', 'Autonomous', 'Deterministic']

VALIDACION = [
    ('buscar_recetas', [
        '¿Cómo preparo arepas de queso? Cita la receta que uses.',
        'Dame una receta de ceviche de pescado.',
        '¿Qué ingredientes lleva el sancocho de gallina?',
    ]),
    ('leer_receta', [
        'Muestra la receta completa con identificador 1.',
        '¿Qué contiene la receta numero 2?',
        'Dame el contenido de la receta cuyo identificador es 3.',
    ]),
    ('convertir_volumen', [
        '¿Cuántos ml hay en 3 tazas?',
        'Convierte 500 ml a tazas.',
        '¿Cuántos mililitros son 8 onzas?',
    ]),
    ('calcular_kcal', [
        '¿Cuántas kcal tienen 150 gramos de queso?',
        '¿Cuántas kcal tienen 200 gramos de pollo?',
        'Kcal de 100 gramos de arroz.',
    ]),
    ('escalar_cantidad', [
        'Escala 500 gramos de masa para 8 comensales si la receta original dice 500 gramos.',
        'Escala 300 gramos de arroz para 6 comensales.',
        'Duplica las porciones de la receta.',
    ]),
    ('consultar_calorias', [
        '¿Cuántas kcal por 100 gramos tienen el arroz?',
        '¿Cuántas kcal por 100 gramos tiene el queso?',
        'Dame las kcal por 100 g del pollo.',
    ]),
    ('consultar_alergias', [
        '¿La pasta es apta para alguien alérgico al gluten?',
        '¿El camaron tiene alergenos de cuidado?',
        '¿El queso es adecuado para alguien con alergia a la lactosa?',
    ]),
    ('consultar_inventario', [
        '¿Qué tengo en la nevera?',
        'Lista mi inventario de cocina.',
        '¿Hay arroz en la nevera?',
    ]),
    ('info_producto_api', [
        'Consulta el producto con código de barras 3017620422003.',
        'Busca en OpenFoodFacts el código de barras 5449000000996.',
        '¿Cuántas kcal tiene el producto 5449000000996 segun la API?',
    ]),
]

MEZCLAS = [
    ('Busca una receta sencilla de ensalada, revisa qué tengo en la nevera '
     'y dime cuántas kcal tienen 200 gramos de aguacate.',
     ['buscar_recetas', 'consultar_inventario', 'calcular_kcal']),
    ('Busca la receta del sancocho de gallina y muestrala completa por su '
     'identificador, escala 500 gramos de papa para 8 comensales, dime las '
     'kcal por 100 gramos de la papa y si es apta para alérgicos al gluten.',
     ['buscar_recetas', 'leer_receta', 'escalar_cantidad', 'consultar_calorias',
      'consultar_alergias']),
]

SIN_DATOS = 'Recomiendame un restaurante japonés cerca de la Torre Eiffel con reserva para mañana.'

async def validar_caso(tipo, ref, consulta, modo, esperada):
    # Un turno de la bateria: la regla de ok depende del tipo de caso y del
    # modo (docstring evitada: el bloque de celda va entre comillas triples).
    resp, traza, seg = await responder(consulta, modo=modo)
    usadas = traza.get('tools_usadas') or []
    if tipo == 'tool':
        ok = esperada in usadas
    elif tipo == 'mezcla':
        # En Deterministic el host solo ejecuta la tool inferida (no hay
        # encadenamiento): se registra esa conducta, no un fallo.
        ok = (sum(t in usadas for t in esperada) == len(esperada)
              if modo != 'Deterministic' else len(usadas) == 1)
    else:  # abstencion: la respuesta correcta NO usa ninguna herramienta
        ok = len(usadas) == 0
    return {'tipo': tipo, 'ref': ref, 'modo': modo,
            'usadas': ','.join(usadas) or '(ninguna)', 'ok': ok,
            'latencia_s': round(seg, 1), 'resp': resp}

async def correr_bateria():
    # Orden de la bateria (estrategia de ejecucion):
    #   CATEGORIA tool: herramienta -> consulta -> modo
    #   CATEGORIA todas_las_tools: mezcla -> modo
    #   CATEGORIA sin_datos: modo
    # Cada turno se imprime COMPLETO (respuesta + Fuentes garantizada) para
    # que la entrega sea analizable pregunta por pregunta.
    filas = []
    print('CATEGORIA tool — 3 consultas x 3 modos por cada herramienta')
    for herramienta, consultas in VALIDACION:
        print(f'\n== {herramienta} ==')
        for n, consulta in enumerate(consultas, 1):
            for modo in MODOS:
                f = await validar_caso('tool', herramienta, consulta, modo, herramienta)
                f['caso'] = n
                filas.append(f)
                print(f"\n  caso {n} [{f['modo']}] tools={f['usadas']} ({f['latencia_s']:.1f} s)")
                print(f['resp'])
    print('\nCATEGORIA todas_las_tools — 2 mezclas x 3 modos')
    for n, (consulta, esperadas) in enumerate(MEZCLAS, 1):
        for modo in MODOS:
            f = await validar_caso('mezcla', f'mezcla {n}', consulta, modo, esperadas)
            f['caso'] = n
            filas.append(f)
            print(f"\n  mezcla {n} [{f['modo']}] tools={f['usadas']} ({f['latencia_s']:.1f} s)")
            print(f['resp'])
    print('\nCATEGORIA sin_datos — el agente debe abstenerse (3 modos)')
    for modo in MODOS:
        f = await validar_caso('abstencion', 'sin datos', SIN_DATOS, modo, None)
        filas.append(f)
        print(f"\n  [{f['modo']}] tools={f['usadas']} ({f['latencia_s']:.1f} s)")
        print(f['resp'])
    return filas

filas_bateria = await correr_bateria()
""")

md(r"""
**Observación (corrida real).** POR LLENAR — resultado turno a turno de la batería: las 9 herramientas con sus 3 casos x 3 modos (categoría `tool`), las 2 mezclas x 3 modos (categoría `todas_las_tools`) y el caso sin datos x 3 modos (categoría `sin_datos`), con las latencias.
""")

code(r"""
# Resumen de la batería: acierto por (categoria, herramienta, modo).
resumen_bateria = (
    pd.DataFrame(filas_bateria)
    .groupby(['tipo', 'ref', 'modo'])
    .agg(aciertos=('ok', 'sum'), casos=('ok', 'count'),
         acierto_pct=('ok', lambda s: round(100 * s.mean(), 1)),
         latencia_media_s=('latencia_s', 'mean'))
    .round(1)
)
display(resumen_bateria)
""")

md(r"""
**Observación (corrida real).** POR LLENAR — lectura del resumen de la batería: qué herramientas pasaron las 3 validaciones, cómo se comportaron las mezclas y si el agente se abstuvo ante información inexistente.
""")

# ==========================================================================
# Experimento
# ==========================================================================
md(r"""
## 9. Experimento: ¿qué modo de ejecución conviene?

Con cada herramienta validada unidad por unidad y en cadena (sección 8), la pregunta siguiente es de diseño: ¿cuál de los tres modos conviene para dar servicio? Los tres modos encarnan una hipótesis distinta sobre el protocolo: *el agente puede decidir* (Autonomous), *le basta una guía* (Guided) o *no conviene decidirle* (Deterministic). El experimento las confronta con un conjunto fijo de 13 consultas en cinco categorías, que cubren los cuatro servidores; el orden de ejecución es modo → categoría → consulta:

- `documentos`: 4 consultas que deben disparar `buscar_recetas` (o `leer_receta`).
- `calculo`: 3 consultas que deben disparar una tool de cocina (`convertir_volumen`, `escalar_cantidad` o `calcular_kcal`).
- `datos`: 3 consultas que deben disparar una tool del servidor SQLite (`consultar_calorias`, `consultar_alergias` o `consultar_inventario`).
- `api`: 1 consulta con código de barras que debe disparar `info_producto_api`.
- `general`: 2 consultas de conversación donde **no** debería invocarse ninguna tool.

Para cada modo se mide: (a) si la tool usada es la esperada, (b) si la respuesta contiene una referencia `http` cuando la categoría lo pedía, (c) la latencia del turno. Se ejecuta en modo Guided sin tool preferida, para medir solo el efecto del mensaje de sistema.
""")

code(r"""
# Consultas de prueba con su categoria y tool esperada (None = no usar tools).
from itertools import product

CASOS = [
    # (consulta, categoria, tool_esperada) — sin repetir consultas de la
    # bateria de la seccion 8: cada caso corre una sola vez en el notebook.
    ('¿Cómo se prepara el ajiaco santafereño?', 'documentos', 'buscar_recetas'),
    ('Dame una receta de pozole rojo mexicano.', 'documentos', 'buscar_recetas'),
    ('¿Qué lleva el lomo saltado peruano?', 'documentos', 'buscar_recetas'),
    ('Encuentra una receta de tortilla de patatas y dime su fuente.', 'documentos', 'buscar_recetas'),
    ('¿Cuántos ml hay en 4 tazas?', 'calculo', 'convertir_volumen'),
    ('¿Cuántas kcal tienen 120 gramos de atún?', 'calculo', 'calcular_kcal'),
    ('Escala 400 gramos de pasta para 6 comensales si la receta original dice 400 gramos.', 'calculo', 'escalar_cantidad'),
    ('¿Cuántas kcal por 100 gramos tiene el aguacate?', 'datos', 'consultar_calorias'),
    ('¿El salmon es apto para alguien alérgico?', 'datos', 'consultar_alergias'),
    ('¿Hay leche en la nevera?', 'datos', 'consultar_inventario'),
    ('Consulta en la API el producto con código de barras 737628064502.', 'api', 'info_producto_api'),
    ('Hola, ¿qué puedes hacer?', 'general', None),
    ('Gracias, hasta luego.', 'general', None),
]

MODOS = ['Guided', 'Autonomous', 'Deterministic']

async def correr_experimento():
    filas = []
    for modo, (consulta, categoria, esperada) in product(MODOS, CASOS):
        # En Deterministic no hay heuristica de eleccion ad hoc: se usa la
        # misma seleccion automatica para que la comparacion sea honesta.
        resp, traza, seg = await responder(consulta, modo=modo, preferida='Auto')
        usadas = traza.get('tools_usadas') or []
        if esperada is None:
            ok = len(usadas) == 0
        else:
            ok = len(usadas) > 0 and (esperada in usadas or esperada.replace('buscar', 'leer') in usadas)
        tiene_ref = 'http' in resp
        filas.append({
            'modo': modo, 'categoria': categoria, 'consulta': consulta,
            'tools': ','.join(usadas) or '(ninguna)',
            'tool_ok': ok, 'con_referencia': tiene_ref,
            'latencia_s': round(seg, 1),
        })
        print(f"{modo:<12} | {categoria:<10} | tools={'/'.join(usadas) or '-':<30} | ok={ok} | {seg:.1f}s")
    return filas

filas = await correr_experimento()
""")

md(r"""
**Observación (corrida real).** POR LLENAR — tabla modo a modo: aciertos y fallos en la selección de tool, presencia de referencias y latencias de cada consulta.
""")

code(r"""
# Resumen del experimento: tasa de acierto en la tool y latencia por modo.
resumen = (
    pd.DataFrame(filas)
    .groupby('modo')
    .agg(aciertos=('tool_ok', 'sum'),
         casos=('tool_ok', 'count'),
         acierto_pct=('tool_ok', lambda s: round(100 * s.mean(), 1)),
         latencia_media_s=('latencia_s', 'mean'),
         latencia_p90_s=('latencia_s', lambda s: s.quantile(0.9)))
    .round(1)
)
display(resumen)
""")

code(r"""
# Grafico del experimento: acierto (%) y latencia media (s) por modo.
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
resumen['acierto_pct'].plot.barh(ax=ax[0], color='#2a7f62')
ax[0].set_xlim(0, 105)
ax[0].set_title('Aciertos en la selección de tool (%)')
for i, v in enumerate(resumen['acierto_pct']):
    ax[0].text(v + 2, i, f'{v:.0f}%', va='center')

resumen['latencia_media_s'].plot.barh(ax=ax[1], color='#43618f')
ax[1].set_title('Latencia media por turno (s)')
for i, v in enumerate(resumen['latencia_media_s']):
    ax[1].text(v + 0.2, i, f'{v:.1f}s', va='center')
plt.tight_layout()
plt.show()
""")

md(r"""
**Observación (corrida real, lectura del experimento).** POR LLENAR — comparación de los tres modos: cuál acierta más en la selección de tool, cuál es más lento (el agente Autónomo encadena turnos de LLM = más latencia), comportamiento en la categoría `general` (¿invocó tools donde no debía?) y qué modo se recomienda para la demo del video.
""")

# ==========================================================================
# Gradio
# ==========================================================================
md(r"""
## 10. De la consola a la interfaz: el chatbot con Gradio

El mismo agente, montado en una interfaz de chat con Gradio, en la línea del notebook guía. Los controles funcionales son tres — el modo de ejecución, la tool preferida (para forzarla cuando la selección automática fallase) y la opción de mostrar la traza MCP — y todo lo demás (a qué servidor pertenece la pregunta) se infiere del mensaje con la heurística del host. La traza MCP debajo de cada respuesta es la evidencia en pantalla de qué servidor respondió.
""")

code(r"""
# Interfaz Gradio del asistente culinario con herramientas MCP. La funcion es
# async porque Gradio la ejecuta en su propio bucle de eventos y `responder`
# es asincrona (llama al agente con await).
import gradio as gr

async def chat_turno(mensaje, historial, modo, preferida, mostrar_trace):
    respuesta, traza, seg = await responder(mensaje, modo=modo, preferida=preferida,
                                            historial=historial)
    if mostrar_trace:
        respuesta = (respuesta + '\n\n---\nTraza MCP: modo=' + traza['modo']
                     + ' | tools=' + ','.join(traza['tools_usadas'] or ['-'])
                     + ' | ' + f'{seg:.1f} s')
    historial = historial + [
        {'role': 'user', 'content': mensaje},
        {'role': 'assistant', 'content': respuesta},
    ]
    return '', historial

def limpiar():
    return '', []

print('Interfaz lista.')
""")

code(r"""
with gr.Blocks() as gr_blocks:
    gr.Markdown('## Asistente culinario MCP — recetas con fuentes, cálculo exacto y datos de consulta')
    gr.Markdown('Pregunte por recetas (con la URL de la fuente), pida cálculos de cocina (conversiones, escalado, kcal), consulte datos de la base (kcal por 100 g, alergenos, nevera) o pida un producto por su código de barras.')

    modo = gr.Dropdown(choices=['Guided', 'Autonomous', 'Deterministic'], value='Guided',
                       label='Modo de ejecución')
    preferida = gr.Dropdown(choices=['Auto', 'buscar_recetas', 'convertir_volumen', 'escalar_cantidad',
                                     'calcular_kcal', 'consultar_calorias', 'consultar_alergias',
                                     'consultar_inventario', 'info_producto_api'],
                            value='Auto', label='Tool preferida')
    traza_chk = gr.Checkbox(label='Mostrar traza MCP bajo la respuesta', value=False)

    chatbot = gr.Chatbot(label='Historial', height=420)
    msg = gr.Textbox(placeholder='¿Cómo preparo arepas de queso? / ¿Cuántos ml son 3 tazas? / ¿La pasta es apta para alérgicos al gluten? / Código de barras de un producto...',
                     label='¿Qué quieres preguntar?')
    clear = gr.Button('Limpiar')

    msg.submit(chat_turno, [msg, chatbot, modo, preferida, traza_chk], [msg, chatbot])
    clear.click(limpiar, None, [msg, chatbot], queue=False)

gr_blocks.launch(inline=False)
""")

code(r"""
gr_blocks.close()
""")

md(r"""
## 11. Apagado limpio

Se cierran los procesos MCP que el notebook mismo inició (los servidores que ya venían de afuera permanecen), para no dejar sesiones colgadas.
""")

code(r"""
# Apagado de los servidores iniciados por este notebook.
for puerto, proc in mcp_procs.items():
    try:
        proc.terminate()
        print(f'Servidor del puerto {puerto} apagado (pid {proc.pid}).')
    except Exception as exc:
        print(f'No se pudo apagar el servidor del puerto {puerto}: {exc}')
""")

md(r"""
## 12. Conclusiones

**POR LLENAR — redactar tras la corrida, con los resultados reales.** Estructura prevista:

1. **El caso resuelto**: un asistente culinario conversacional donde el conocimiento (19.249 recetas curadas) se sirve por cuatro servidores MCP — documentos con URL citable, cálculo determinístico, datos de consulta en SQLite (kcal por 100 g, alergenos, nevera) y una API viva de productos con caché de respaldo — consumidos por el mismo agente de tres modos.
2. **MCP vs. RAG monolítico (comparación con el Taller 5)**: mismo corpus, mismo LLM y curación idéntica, pero en el Taller 5 la herramienta única era el vector store embebido en el proceso; aquí cada capacidad es un servidor independiente con contrato declarado — el host solo conoce herramientas, nunca los datos.
3. **El valor del protocolo, medida con las cuatro fuentes**: de los 2 servidores de la corrida inicial a los 4 de esta corrida, la línea del agente no cambió; el descubrimiento de tools (ahora 9) siguió siendo automático por `get_tools()`.
4. **Hallazgos del experimento (13 consultas x 3 modos)**: POR LLENAR (acierto y latencia por modo, con la tabla y el gráfico; modo recomendado para la demo).
5. **Análisis cualitativo de los fallos**: POR LLENAR (causas de los turnos fallidos: invocación fallida, redacción que pierde datos u omitió la cifra, sobre-disparo en `general`; qué significa para la capa del protocolo vs. la del LLM).
6. **Trabajo futuro**: POR LLENAR (p. ej., salida verbatim para tools de cálculo puro, recursos MCP además de tools, más consultas por categoría, un segundo generador Ollama, portabilidad a otro dominio, streaming).
""")

md(r"""
## Referencias

- [Model Context Protocol — Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP Architecture overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)
- [MCP Python SDK (FastMCP)](https://py.sdk.modelcontextprotocol.io/)
- [langchain-mcp-adapters](https://pypi.org/project/langchain-mcp-adapters/)
- Dataset: [somosnlp/RecetasDeLaAbuela](https://huggingface.co/datasets/somosnlp/RecetasDeLaAbuela) (Hackathon #Somos600M)
- [Open Food Facts — API v2](https://world.openfoodfacts.org/) (base abierta de alimentos envasados, sin llave)
- [FDA — Major food allergens (big 9)](https://www.fda.gov/food/food-labeling-packaging/major-food-allergens-labeling) (referencia de la tabla orientativa de alergenos)
- [Ollama](https://ollama.com/) · [Gradio](https://www.gradio.app/) · [LangChain](https://www.langchain.com/)
""")

# ==========================================================================
# Construcción del .ipynb
# ==========================================================================
nb = {
    "cells": [
        {
            "cell_type": tipo,
            "metadata": {},
            "source": texto.splitlines(keepends=True),
            **({"outputs": [], "execution_count": None} if tipo == "code" else {}),
        }
        for tipo, texto in CELLS
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

with open(DST, "w", encoding="utf-8", newline="\n") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"{DST}: {len(nb['cells'])} celdas "
      f"({sum(1 for t, _ in CELLS if t == 'code')} código, "
      f"{sum(1 for t, _ in CELLS if t == 'markdown')} markdown)")
print("Marcas POR LLENAR:", sum(
    1 for _, text in CELLS if 'POR LLENAR' in text))