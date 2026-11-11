# Evidencias del proyecto

Este documento recoge las comprobaciones que respaldan el README. Las salidas y
los recuentos son una foto del momento; si cambia el ejemplo o una plantilla,
hay que volver a generarlos.

## 1. Entorno de las pruebas

- Windows 11, terminal de PowerShell.
- Python 3.12.16, gestionado con uv.
- Dependencias principales: Typer, Rich, PyYAML y Jinja2.
- Proyecto separado de `cli-disco` y de `cli-tareas`.

## 2. Validación del ejemplo

```text
$ uv run examenes validar ejemplos
+-----------------------------------------+
| Archivo                        | Estado |
+--------------------------------+--------|
| ejemplos\ejemplo-entornos.yaml | OK     |
+-----------------------------------------+
1 fichero válido
```

El ejemplo es contenido original de repaso sobre pruebas y depuración. No es una
copia de los apuntes del módulo ni de los PDF/PPTX del alumno.

## 3. Listado

```text
$ uv run examenes listar ejemplos
```

La tabla muestra el archivo, el título, el módulo, 2 temas, 3 preguntas, 1
ejercicio y el estado `OK`. En una terminal estrecha, Rich parte las columnas
largas; con `COLUMNS=200` se ve en una sola línea. Es un efecto de presentación,
no un error de datos.

## 4. Renderizado

Comandos ejecutados en `pruebas-examenes`:

```bash
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml \
  --salida pruebas-examenes/material.md
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml \
  --plantilla cuestionario --salida pruebas-examenes/cuestionario.md
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml \
  --plantilla soluciones --salida pruebas-examenes/soluciones.md
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml \
  --formato html --salida pruebas-examenes/material.html
uv run examenes indice ejemplos --salida pruebas-examenes/INDICE.md
```

| Salida | Tamaño | Comprobación |
|---|---:|---|
| `material.md` | 3.4 KB (3.494 B) | Metadatos, objetivos, 2 temas, 3 preguntas y 1 ejercicio |
| `cuestionario.md` | 1.2 KB (1.193 B) | Sin respuestas, explicaciones ni soluciones |
| `soluciones.md` | 1.7 KB (1.715 B) | Respuestas, explicaciones y solución del ejercicio |
| `material.html` | 6.3 KB (6.433 B) | HTML con CSS, contenido escapado y estructura semántica |
| `INDICE.md` | 401 B | Título, módulo, archivo y recuentos |

### Material Markdown

Se comprobó que:

- El título y la descripción aparecen al principio.
- Los objetivos se renderizan como lista.
- Cada tema incluye resumen, puntos clave y recursos.
- Cada pregunta muestra dificultad, tema, enunciado, opciones, respuesta y
  explicación.
- El ejercicio muestra enunciado, pistas y solución.

### Cuestionario

Se comprobó que:

- Incluye enunciados y opciones.
- **No** incluye `Respuesta:`, `Explicación:` ni `Solución:`.
- Sirve para practicar sin ver la solución.

### Soluciones

Se comprobó que:

- Incluye la respuesta de cada pregunta.
- Incluye la explicación cuando existe.
- En los ejercicios muestra el enunciado y la solución.
- Si falta una respuesta o una solución, escribe un aviso en lugar de dejar el
  hueco vacío.

### HTML

Se comprobó que:

- Tiene `charset="utf-8"` y estilos para pantalla e impresión.
- Usa `<article>` para temas, preguntas y ejercicios.
- El contenido multilínea conserva los saltos con `white-space: pre-wrap`.
- Una prueba automática confirma que `<script>alert(1)</script>` se convierte en
  texto escapado y no se ejecuta.

## 5. Protección de salidas

Pruebas realizadas:

| Caso | Resultado |
|---|---|
| Renderizar dos veces en el mismo fichero | La segunda vez falla con «ya existe» |
| Renderizar con `--forzar` | Sobrescribe correctamente |
| `nuevo` sobre un YAML existente | Falla sin `--forzar` |
| `nuevo --forzar` | Sobrescribe correctamente |
| `--sin-soluciones` con `--plantilla soluciones` | Falla con un error claro |
| `--plantilla inventada` | Falla y muestra las plantillas disponibles |
| `--formato html` con `cuestionario` | Falla y muestra los formatos disponibles |

## 6. Suite automática

```text
$ uv run pytest -q
46 passed
```

La suite cubre:

- Carga de un material válido y del ejemplo del repositorio.
- Campos obligatorios, tipos, IDs duplicados, referencias y campos desconocidos.
- Claves YAML duplicadas.
- Fechas YAML convertidas a ISO.
- Render Markdown con y sin soluciones.
- Cuestionario sin respuestas y solucionario.
- Autoescape de HTML.
- Plantillas y formatos disponibles.
- Escritura sin sobrescritura y con `--forzar`.
- Esqueleto de `nuevo`.
- Comandos `version`, `validar`, `listar`, `plantillas`, `renderizar`, `nuevo`
  e `indice`.
- Ignorar `.venv`, carpetas ocultas y `node_modules` al recorrer una carpeta.

## 7. Material original respetado

- No se modificó ningún PDF, PPTX, DOCX ni apunte de
  `E:\01-ESTUDIOS\FP-INFORMATICA\SEMIPRESENCIAL`.
- No se copió contenido de esos materiales al repositorio.
- El ejemplo `ejemplos/ejemplo-entornos.yaml` es original.
- `cli-disco` y `cli-tareas` no se tocaron desde este proyecto.
- No se crearon ni modificaron ficheros `.env`.

## 8. Cómo reproducir las comprobaciones

```bash
uv sync
uv run pytest -q
uv run examenes --help
uv run examenes validar ejemplos
uv run examenes listar ejemplos
uv run examenes plantillas
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml \
  --salida pruebas-examenes/material.md --forzar
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml \
  --formato html --salida pruebas-examenes/material.html --forzar
uv run examenes indice ejemplos --salida pruebas-examenes/INDICE.md --forzar
```

`pruebas-examenes/` está ignorada por Git. Para una prueba limpia, usa una
carpeta temporal fuera del repositorio.
