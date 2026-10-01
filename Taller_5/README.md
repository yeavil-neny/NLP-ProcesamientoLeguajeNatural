# Carpeta `Taller_5` — Retrieval Augmented Generation (RAG)

Entregables del Taller 5 del curso (sesión 5: RAG con Ollama y LangChain).

## Contenido

| Archivo | Descripción |
| --- | --- |
| `ProfeOriginal--1-ollama-rag.ipynb` | Notebook guía 1 del profesor, sin modificaciones (RAG a mano con Ollama sobre Wikihow en español). |
| `1-ollama-rag-comentado.ipynb` | Copia comentada del notebook guía 1: documentación y comentarios paso a paso, sin cambios en la lógica ni en los outputs de la corrida original. |
| `ProfeOriginal--2-ollama-langchain.ipynb` | Notebook guía 2 del profesor, sin modificaciones (RAG con LangChain + FAISS sobre Wikihow en español). |
| `2-ollama-langchain-comentado.ipynb` | Copia comentada del notebook guía 2: documentación y comentarios paso a paso, sin cambios en la lógica ni en los outputs de la corrida original. |
| `proyecto_rag_chatbot_recetas.ipynb` | Solución del taller: chatbot RAG propio (`RecetasDeLaAbuela`, recetas hispanoamericanas) con EDA, curación, experimentos de recuperación (chunking, encoder, k), comparación con y sin RAG, comparativa con LangChain y técnica preferida argumentada. |
| `guion_video.md` | Guion y checklist del video demostrativo exigido en la entrega (máximo 2 minutos, interfaz de Gradio e interacciones con citas visibles). |

## Convenciones

- Los notebooks `ProfeOriginal--*` son copias byte a byte de los originales del repositorio del profesor, para trazabilidad de la entrega.
- En las copias comentadas, toda la lógica está validada por reconstrucción: al retirar las líneas de comentarios se recupera exactamente el código del original.
- La narrativa de la solución sigue la línea del curso: registro impersonal en tercera persona, sin iconografía.

## Cómo correr la solución

1. Abrir `proyecto_rag_chatbot_recetas.ipynb` en Colab con GPU T4.
2. Ejecutar `Run All` (el indexado se guarda en `data/vectorstore.npy` y solo se computa una vez).
3. Si se corre en Colab, descomentar la celda de la terminal y lanzar `ollama serve &` antes de las celdas del chatbot.
4. En la interfaz de Gradio (última sección) probar las preguntas de demostración del `guion_video.md`.