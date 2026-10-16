# NLP — Procesamiento del Lenguaje Natural

Entregables del curso de NLP (Deep Learning aplicado): las carpetas `Taller_1` a `Taller_6`, una por sesión. La rúbrica de todas sigue el mismo espíritu: notebook completo, reproducible, con narrativa impersonal, sin iconografía y con aportaciones propias más allá del ejemplo guía.

| Carpeta | Sesión / tema | Solución del taller |
| --- | --- | --- |
| `Taller_1` | Fundamentos de NLP con redes recurrentes | `proyecto_fundamentos_NLP_LSTM.ipynb` |
| `Taller_2` | Transformers desde cero y clasificación | `proyecto_transformers_clasificacion.ipynb` |
| `Taller_3` | Clasificación con transformers pre-entrenados (Hugging Face / BERT) | `proyecto_bert_clasificacion.ipynb` |
| `Taller_4` | Generación de texto con GPT | `proyecto_gpt_resenas_ecommerce.ipynb` (reseñas de e-commerce) |
| `Taller_5` | Retrieval Augmented Generation (RAG con Ollama y LangChain) | `proyecto_rag_chatbot_recetas.ipynb` (corpus `RecetasDeLaAbuela`) |
| `Taller_6` | Model Context Protocol (MCP con Ollama, LangChain y Gradio) | `proyecto_mcp_chatbot_recetas.ipynb` (recetas vía servidores MCP propios) |

## Convenciones comunes

- En cada carpeta donde hay notebooks guía del profesor, el original se conserva byte a byte (prefijo `ProfeOriginal--` o el nombre original) y la copia comentada es una versión aparte (`*-comentado.ipynb`): la lógica del código guía no cambia, solo se añaden comentarios y celdas de explicación, validándose por reconstrucción.
- El video demostrativo de cada entrega (máximo 2 minutos) tiene su guion y checklist en `guion_video.md` dentro de la carpeta correspondiente.
- El registro de la narrativa es impersonal en tercera persona y sin emojis; las estrellas de calificaciones se conservan cuando el profesor las usa.

El detalle de cada carpeta (contenido, cómo correr la solución y lecciones de ejecución) está en el `README.md` propio de cada una.