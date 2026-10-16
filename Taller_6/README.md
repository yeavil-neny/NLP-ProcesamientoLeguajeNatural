# Carpeta `Taller_6` — Mini proyecto MCP con LLM y LangChain

Entregables del Taller 6 del curso (sesión 6: Model Context Protocol con Ollama y LangChain). El índice con los talleres de las demás sesiones está en el `README.md` de la raíz del repositorio.

## Qué aborda este taller

Caso propio: un **asistente culinario conversacional** cuyo agente (llama3.2:3b con LangChain) consume **dos servidores MCP de autoría propia** en lugar de la calculadora y el clima de los ejemplos guía:

- `RecetasDocMCP` (puerto 9090): documentos del corpus curado `RecetasDeLaAbuela` con `buscar_recetas` y `leer_receta`; cada resultado incluye la URL de la página de origen, así las respuestas del bot quedan **con referencias citables** (requisito del video de la entrega).
- `CocinaUtilsMCP` (puerto 9091): cálculo exacto y determinístico con `convertir_volumen`, `escalar_cantidad` y `calcular_kcal`.

## Contenido

| Archivo | Descripción |
| --- | --- |
| `3-chatbot-con-mcp-y-gradio.ipynb` | Notebook guía del profesor, copiado tal cual de la sesión (chatbot con MCP sobre los servidores guía de calculadora y clima, terminado en interfaz Gradio). |
| `3-chatbot-con-mcp-y-gradio-comentado.ipynb` | Copia comentada del notebook guía: documentación y comentarios paso a paso, sin cambios en la lógica ni en los outputs de la corrida original. |
| `mcp_servers/recetas_mcp_server.py` | Servidor MCP propio 1 (`RecetasDocMCP`, puerto 9090), con búsqueda por índice invertido sobre el corpus y salida con referencias. |
| `mcp_servers/cocina_mcp_server.py` | Servidor MCP propio 2 (`CocinaUtilsMCP`, puerto 9091), con conversiones, escalado y kilocalorías aproximadas. |
| `proyecto_mcp_chatbot_recetas.ipynb` | Solución del taller: EDA del corpus, demo de encadenamiento entre servidores, experimento comparativo de los tres modos de ejecución (Guided, Autonomous, Deterministic) y chatbot Gradio con trazas MCP. |
| `guion_video.md` | Guion y checklist del video demostrativo exigido en la entrega (máximo 2 minutos, ejecución en vivo de la celda de Gradio e interacciones con referencias visibles). |

## Cómo correr la solución

1. Abrir `proyecto_mcp_chatbot_recetas.ipynb` en Colab desde GitHub (botón "Open In Colab" del notebook).
2. Ejecutar `Run All`: instala librerías, descarga los servidores desde este repositorio (bootstrap), carga y cura el corpus, escribe `mcp_servers/recetas_corpus.json`, levanta `ollama serve` automáticamente (sin terminal manual) y arranca los dos servidores MCP en los puertos 9090/9091 comprobando su salud por sondeo.
3. La sección del experimento ejecutará 27 turnos del agente (9 preguntas × 3 modos); tarda unos minutos.
4. Terminar en la interfaz de Gradio (sección 10) y probar las consultas de demostración del `guion_video.md`; activar la casilla "Mostrar traza MCP" para evidenciar qué servidor respondió.

## Notas de ejecución

- `recetas_corpus.json` no se versiona: el notebook lo genera en cada corrida desde la curación del dataset `somosnlp/RecetasDeLaAbuela` (mismo corpus y misma curación del Taller 5) y el servidor lo lee al arrancar.
- Los enlaces públicos `*.gradio.live` cambian con cada lanzamiento y mueren con cada desconexión de Colab.