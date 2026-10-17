# Guion del video demostrativo — Taller 6

Entregable del taller: video de máximo 2 minutos que muestre (1) la ejecución de la celda que levanta la interfaz de Gradio y (2) un par de interacciones con el bot en las que quede demostrado que el bot responde con referencias a los documentos usados. Este guion está pensado para una corrida previa completa del notebook en Colab (Run All), con los servidores MCP corriendo y Ollama listo, de modo que durante la grabación solo se ejecuten las celdas rápidas.

## Preparación previa (antes de grabar)

1. Correr el notebook completo (`Run All`) en Colab una vez: con eso quedan instaladas las librerías, descargados los dos servidores MCP propios, generado `recetas_corpus.json`, levantado el servicio de Ollama y arrancados los servidores en los puertos 9090 (recetas) y 9091 (cocina).
2. Probar la sesión de demostración completa una vez antes de grabar (los ítems del guion) para confirmar que las respuestas traen la línea de "Fuentes:" con la URL y que el tiempo no supera 2 minutos. Si el modelo tarda, dejar solo las dos interacciones principales.
3. Dejar activada la casilla "Mostrar traza MCP bajo la respuesta" de la interfaz: esa línea (modo, tools usadas, latencia) es la evidencia on-screen de que el agente llamó a los servidores MCP, un plus específico de esta entrega.
4. Herramienta de grabación: grabador de pantalla (por ejemplo, el de Windows u OBS) a 1080p con el zoom del navegador al 100 por ciento o más, para que las URLs de las fuentes se lean con claridad.
5. Decidir dónde queda el video: subirlo al OneDrive institucional (con "cualquiera con el enlace" marcado) o cargarlo como adjunto en Intu.

## Avisos de la corrida real (leer antes de grabar)

La corrida completa del notebook en Colab mostró tres comportamientos que conviene manejar durante la grabación:

1. **El primer turno puede tardar ~90 s** (fue de 88.4 s: carga fría de Ollama más el arranque de la sesión MCP). Calentar el sistema antes de grabar: después del Run All, hacer una consulta en la interfaz y descartarla, de modo que el primer turno grabado ya responda en pocos segundos.
2. **La línea de "Fuentes:" a veces sale vacía** con este modelo de 3 B: en las tres demostraciones de la corrida la redacción no incluyó la URL. Si la respuesta grabada no trae la URL, repetir la pregunta (o reformularla levemente) hasta que la citación aparezca: la referencia legible es el requisito central del video.
3. **Verificar la cifra de kcal en pantalla**: en la corrida el encadenamiento entre servidores sí se produjo (traza con `buscar_recetas` + `calcular_kcal`), pero la redacción final omitió la cifra. Si ocurre, repetir la interacción o elegir una pregunta de conversión (modo más robusto: el resultado exacto llega en la salida de la tool).

## Estructura sugerida de la grabación (2 minutos)

| Minuto | Acción | Qué decir (o equivalente con otras palabras) |
| --- | --- | --- |
| 0:00 - 0:15 | Presentar la entrega en pantalla: notebook visible en Colab con el título y, si es rápido, la salida de la celda de descubrimiento de herramientas (lista de las 5 tools de los dos servidores). | "Esta es la entrega del Taller 6: un asistente culinario con Model Context Protocol. El agente usa Llama 3 local con Ollama y consume dos servidores MCP propios: uno sirve documentos de recetas con referencias y otro hace cálculos exactos de cocina." |
| 0:15 - 0:35 | Ejecutar en vivo la celda de Gradio (sección 10): se ve la salida de `launch` con la URL temporal. | "A continuación se ejecuta la celda que levanta la interfaz con Gradio." (Se ve la salida: "Running on local URL..." o "Running on public URL...") |
| 0:35 - 1:05 | Primera interacción: preguntar "¿Cómo preparo arepas de queso? Cita la receta que uses". Mientras responde, leer en voz alta la línea de Fuentes de la respuesta y señalar la traza MCP que evidencia la tool `buscar_recetas` del servidor de recetas. | "El bot buscará la receta en el servidor MCP de documentos... aquí responde con el procedimiento y cita la fuente: título, país y la URL de la página gastronómica original." |
| 1:05 - 1:35 | Segunda interacción (encadenamiento entre servidores): preguntar "Busca una receta de guacamole y dime cuántas kcal aproximadas aportan 200 gramos de aguacate". Señalar en la traza que se usaron herramientas de los dos servidores, y que la cifra de kcal proviene del servidor de cálculo, no del modelo. | "Esta consulta cruza los dos servidores: primero la receta con su fuente y luego el cálculo de kilocalorías del servidor de cocina, un resultado exacto que el LLM no puede inventar." |
| 1:35 - 1:55 | Cierre: volver al notebook y mostrar por un momento la tabla del experimento de modos (sección 9) con los aciertos y latencias. | "El notebook completo incluye además los tres modos de ejecución del agente comparados experimentalmente, con aciertos y latencias. Todo está en el repositorio." |

## Qué debe quedar demostrado en pantalla (checklist)

- [ ] La celda de Gradio ejecutándose en vivo, con la URL de la interfaz visible.
- [ ] Al menos dos preguntas respondidas dentro de la interfaz.
- [ ] Al menos una respuesta en la que la línea de "Fuentes:" (título y URL de la receta) se lea claramente en pantalla.
- [ ] La traza MCP visible en al menos una respuesta, evidenciando la (o las) herramientas invocadas.
- [ ] Si la primera respuesta no trae la línea de "Fuentes:" con URL, se repitió la pregunta hasta lograrlo.
- [ ] Duración no mayor a 2 minutos.

## Al terminar

- Revisar la grabación: audio audible, texto legible y URLs legibles.
- Subir el video a OneDrive institucional o a la plataforma elegida, generar el enlace público y anotarlo en la entrega de Intu, o adjuntarlo directamente.
- Grabar en el mensaje de entrega el enlace del repositorio con la carpeta `Taller_6` y el enlace del video.
- Al terminar la demo, cerrar la interfaz con la celda de apagado (sección 11) para no dejar el servidor de Gradio abierto.