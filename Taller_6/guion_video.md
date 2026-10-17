# Guion del video demostrativo — Taller 6

Entregable del taller: video de máximo 2 minutos que muestre (1) la ejecución de la celda que levanta la interfaz de Gradio y (2) un par de interacciones con el bot en las que quede demostrado que el bot responde con referencias a los documentos usados. Este guion está pensado para una corrida previa completa del notebook en Colab (Run All), con los servidores MCP corriendo y Ollama listo, de modo que durante la grabación solo se ejecuten las celdas rápidas.

## Preparación previa (antes de grabar)

1. Correr el notebook completo (`Run All`) en Colab una vez: con eso quedan instaladas las librerías, descargados los cuatro servidores MCP propios, generado `recetas_corpus.json`, sembrada la base SQLite complementaria, levantado el servicio de Ollama y arrancados los cuatro servidores en los puertos 9090-9093 (recetas, cocina, datos y API).
2. Probar la sesión de demostración completa una vez antes de grabar (los ítems del guion) para confirmar que las respuestas traen la línea de "Fuentes:" con la URL y que el tiempo no supera 2 minutos. Si el modelo tarda, dejar solo las dos interacciones principales.
3. Dejar activada la casilla "Mostrar traza MCP bajo la respuesta" de la interfaz: esa línea (modo, tools usadas, latencia) es la evidencia on-screen de que el agente llamó a los servidores MCP, un plus específico de esta entrega.
4. Herramienta de grabación: grabador de pantalla (por ejemplo, el de Windows u OBS) a 1080p con el zoom del navegador al 100 por ciento o más, para que las URLs de las fuentes se lean con claridad.
5. Decidir dónde queda el video: subirlo al OneDrive institucional (con "cualquiera con el enlace" marcado) o cargarlo como adjunto en Intu.

## Avisos de la corrida real (leer antes de grabar)

La corrida válida de la entrega (con el modelo descargado) mostró cuatro comportamientos que conviene manejar durante la grabación:

1. **El primer turno puede tardar ~90 s** (fue de 89.2 s: carga fría de Ollama más el arranque de la sesión MCP). Calentar el sistema antes de grabar: después del Run All, hacer una consulta en la interfaz y descartarla, de modo que el primer turno grabado ya responda en pocos segundos.
2. **La línea de "Fuentes:" sale con el título y el sitio de origen, pero sin URL** (en la corrida: "Receta de arepa de queso de Recetas Gratis"), o vacía según la respuesta. Si la respuesta no trae la referencia, repetir la pregunta. El requisito del video es "referencias a los documentos usados": la referencia con título y sitio cumple; con URL, mejor.
3. **La cifra de kcal puede faltar en la redacción** (en la corrida, la respuesta del guacamole omitió los kcal calculados por el servidor de cocina). Si ocurre, mostrar la traza MCP donde consta la invocación de `calcular_kcal`, o usar la pregunta del código de barras, cuya cifra (539 kcal de la Nutella) sí quedó en la respuesta con su fuente.
4. **El código de barras no depende del servicio externo**: si OpenFoodFacts no responde, la herramienta contesta desde la caché con su rotulo ("cache local"); la demo puede grabarse en cualquiera de los dos escenarios.

## Estructura sugerida de la grabación (2 minutos)

| Minuto | Acción | Qué decir (o equivalente con otras palabras) |
| --- | --- | --- |
| 0:00 - 0:15 | Presentar la entrega en pantalla: notebook visible en Colab con el título y, si es rápido, la salida de la celda de descubrimiento de herramientas (lista de las 9 tools de los cuatro servidores). | "Esta es la entrega del Taller 6: un asistente culinario con Model Context Protocol. El agente usa Llama 3 local con Ollama y consume cuatro servidores MCP propios: documentos de recetas con referencias, cálculos exactos de cocina, datos de consulta en una base SQLite y una API viva de productos sin llave, con respaldo en caché. Nueve herramientas en total." |
| 0:15 - 0:35 | Ejecutar en vivo la celda de Gradio (sección 10): se ve la salida de `launch` con la URL temporal. | "A continuación se ejecuta la celda que levanta la interfaz con Gradio." (Se ve la salida: "Running on local URL..." o "Running on public URL...") |
| 0:35 - 1:05 | Primera interacción: preguntar "¿Cómo preparo arepas de queso? Cita la receta que uses". Mientras responde, leer en voz alta la línea de Fuentes de la respuesta (título y sitio de origen) y señalar la traza MCP que evidencia la tool `buscar_recetas` del servidor de recetas. | "El bot busca la receta en el servidor MCP de documentos... aquí responde con el procedimiento y cita la fuente de la receta original." |
| 1:05 - 1:35 | Segunda interacción (encadenamiento entre servidores): preguntar "Busca una receta de guacamole y dime cuántas kcal aproximadas aportan 200 gramos de aguacate". Señalar en la traza que se usaron herramientas de los dos servidores; si la redacción no muestra la cifra, señalar en la traza la invocación de `calcular_kcal` o pasar a la tercera interacción. | "Esta consulta cruza los dos servidores: primero la receta con su fuente y luego el cálculo de kilocalorías del servidor de cocina, un resultado exacto que el LLM no puede inventar." |
| 1:35 - 1:45 | (Respaldo recomendado) Tercera interacción: "Consulta el producto con código de barras 3017620422003". La respuesta trae la cifra (539 kcal por 100 g) y la fuente de la API. | "Y si es un producto envasado de marca, el cuarto servidor lo consulta en vivo en OpenFoodFacts, con caché como respaldo; sin llave de API." |
| 1:45 - 2:00 | Cierre: volver al notebook y mostrar por un momento la tabla del experimento de modos (sección 9) con los aciertos y latencias. | "El notebook completo incluye además los tres modos de ejecución del agente comparados en un experimento de 39 turnos, con aciertos y latencias por modo. Todo está en el repositorio." |

## Qué debe quedar demostrado en pantalla (checklist)

- [ ] La celda de Gradio ejecutándose en vivo, con la URL de la interfaz visible.
- [ ] Al menos dos preguntas respondidas dentro de la interfaz.
- [ ] Al menos una respuesta en la que la línea de "Fuentes:" (título y sitio, o URL de la receta) se lea claramente en pantalla.
- [ ] La traza MCP visible en al menos una respuesta, evidenciando la (o las) herramientas invocadas.
- [ ] Si la primera respuesta no trae la línea de "Fuentes:" con URL, se repitió la pregunta hasta lograrlo.
- [ ] Duración no mayor a 2 minutos.

## Al terminar

- Revisar la grabación: audio audible, texto legible y URLs legibles.
- Subir el video a OneDrive institucional o a la plataforma elegida, generar el enlace público y anotarlo en la entrega de Intu, o adjuntarlo directamente.
- Grabar en el mensaje de entrega el enlace del repositorio con la carpeta `Taller_6` y el enlace del video.
- Al terminar la demo, cerrar la interfaz con la celda de apagado (sección 11) para no dejar el servidor de Gradio abierto.