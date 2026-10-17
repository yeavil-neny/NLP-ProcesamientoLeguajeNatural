# Contexto de trabajo del equipo — Grupo Delta

Sincronizado el 17-oct-2026. Documento de referencia compartido: cualquier integrante del grupo puede retomar cualquier taller desde este archivo sin perder el hilo de las decisiones, corridas y convenciones. Se actualiza al final de cada sesión de trabajo material.

---

## 1. Estado de los entregables del curso (a la fecha)

| Taller | Tema | Estado |
| --- | --- | --- |
| 1, 2 | Clasificación de reseñas (LSTM, Transformer) | Entregados; históricos: LSTM 0.5168, Transformer 0.4896 |
| 3 | BERT (BETO) clasificación, reseñas Amazon en español | Entregado y calificado: 85.71/100; revisión solicitada al profesor por la casilla Innovación (correo enviado 17-oct-2026; queda a la espera de respuesta) |
| 4 | GPT-2 generación de texto, reseñas e-commerce | Entregado completo (final `67fd6e4`); pendiente de conocer su calificación |
| 5 | RAG chatbot de recetas (e5-large + Llama 3) | Entregado y sincronizado; corrida y observaciones en GitHub |
| **6** | **MCP + Gradio (asistente culinario, 4 servidores)** | **Corrida final limpia y sincronizada con todos los resultados; pendiente SOLO grabar el video** |

El remoto (GitHub, `main`) es la fuente de verdad de todas las entregas.

## 2. Taller 6 — arquitectura y decisiones (la versión final)

**Caso**: asistente culinario conversacional (mismo problema de negocio del Taller 5) donde el conocimiento se sirve por **4 servidores MCP propios** y el agente mantiene **3 estrategias de ejecución**.

### Los 4 servidores (`Taller_6/mcp_servers/`, FastMCP, streamable-HTTP)

| # | Servidor | Puerto | Tools | Fuente de datos |
| --- | --- | --- | --- | --- |
| 1 | `RecetasDocMCP` | 9090 | `buscar_recetas`, `leer_receta` | `recetas_corpus.json` (19.249 recetas curadas; índice invertido propio; cada hit con URL de origen) |
| 2 | `CocinaUtilsMCP` | 9091 | `convertir_volumen`, `escalar_cantidad`, `calcular_kcal` | tablas en código (1 taza = 240 ml; kcal tipo USDA) |
| 3 | `DatosCocinaMCP` | 9092 | `consultar_calorias`, `consultar_alergias`, `consultar_inventario` | SQLite `cocina_datos.db` (58 kcal, 40 alergias FDA big-9, 6 de la nevera) — **solo consulta** |
| 4 | `AlimentosAPIMCP` | 9093 | `info_producto_api` | API viva OpenFoodFacts (sin llave) con caché de respaldo (`api_cache.json`) |

**Decisiones del equipo que quedaron asiento:**
- **SQLite de solo consulta**: ninguna herramienta escribe en la base; el sembrador (`seed_datos.py`) reinicia la base en cada corrida (reproducibilidad garantizada). Se evaluó un inventario con escritura (agregar/quitar) y el equipo decidió no incluirlo (17-oct-2026).
- **API viva con respaldo**: timeout + reintento + caché local con instantánea real del 17-oct-2026 (Nutella 539 kcal/100 g, Coca-Cola 42.4); si OpenFoodFacts no responde, la tool contesta desde el caché rotulado y la corrida continúa (la búsqueda del servicio estuvo caída con HTTP 503 esa tarde y el respaldo demostró funcionar).
- **Garantía mecánica de fuentes (componer_fuentes)**: la línea "Fuentes:" la garantiza el HOST tras cada redacción, no el LLM: URLs reales de las salidas de las tools; si no hay URL, se cita la herramienta usada y su servidor; si el turno no usó herramientas, se declara "respuesta sin base documental". Motivación: en las corridas, el modelo de 3 B olvidaba copiar la URL, la dejaba vacía o mal ubicada.
- **Generador fijo** (`llama3.2:3b`, temperature=0): la comparación es entre arquitecturas de servicio (T5 RAG vs T6 MCP); cambiar el LLM contaminaría el diseño experimental.

### Estrategias de ejecución (los 3 modos, intactos desde el notebook guía)

- **Autonomous**: el agente decide libremente (la heurística del host no aplica).
- **Guided** (por defecto): la heurística del host sugiere la tool como instrucción; hay fallback si el agente no ejecuta nada.
- **Deterministic**: el host ejecuta directamente la tool inferida por la heurística y el LLM solo redacta.

## 3. Historia de las corridas del Taller 6 (y sus hallazgos)

| Corrida (commit) | Resultado |
| --- | --- |
| `b08bc19` (crispesdeep, 2 servidores) | Corrida válida: 27 turnos, 23/27 aciertos; Deterministic 100%/2.6 s; citación débil (Fuentes vacías/473.2) |
| `8b4215b` (Yenny, 4 servidores) | **Corrida invalidada**: en runtime fresco, `ollama pull` corrió antes de `ollama serve`; el modelo no se descargó y 19 turnos con LLM devolvieron 404. La parte MCP funcionó completa. **Fix en `5228b50`**: orden instala → sirve → pull condicionado a `ollama list` |
| `292d725` (Yenny, válida) | 39 turnos, 37/39 (94.9%); Deterministic 100%/2.2 s; aún con 5 demos y batería por crear |
| `ac3077f` (Fredy) | 4 servidores + batería 8.1 (90 turnos compacta) + garantía de Fuentes; 0 errores; sync en `c6982cd` |
| **`586a5c1` (Yenny, FINAL)** | **Sección 8 fusionada (validación única de 90 turnos con salida completa y Fuentes garantizada por turno, sin consultas repetidas) + experimento con casos nuevos (sin duplicar la batería). 0 errores. Sincronizada en el commit del sync final (ver `git log`)** |

### Cifras oficiales finales de la corrida `586a5c1` (sección 8 fusionada)

- **Batería de validación (sección 8 única, 90 turnos con salida completa y Fuentes garantizada por turno)**: 82/90 aciertos (91.1%). Categoría `tool` (81): **Deterministic 27/27 (100%)**, Guided 26/27, Autonomous 25/27 — mismo patrón estable de la corrida anterior; los fallos de los modos con agente: la confusión `calcular_kcal` vs `consultar_calorias` y un caso donde Autonomous no invocó nada.
- **Categoría `todas_las_tools` (6 turnos)**: la mezcla 1 en Guided sigue siendo el hallazgo estrella: **buscar_recetas + consultar_inventario + calcular_kcal encadenados en 3 servidores en un solo turno**. En la mezcla 2 (5 tools), Guided alcanzó 2/5; Autonomous no completó cadenas; Deterministic ejecuta una sola tool (conducta registrada, no fallo).
- **Categoría `sin_datos` (3 turnos)**: solo Deterministic se abstuvo; Guided y Autonomous llamaron `buscar_recetas`.
- **La garantía de fuentes salió en el 100% de los turnos**: URL real en los 27 de documentos, herramienta + servidor en cálculo/datos/API y "sin base documental" en el turno sin herramientas. La anomalía de respuestas casi vacías (2 de 5 en la corrida previa) NO se reprodujo: es intermitente.
- **Experimento de modos (39 turnos, casos nuevos sin duplicar la batería)**: 35/39 (89.7%); Guided 92.3% (2.4 s, p90 4.6), **Deterministic 92.3% (2.1 s, p90 5.1) — recomendado para la demo**, Autonomous 84.6% (4.1 s, p90 7.7). Dos hallazgos de diseño nuevos: (a) "¿Qué lleva el lomo saltado peruano?" no activa señales del host → Deterministic la rechaza honesta (Guided la resolvió con criterio libre del agente): la calidad de Deterministic es condición de las señales; (b) "120 gramos de atún" en Autonomous: confusión de tools parecidas. El saludo persiste sobre-disparando en Guided/Autonomous.
- **Conclusión "dónde es más fuerte el MCP" (en las conclusiones del notebook)**: MCP domina en actos (cálculo exacto, SQL, API, extensibilidad de 2 a 4 servidores medida, citación garantizada por el host) y el RAG del Taller 5 sigue dominando en recuperación semántica (hit@1 0.60/MRR 0.625) y latencia de recuperación (30.3 ms); las comparaciones de latencia son honestas RELATIVAS entre modos (la sesión fría pagó hasta ~10 s en el primer turno).

## 4. Taller 3 — situación de la calificación (contexto para coordinar la respuesta del profesor)

- Nota: 85.71/100; casilla Innovación en "Estándar (1.0)" con descriptores de "Muy bien" que el entregable cumple (evidencia: sección "Análisis en Profundidad del Modelo Óptimo", experimento E4 "más allá de la guía", comparación de los 3 talleres, EDA propio).
- Los 3 comentarios del profesor ("aporte de datos adicional", "múltiples modelos preentrenados", "falta análisis cualitativo de errores") fueron controvertidos con las citas del enunciado/rúbrica que el equipo compartió; el tercero se desmiente con la celda "Análisis cualitativo: leamos los errores del modelo".
- El correo de revisión (con esas argumentaciones) fue enviado por el equipo el 17-oct-2026. Pendiente: respuesta del profesor. Al aplicar esta lección, TODOS los aportes propios del Taller 6 quedaron rotulados como tales (sección 1.2 del notebook) para que no vuelva a pasar que un entregable contenga lo que se pide y califique sin ello.

## 5. Convenciones del equipo (aplicar SIEMPRE)

1. **El remoto es la fuente de verdad**: no editar notebooks compartidos sin avisar; antes de editar, `git fetch` y revisar si `main` avanzó.
2. **Commits**: desde la cuenta del grupo (`Yeavil-neny`), **sin líneas de co-autoría** (decisión explícita del 17-oct-2026), con mensajes descriptivos en español.
3. **Estilo de la narrativa**: registro impersonal/tercera persona (sin "veamos", "puedes", "nuestro"); los prompts y las respuestas del bot (que la app dirige al usuario) se citan tal cual; **sin emojis decorativos** (las estrellas ★ de calificaciones se conservan).
4. **No editar**: `Taller_2/proyecto_transformers_clasificacion.ipynb` (instrucción explícita del 20-sep-2026).
5. **Sincronización post-corrida**: editar SOLO celdas markdown; nunca tocar salidas ni execution_count; verificar bit a bit contra el commit de la corrida (scripts en `Taller_6/_build/`).

## 6. Cómo trabajar los notebooks del taller 6 (flujo reproducible)

1. **Generar/actualizar el notebook**: `python -I -X utf8 _build/build_solucion.py` (desde `Taller_6/`; la ruta del generador está anclada a la del script). El notebook se genera sin corrida y con marcas `POR LLENAR`.
2. **Run All en Colab** (abierto desde el badge del repo, o subir el archivo directo): el notebook es auto-bootstrapeable (descarga servidores/sembrador/caché desde `raw` de este repo; Ollama: instala si falta → sirve → descarga el modelo solo si no está).
3. **Commit del corrido** (Colab) y luego **sincronizar las marcas** con un script de solo-markdown (`fill_observaciones_v*.py` como patrón: reemplazos exactos verificados, verificación de salidas/execution_count intactos, formato indent=2 + finales de línea del archivo original).
4. **Pruebas locales de servidores** sin dataset de HF: `python -I -X utf8 _build/test_servidores_nuevos.py` (sembrado + 2 servidores nuevos) y `test_servidores.py` (los originales, con mini corpus sintético).

## 7. Lecciones técnicas acumuladas (no repetirlas)

- `ollama pull` requiere el servicio `ollama serve` atendiendo: en runtime fresco el orden instalado-antes-de-servir deja el modelo sin descargar (error 404 en cada turno).
- Las celdas generadas con docstrings `"""` deben envolverse en `r'''...'''` (una docstring `"""` dentro de un bloque `r"""` corta el string a la mitad) — ya aplicado en `build_solucion.py`.
- Al regenerar notebooks: anclar las rutas de los scripts a `Path(__file__)` (una ruta relativa mandó la generación a la raíz del repo) y verificar SIEMPRE que el commit tocó el archivo esperado.
- El editor web de GitHub anula los `execution_count` de los .ipynb (lección del Taller 5).
- Las regex de limpieza de emojis deben proteger caracteres de contenido (la estrella ★ terminó en las cifras de un entregable; reparado reconstruyendo desde el commit base).
- OpenFoodFacts: sin llave, la búsqueda por nombre es la parte inestable (503 esa tarde); el endpoint por código de barras es el estable.
- Corridas en Colab con sesiones reutilizadas: "ya estaba atendido; se reutiliza" es normal; las latencias se comparan RELATIVAS entre modos (la temperatura de sesión cambia la escala absoluta).

## 8. Pendientes abiertos (al 17-oct-2026)

- [ ] **Taller 6**: grabar y entregar el video (2 min) con `Taller_6/guion_video.md` (ya ajustado con los avisos de la corrida final: calentar, repetir la pregunta si la redacción sale vacía, la Fuentes garantizada, y la mezcla validada como segunda interacción).
- [ ] **Taller 3**: seguimiento de la respuesta del profesor a la solicitud de revisión de Innovación.
- [ ] **Taller 4**: al llegar su calificación, aplicar el mismo protocolo (comparar con la rúbrica, pedir revisión solo con evidencia verificable).