# Guion del video demostrativo — Taller 5

Entregable del taller: video de máximo 2 minutos que muestre (1) la ejecución de la celda que levanta la interfaz de Gradio y (2) un par de interacciones con el bot en las que quede demostrado que el bot responde con referencias a los documentos usados. Este guion está pensado para una corrida previa completa del notebook en Colab (Run All), con el indexado y el LLM ya listos, de modo que durante la grabación solo se ejecuten las celdas rápidas.

## Preparación previa (antes de grabar)

1. Correr el notebook completo (`Run All`) en Colab una vez: con eso quedan el dataset, el `vectorstore` en disco y Ollama instalado. En las corridas siguientes las celdas de carga y indexación reaprovechan los archivos guardados y son rápidas.
2. Con el notebook abierto, lanzar el servicio de Ollama: descomentar la celda de la terminal (`%load_ext colabxterm` / `%xterm`), ejecutarla y en la terminal escribir `ollama serve &` y Enter. Verificar el servicio con alguna celda de prueba que use el chatbot (la de "Prueba 1").
3. Probar la sesión de demostración completa una vez antes de grabar (los ítems del guion) para confirmar que las respuestas citan fuentes y que el tiempo no supera 2 minutos. Si el modelo tarda en responder, aumentar el tamaño de letra del navegador y usar las tres primeras interacciones del guion.
4. Herramienta de grabación: grabador de pantalla (por ejemplo, el de Windows o OBS) a 1080p con el zoom del navegador al 100 por ciento de tamaño o más, para que el texto de las respuestas y las citas se lea con claridad.
5. Decidir dónde queda el video: subirlo al OneDrive institucional (con "cualquiera con el enlace" marcado) o cargarlo como adjunto en Intu.

## Estructura sugerida de la grabación (2 minutos)

| Minuto | Acción | Qué decir (o equivalente con otras palabras) |
| --- | --- | --- |
| 0:00 - 0:15 | Presentar la entrega en pantalla: notebook visible en Colab con el título. | "Esta es la entrega del Taller 5: un chatbot con Retrieval Augmented Generation que responde sobre un corpus propio de recetas de cocina hispanoamericanas. El sistema usa un retriever de embeddings y Llama 3 servido con Ollama, y cada respuesta llega con las citas de las recetas usadas." |
| 0:15 - 0:35 | Ejecutar en vivo la celda de Gradio (sección 13): se ve la salida de `launch` con la URL. | "A continuación se ejecuta la celda que levanta la interfaz con Gradio." (Se ve la salida: "Running on public URL...") |
| 0:35 - 1:00 | Abrir la interfaz en la pestaña y hacer la primera pregunta: "¿Cómo se hace el guacamole?". En tanto responde, leer en voz alta la línea de fuentes que aparece al final de la respuesta (número, título, país y URL). | "...la respuesta construye la receta y cita la fuente: receta con tal título, de México, publicada en esta página." |
| 1:00 - 1:25 | Segunda interacción: preguntar "¿Cuáles son los ingredientes de las arepas?" (u otro plato distinto), y después una pregunta de seguimiento como "¿Y cuánto tarda esa receta?" para demostrar el historial conversacional; señalar que la respuesta sigue trayendo fuentes. | "También funciona la conversación: el bot reformula la pregunta de seguimiento y sigue citando fuentes." |
| 1:25 - 1:50 | Cierre: volver a la pestaña del notebook y mostrar por un momento la respuesta a la pregunta de prueba con las citas, o la celda que imprime las fuentes de LangChain (la comparativa, sección 12). | "Se observa cómo ambas técnicas (a mano y con LangChain) devuelven las referencias de los documentos usados. El detalle completo está en el notebook del repositorio." |

## Qué debe quedar demostrado en pantalla (checklist)

- [ ] La celda de Gradio ejecutándose en vivo, con la URL de la interfaz visible.
- [ ] Al menos dos preguntas respondidas dentro de la interfaz.
- [ ] Al menos una respuesta en la que las citas (título y URL, o país) se leen claramente en pantalla.
- [ ] Una interacción de seguimiento que muestre el historial conversacional (opcional, pero suma).
- [ ] Duración no mayor a 2 minutos.

## Al terminar

- Revisar la grabación: audio audible, texto legible y citas visibles.
- Subir el video a OneDrive institucional o a la plataforma elegida, generar el enlace público y anotarlo en la entrega de Intu, o adjuntarlo directamente.
- Grabar en el mensaje de entrega el enlace del repositorio con la carpeta `Taller_5` y el enlace del video.