# ADR-0010 — Se adopta MarkItDown como comando, no como servidor MCP

| Campo | Valor |
|---|---|
| Fecha | 2026-09-15 |
| Estado | ACEPTADA |
| Fase | 5 — Herramientas (ampliación) |

## Decisión

Se adopta **`markitdown[pdf]==0.1.7` como herramienta de línea de comandos** para convertir documentos a markdown antes de que el modelo los lea. **No se instala `markitdown-mcp`.**

## Contexto

El Director preguntó si convenía usar el servidor MCP de MarkItDown para procesar archivos sin desperdiciar tokens. La intuición era correcta; la forma, no.

### Lo que se midió

Sobre un PDF real de 38 páginas y 7,3 MB:

| Camino | Costo |
|---|---|
| **MarkItDown → markdown → leer** | 38.043 caracteres ≈ **11.528 tokens**, en 2,9 s |
| **Lectura nativa del PDF** | ≈ **53.000 a 80.000 tokens** (texto + 38 páginas como imagen) |
| **Ahorro** | **5× a 7×** — entre 0,52 % y 0,85 % de la ventana semanal, por documento |

La estructura se conserva: 845 líneas con encabezados y tablas. El conteo de caracteres y páginas es exacto; la conversión a tokens y el costo por página como imagen son estimaciones declaradas. **No se refinó más porque la conclusión no cambia en ningún punto del rango.**

### Lo que se creía y era falso

La hipótesis inicial era que la capacidad ya estaba instalada, porque el Director tiene las skills `pdf`, `docx`, `xlsx` y `pptx` con 50 scripts de Python entre las cuatro.

**Falso.** Los ocho scripts de la skill `pdf` son todos de **formularios e imágenes** — rellenar campos, verificar cajas delimitadoras, convertir páginas a imagen. **Ninguno extrae texto.** Y ninguna de sus librerías (`pypdf`, `pdfplumber`, `fitz`, `pypdfium2`) estaba instalada.

Verificar antes de decidir evitó descartar algo útil por una suposición cómoda.

## Opciones consideradas

1. **`markitdown-mcp`** — existe, pero en versión **alfa** (`0.0.1a7`). Y un servidor MCP carga las descripciones de sus herramientas en **cada sesión, para siempre**.
2. **`markitdown[all]`** — 51 dependencias, incluye OCR y audio. Arrastra `onnxruntime` y `pandas` completos.
3. **`markitdown[pdf]`** — lo mínimo que resuelve el caso medido.
4. **No instalar nada** — deja el costo de leer documentos donde está.

## Enfoque elegido

Opción 3.

## Por qué

**Contra el MCP, la misma lógica del ADR-0007:** un servidor MCP cobra contexto fijo en cada sesión para exponer algo que un comando hace con costo de contexto **cero**. Acá el comando gana sin discusión. Sumado a que la versión del servidor es alfa y el checklist de admisión exige versión pineada y proyecto mantenido.

**Contra `[all]`:** no hay caso de uso para OCR ni audio. Se instala cuando aparezca, no antes.

**A favor de instalar algo:** el ahorro está medido, es grande y recurrente. El Director tiene PDFs reales —documentos legales, resúmenes, material académico— y leerlos nativo cuesta casi un 1 % de la semana cada uno.

## Trade-offs

- **Se gana:** 5× a 7× menos tokens por documento, en 3 segundos, conservando estructura. Cero contexto fijo.
- **Se pierde:** ~20 dependencias nuevas en el entorno Python, entre ellas `numpy` y `onnxruntime` (llegan con `magika`, el detector de tipos de Microsoft). No es un paquete chico.
- **Se acepta:** MarkItDown extrae la **capa de texto**. Un PDF escaneado sin texto no se convierte — para eso haría falta OCR, que es el extra pesado que no se instaló.

## Consecuencias

1. **Regla operativa:** antes de leer un PDF, `.docx`, `.xlsx` o `.pptx` extenso, convertirlo con MarkItDown y leer el markdown. Para documentos de una o dos páginas no vale la pena el rodeo.
2. Se agrega `config/requirements.txt` con **todo pineado**, para que el entorno sea reproducible.
3. `tests/medir-extraccion.py` queda como herramienta: mide el ahorro de cualquier documento sin mostrar su contenido — importante, porque los documentos del Director son datos `PERSONAL`.
4. **Si aparece un PDF escaneado**, ahí se evalúa el extra de OCR. No antes.

### Señal de reconsideración

Se revisa si MarkItDown deja de mantenerse, si aparece un formato que no cubra, o si `markitdown-mcp` sale de alfa **y** ofrece algo que el comando no pueda.
