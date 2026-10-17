# Guion del video demostrativo — Taller 6

Entregable del taller: video de máximo 2 minutos que muestre (1) la ejecución de la celda que levanta la interfaz de Gradio y (2) un par de interacciones con el bot en las que quede demostrado que el bot responde con referencias a los documentos usados. Este guion está pensado para una corrida previa completa del notebook en Colab (Run All), con los servidores MCP corriendo y Ollama listo, de modo que durante la grabación solo se ejecuten las celdas rápidas.

## Preparación previa (antes de grabar)

1. Correr el notebook completo (`Run All`) en Colab una vez: con eso quedan instaladas las librerías, descargados los cuatro servidores MCP propios, generado `recetas_corpus.json`, sembrada la base SQLite complementaria, levantado el servicio de Ollama y arrancados los cuatro servidores en los puertos 9090-9093 (recetas, cocina, datos y API).
2. Probar la sesión de demostración completa una vez antes de grabar (los ítems del guion) para confirmar que las respuestas traen la línea de "Fuentes:" con la URL y que el tiempo no supera 2 minutos. Si el modelo tarda, dejar solo las dos interacciones principales.
3. Dejar activada la casilla "Mostrar traza MCP bajo la respuesta" de la interfaz: esa línea (modo, tools usadas, latencia) es la evidencia on-screen de que el agente llamó a los servidores MCP, un plus específico de esta entrega.
4. Herramienta de grabación: grabador de pantalla (por ejemplo, el de Windows u OBS) a 1080p con el zoom del navegador al 100 por ciento o más, para que las URLs de las fuentes se lean con claridad.
5. Decidir dónde queda el video: subirlo al OneDrive institucional (con "cualquiera con el enlace" marcado) o cargarlo como adjunto en Intu.

## Avisos de la corrida final (leer antes de grabar)

La corrida final (4 servidores, con la garantía mecánica de Fuentes) mostró estos comportamientos:

1. **El primer turno puede tardar ~90 s** (carga fría de Ollama). Calentar antes de grabar: después del Run All, hacer una consulta en la interfaz y descartarla.
2. **La línea de "Fuentes: " ahora sale siempre** (es garantía del host, no del modelo): con la URL real del documento cuando la tool la trae (demo de arepas), con la herramienta y su servidor cuando no (cálculos, SQLite, API), o con el aviso de "respuesta sin base documental" si el turno no usó herramientas. Grabarla en pantalla: es el requisito de referencias de la demo.
3. **Las respuestas del redactor pueden quedar casi vacías** (ocurrió en 2 de 5 demostraciones de la corrida): el texto no trae contenido aunque la tool respondió. Si pasa: repetir la pregunta, o forzar la tool en el dropdown, o usar el modo Deterministic para esa consulta. La traza MCP y la línea de Fuentes quedan igualmente evidenciadas.
4. **El código de barras no depende del servicio externo** (respuesta en vivo o desde caché, con su rotulo): la demo puede grabarse en cualquiera de los dos escenarios.

## Estructura sugerida de la grabación (2 minutos)

| Minuto | Acción | Qué decir (o equivalente con otras palabras) |
| --- | --- | --- |
| 0:00 - 0:15 | Presentar la entrega en pantalla: notebook visible en Colab con el título y, si es rápido, la salida de la celda de descubrimiento de herramientas (lista de las 9 tools de los cuatro servidores). | "Esta es la entrega del Taller 6: un asistente culinario con Model Context Protocol. El agente usa Llama 3 local con Ollama y consume cuatro servidores MCP propios: documentos de recetas con referencias, cálculos exactos de cocina, datos de consulta en una base SQLite y una API viva de productos sin llave, con respaldo en caché. Nueve herramientas en total." |
| 0:15 - 0:35 | Ejecutar en vivo la celda de Gradio (sección 10): se ve la salida de `launch` con la URL temporal. | "A continuación se ejecuta la celda que levanta la interfaz con Gradio." (Se ve la salida: "Running on local URL..." o "Running on public URL...") |
| 0:35 - 1:05 | Primera interacción: preguntar "¿Cómo preparo arepas de queso? Cita la receta que uses". Mientras responde, leer en voz alta la línea de Fuentes con la URL real de origen y señalar la traza MCP que evidencia la tool `buscar_recetas` del servidor de recetas. | "El bot busca la receta en el servidor MCP de documentos... aquí responde con el procedimiento y la garantía de fuentes del host deja en pantalla la URL de la página gastronómica original." |
| 1:05 - 1:35 | Segunda interacción (mezcla validada en la corrida, categoría `todas_las_tools`, modo Guided): preguntar "Busca una receta sencilla de ensalada, revisa qué tengo en la nevera y dime cuántas kcal tienen 200 gramos de aguacate". Señalar en la traza las tres tools de los tres servidores encadenadas en un solo turno (verificado en la corrida: 0.8 s). | "Esta consulta cruza tres servidores en un mismo turno: documentos de recetas, la base de datos de la nevera en SQLite y el cálculo de kilocalorías — el encadenamiento clave del caso MCP." |
| 1:35 - 1:45 | (Respaldo recomendado) Tercera interacción: "Consulta el producto con código de barras 3017620422003" en modo Deterministic. La respuesta trae la cifra (539 kcal por 100 g) y la línea de Fuentes cita la herramienta de la API. | "Y para un producto envasado de marca, el cuarto servidor lo consulta en vivo en OpenFoodFacts, con caché como respaldo; sin llave de API." |
| 1:45 - 2:00 | Cierre: volver al notebook y mostrar por un momento la tabla del experimento de modos (sección 9) con los aciertos y latencias. | "El notebook completo incluye además los tres modos de ejecución del agente comparados en un experimento de 39 turnos, con aciertos y latencias por modo. Todo está en el repositorio." |

## Qué debe quedar demostrado en pantalla (checklist)

- [ ] La celda de Gradio ejecutándose en vivo, con la URL de la interfaz visible.
- [ ] Al menos dos preguntas respondidas dentro de la interfaz.
- [ ] Al menos una respuesta en la que la línea de "Fuentes:" con la URL real de la receta se lea claramente en pantalla (en la corrida final salió con URL: demo de arepas).
- [ ] La traza MCP visible en al menos una respuesta, evidenciando la (o las) herramientas invocadas.
- [ ] Si la primera respuesta no trae la línea de "Fuentes:" con URL, se repitió la pregunta hasta lograrlo.
- [ ] Duración no mayor a 2 minutos.

## Al terminar

- Revisar la grabación: audio audible, texto legible y URLs legibles.
- Subir el video a OneDrive institucional o a la plataforma elegida, generar el enlace público y anotarlo en la entrega de Intu, o adjuntarlo directamente.
- Grabar en el mensaje de entrega el enlace del repositorio con la carpeta `Taller_6` y el enlace del video.
- Al terminar la demo, cerrar la interfaz con la celda de apagado (sección 11) para no dejar el servidor de Gradio abierto.