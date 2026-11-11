# examenes · material de estudio desde YAML y plantillas

> CLI que convierte contenido estructurado en material de estudio reproducible:
> temario, preguntas, ejercicios, cuestionarios y soluciones en Markdown o HTML.

Proyecto de 1º DAM (semipresencial). Este README es el **CDI** del proyecto:
reto, objetivos, alcance, actividades, evidencias, criterios de evaluación y
conclusiones.

---

## Índice

1. [El reto](#1-el-reto)
2. [Objetivos](#2-objetivos)
3. [Alcance](#3-alcance)
4. [Stack y arquitectura](#4-stack-y-arquitectura)
5. [Instalación y uso rápido](#5-instalación-y-uso-rápido)
6. [Esquema YAML](#6-esquema-yaml)
7. [Comandos](#7-comandos)
8. [Plantillas y formatos](#8-plantillas-y-formatos)
9. [Flujo de trabajo](#9-flujo-de-trabajo)
10. [Actividades](#10-actividades)
11. [Evidencias](#11-evidencias)
12. [Pruebas](#12-pruebas)
13. [Criterios de evaluación](#13-criterios-de-evaluación)
14. [Limitaciones y trabajo futuro](#14-limitaciones-y-trabajo-futuro)
15. [Conclusiones](#15-conclusiones)
16. [Autoría y contexto académico](#16-autoría-y-contexto-académico)

---

## 1. El reto

Preparar exámenes suele acabar en un caos de ficheros: apuntes en PDF, diapositivas
en PPTX, ejercicios sueltos, resúmenes en Word y preguntas copiadas a mano en
varias libretas. Cada vez que cambia el temario hay que repetir el mismo trabajo,
y es fácil que una pregunta quede sin respuesta o que dos versiones del material
digan cosas distintas.

**Reto:** separar el **contenido** de la **presentación**. El contenido se escribe
una vez en YAML; las plantillas deciden cómo se ve. Así se puede generar un
temario completo, un cuestionario sin respuestas y un solucionario desde la misma
fuente, sin copiar y pegar.

## 2. Objetivos

### Objetivo general

Diseñar e implementar una CLI que valide material de estudio estructurado y lo
renderice con plantillas, de forma reproducible y sin tocar los materiales
originales del alumno.

### Objetivos específicos

- Definir un esquema YAML claro para temario, preguntas y ejercicios.
- Validar el YAML con mensajes de error comprensibles y sin ejecutar código.
- Renderizar el mismo contenido en varias plantillas y formatos.
- Generar un cuestionario sin respuestas y un solucionario separado.
- Crear un índice de todos los materiales de una carpeta.
- Ofrecer un esqueleto de YAML para empezar sin memorizar el esquema.
- No sobrescribir una salida existente sin `--forzar`.
- Cubrir la lógica con pruebas automáticas y un ejemplo original.
- Dejar preparada la arquitectura para añadir IA más adelante, sin depender de
  ella en esta primera versión.

## 3. Alcance

### Qué hace

- Lee ficheros `.yaml` y `.yml` en UTF-8.
- Valida campos obligatorios, tipos, identificadores, referencias entre temas y
  preguntas, y valores permitidos.
- Renderiza material completo, cuestionario y soluciones en Markdown; el material
  completo también en HTML.
- Genera un índice Markdown de una carpeta de materiales.
- Crea un YAML de ejemplo con `nuevo`.
- Escribe las salidas en la ruta indicada, creando carpetas si hace falta.
- Protege el contenido existente: no sobrescribe sin `--forzar`.

### Qué no hace

- **No modifica** los PDF, PPTX, DOCX ni apuntes que ya tengas. Solo lee los YAML
  que crees para esta CLI.
- **No genera PDF ni PPTX todavía.** La primera versión trabaja con Markdown y
  HTML, que son fáciles de revisar y versionar.
- **No usa IA todavía.** El diseño la deja para una fase posterior, siempre con
  revisión humana.
- No descarga contenido de Internet ni manda datos a ningún servicio.
- No es una herramienta para copiar exámenes de otros: el contenido lo escribe
  el alumno.
- No crea una base de datos ni un sistema de repetición espaciada.

## 4. Stack y arquitectura

| Pieza | Uso |
|---|---|
| Python 3.12 | Lenguaje del proyecto |
| [uv](https://docs.astral.sh/uv/) | Entorno y dependencias |
| Typer | Órdenes, opciones y ayuda |
| Rich | Tablas y mensajes |
| PyYAML | Lectura segura de YAML |
| Jinja2 | Plantillas de renderizado |
| pytest | Pruebas automáticas |
| pathlib | Todas las rutas |

### Estructura

```text
cli-examenes/
├─ src/examenes/
│  ├─ cli.py            Órdenes, opciones y salida
│  ├─ cargador.py       Lectura, validación y modelos
│  ├─ modelos.py        Tema, Pregunta, Ejercicio y Material
│  ├─ render.py         Jinja2, destinos y escritura
│  ├─ esqueleto.py      YAML de ejemplo para «nuevo»
│  ├─ errores.py        Errores humanos
│  ├─ util.py           slugify, tamaños y recuentos
│  └─ plantillas/
│     ├─ material.md.j2
│     ├─ material.html.j2
│     ├─ cuestionario.md.j2
│     ├─ soluciones.md.j2
│     └─ internas/indice.md.j2
├─ ejemplos/
│  └─ ejemplo-entornos.yaml
├─ tests/
├─ docs/
│  ├─ adr/0001-arquitectura.md
│  ├─ esquema-yaml.md
│  ├─ evidencias.md
│  └─ prompts.md
├─ pyproject.toml
└─ README.md
```

### Flujo interno

```text
YAML -> cargar_yaml() -> validar() -> Material -> Jinja2 -> Markdown/HTML
                           |
                           +-> lista de errores con ruta y campo
```

- `cli.py` no valida el esquema: solo llama al cargador, al renderizador y pinta.
- `cargador.py` usa `yaml.safe_load` (a través de un `SafeLoader` propio) y
  rechaza claves duplicadas.
- `modelos.py` no depende de Typer ni de Rich.
- `render.py` carga las plantillas desde el paquete y activa autoescape en HTML.
- `escribir_salida` no sobrescribe sin `--forzar`.

La decisión completa está en
[`docs/adr/0001-arquitectura.md`](docs/adr/0001-arquitectura.md).

## 5. Instalación y uso rápido

Requisitos: Python 3.12 y uv.

```bash
git clone <URL-del-repositorio>
cd cli-examenes
uv sync
uv run examenes --help
uv run examenes version
```

Crear un material desde cero:

```bash
uv run examenes nuevo material/ra3.yaml \
  --titulo "RA3 - Gestión de ficheros" \
  --modulo "Programación" \
  --autor "Borja Herreros"

# Edita material/ra3.yaml y valida
uv run examenes validar material/ra3.yaml

# Genera el material completo y el cuestionario
uv run examenes renderizar material/ra3.yaml
uv run examenes renderizar material/ra3.yaml \
  --plantilla cuestionario --salida salida/cuestionario.md
```

Probar con el ejemplo incluido:

```bash
uv run examenes validar ejemplos
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml --formato html
```

## 6. Esquema YAML

Un material tiene metadatos, temas, preguntas y ejercicios. Este es un resumen;
la referencia completa está en [`docs/esquema-yaml.md`](docs/esquema-yaml.md).

```yaml
version: 1
titulo: "Pruebas y depuración"
modulo: "Entornos de desarrollo"
curso: "1º DAM"
autor: "Borja Herreros"
fecha: 2026-11-20
descripcion: |
  Material de repaso.
objetivos:
  - "Diferenciar error, fallo y defecto."

temas:
  - id: "tema-1"
    titulo: "Pruebas unitarias"
    resumen: |
      Una prueba unitaria comprueba una unidad pequeña de código.
    puntos_clave:
      - "Patrón AAA: preparar, actuar y comprobar."
    recursos:
      - "Documentación de pytest"

preguntas:
  - id: "p1"
    tipo: "test"
    enunciado: "¿Qué comprueba una prueba unitaria?"
    opciones:
      - "a) El sistema completo"
      - "b) Una unidad pequeña de código"
    respuesta: "b"
    explicacion: "Aísla una función o clase."
    dificultad: "baja"
    tema: "tema-1"

ejercicios:
  - id: "e1"
    titulo: "Depurar una suma"
    enunciado: |
      Corrige la función que concatena en vez de sumar.
    pistas:
      - "Comprueba los tipos de los argumentos."
    solucion: |
      Convertir los argumentos a número antes de sumar.
```

### Reglas principales

- `version` debe ser `1`.
- `titulo`, `modulo` y al menos un `tema` son obligatorios.
- Cada `tema` necesita `id` y `titulo`.
- Cada `pregunta` necesita `id`, `tipo`, `enunciado`; si es `test`, al menos dos
  opciones y una `respuesta`.
- `tipo` puede ser `test`, `corta` o `practica`.
- `dificultad` puede ser `baja`, `media` o `alta`.
- Los `id` no se repiten entre temas, preguntas y ejercicios.
- Si una pregunta indica `tema`, ese tema debe existir.
- No se admiten campos desconocidos: así se detectan las erratas.
- Las claves duplicadas en el mismo objeto YAML son un error.

## 7. Comandos

### 7.1. `version`

```bash
uv run examenes version
```

### 7.2. `validar`

Valida un fichero o todos los YAML de una carpeta. Muestra una tabla con el
estado y todos los errores encontrados. Sale con código 1 si algo falla.

```bash
uv run examenes validar ejemplos
uv run examenes validar material/ra3.yaml
```

| Opción | Descripción |
|---|---|
| `RUTA` | Fichero o carpeta (por defecto, la actual) |

Se ignoran las carpetas ocultas, `.venv`, `__pycache__` y `node_modules`.

### 7.3. `listar`

Lista los materiales con título, módulo, número de temas, preguntas y ejercicios.
Si un fichero no es válido, lo marca como error y sale con código 1.

```bash
uv run examenes listar ejemplos
uv run examenes listar material
```

### 7.4. `plantillas`

Muestra las plantillas instaladas y los formatos disponibles.

```bash
uv run examenes plantillas
```

### 7.5. `renderizar`

Genera un documento a partir de un YAML.

```bash
uv run examenes renderizar material/ra3.yaml
uv run examenes renderizar material/ra3.yaml --formato html
uv run examenes renderizar material/ra3.yaml --plantilla cuestionario
uv run examenes renderizar material/ra3.yaml --plantilla soluciones
uv run examenes renderizar material/ra3.yaml --sin-soluciones
```

| Opción | Descripción |
|---|---|
| `ARCHIVO` | YAML del material |
| `--plantilla`, `-p` | `material`, `cuestionario` o `soluciones` |
| `--formato`, `-f` | `md` o `html` |
| `--salida`, `-s` | Fichero o carpeta de destino |
| `--sin-soluciones` | Oculta respuestas y soluciones en `material` |
| `--forzar` | Sobrescribe la salida si ya existe |

- Sin `--salida`, se escribe en `salida/<titulo-slug>.<formato>`.
- Si `--salida` es una carpeta (o no tiene extensión), se usa el nombre generado.
- `--sin-soluciones` no se permite con la plantilla `soluciones`.
- Nunca se sobrescribe un fichero existente sin `--forzar`.

### 7.6. `nuevo`

Crea un YAML válido con las secciones principales y textos de ejemplo.

```bash
uv run examenes nuevo material/ra3.yaml \
  --titulo "RA3 - Gestión de ficheros" \
  --modulo "Programación" \
  --curso "1º DAM" \
  --autor "Borja Herreros" \
  --fecha 2026-11-20
```

| Opción | Descripción |
|---|---|
| `DESTINO` | Fichero `.yaml`/`.yml`; si no tiene extensión, se añade `.yaml` |
| `--titulo` | Título del material (obligatorio) |
| `--modulo` | Módulo (obligatorio) |
| `--curso` | Curso o grupo (por defecto, `1º DAM`) |
| `--autor` | Nombre del autor |
| `--fecha` | Fecha ISO (por defecto, hoy) |
| `--forzar` | Sobrescribe si ya existe |

### 7.7. `indice`

Genera un índice Markdown con todos los materiales válidos de una carpeta.

```bash
uv run examenes indice material --salida material/INDICE.md
```

| Opción | Descripción |
|---|---|
| `RUTA` | Carpeta con materiales (por defecto, la actual) |
| `--salida`, `-s` | Fichero Markdown de salida (por defecto, `INDICE.md`) |
| `--forzar` | Sobrescribe el índice si ya existe |

Si algún YAML no es válido, no genera un índice a medias: muestra los errores y
sale con código 1.

## 8. Plantillas y formatos

| Plantilla | Formatos | Contenido |
|---|---|---|
| `material` | `md`, `html` | Guía completa: metadatos, objetivos, temario, preguntas y ejercicios |
| `cuestionario` | `md` | Solo enunciados y opciones, sin respuestas ni soluciones |
| `soluciones` | `md` | Respuestas, explicaciones y soluciones |

- Las plantillas viven en `src/examenes/plantillas/` y se cargan con Jinja2.
- En HTML se activa autoescape: un título con `<script>` se muestra como texto,
  no se ejecuta.
- Los bloques multilínea del YAML se conservan con `white-space: pre-wrap` en
  HTML y con párrafos normales en Markdown.
- El índice usa una plantilla interna que no aparece en `plantillas`.

## 9. Flujo de trabajo

1. **Crear** el YAML con `nuevo` o copiando un ejemplo.
2. **Rellenar** temas, preguntas y ejercicios.
3. **Validar** con `validar` hasta que no haya errores.
4. **Renderizar** el material completo y revisarlo.
5. **Generar** el cuestionario para practicar sin respuestas.
6. **Generar** las soluciones para corregir.
7. **Guardar** el YAML en Git; las salidas pueden regenerarse cuando haga falta.

La fuente de verdad es el YAML. Si cambia una pregunta, se cambia una vez y se
vuelven a generar todas las versiones.

## 10. Actividades

### Fase 1. Análisis

- [x] Revisar la estructura de los materiales existentes sin modificarlos.
- [x] Detectar que los PDF/PPTX/DOCX no son una fuente cómoda para regenerar.
- [x] Decidir que el contenido se escribe en YAML y la presentación en plantillas.
- [x] Separar este proyecto de `cli-disco` y de `cli-tareas`.

### Fase 2. Esquema y carga

- [x] Definir los modelos `Material`, `Tema`, `Pregunta` y `Ejercicio`.
- [x] Implementar la lectura con `yaml.safe_load` y rechazo de claves duplicadas.
- [x] Validar campos obligatorios, tipos, dificultades, referencias e IDs.
- [x] Rechazar campos desconocidos para detectar erratas.
- [x] Convertir fechas YAML a texto ISO.

### Fase 3. Renderizado

- [x] Crear la plantilla de material en Markdown.
- [x] Crear la plantilla de material en HTML con CSS y autoescape.
- [x] Crear la plantilla de cuestionario sin respuestas.
- [x] Crear la plantilla de soluciones.
- [x] Crear la plantilla interna de índice.
- [x] Evitar sobrescrituras sin `--forzar`.

### Fase 4. CLI y ejemplos

- [x] Implementar `version`, `validar`, `listar`, `plantillas`, `renderizar`,
      `nuevo` e `indice`.
- [x] Añadir un YAML de ejemplo original.
- [x] Ignorar `.venv`, carpetas ocultas y `node_modules` al recorrer carpetas.
- [x] Probar el flujo completo en `pruebas-examenes`.

### Fase 5. Calidad y documentación

- [x] Escribir pruebas de carga, validación, render, esqueleto y CLI.
- [x] Documentar el esquema completo en `docs/esquema-yaml.md`.
- [x] Registrar la arquitectura en `docs/adr/0001-arquitectura.md`.
- [x] Registrar el uso de IA en `docs/prompts.md`.
- [x] Guardar evidencias en `docs/evidencias.md`.

## 11. Evidencias

### Validación del ejemplo

```text
$ uv run examenes validar ejemplos
+-----------------------------------------+
| Archivo                        | Estado |
+--------------------------------+--------|
| ejemplos\ejemplo-entornos.yaml | OK     |
+-----------------------------------------+
1 fichero válido
```

### Renderizado

```bash
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml --formato html
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml --plantilla cuestionario
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml --plantilla soluciones
uv run examenes indice ejemplos --salida pruebas-examenes/INDICE.md
```

Resultados comprobados:

- El material Markdown incluye metadatos, objetivos, 2 temas, 3 preguntas y 1
  ejercicio.
- El cuestionario no incluye respuestas ni soluciones.
- El solucionario incluye respuestas, explicaciones y la solución del ejercicio.
- El HTML se genera con estilos y escapa el contenido peligroso.
- El índice incluye título, módulo, archivo, temas, preguntas y ejercicios.

### Pruebas automáticas

```text
$ uv run pytest -q
46 passed
```

Detalle en [`docs/evidencias.md`](docs/evidencias.md).

## 12. Pruebas

```bash
uv run pytest
uv run pytest -q
```

La suite usa `tmp_path` para no escribir en el repositorio y `CliRunner` para
probar la CLI. Cubre:

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

Para probar sin ensuciar el repositorio:

```bash
uv run examenes renderizar ejemplos/ejemplo-entornos.yaml \
  --salida pruebas-examenes/material.md
```

La carpeta `pruebas-examenes/` está ignorada por Git.

## 13. Criterios de evaluación

| Criterio | Qué se valora | Peso |
|---|---|---|
| Funcionalidad | Las órdenes generan el material esperado y cubren el flujo completo | 30 % |
| Validación y seguridad | Esquema claro, errores útiles, YAML seguro, sin sobrescrituras accidentales | 20 % |
| Plantillas | Markdown/HTML correctos, cuestionario y soluciones separados, autoescape | 15 % |
| Calidad del código | Separación por módulos, nombres claros, `pathlib`, `encoding="utf-8"` | 15 % |
| Pruebas | Suite automática, casos límite y ejemplo original | 10 % |
| Documentación y defensa | README/CDI, esquema, ADR, prompts, evidencias y explicación oral | 10 % |

### Escala de referencia

- **0-4:** no valida o genera documentos incoherentes.
- **5-6:** genera Markdown básico, pero faltan pruebas o validación.
- **7-8:** funciona, valida, está probado y documentado; algún caso límite
  pendiente.
- **9-10:** además demuestra separación contenido/presentación, seguridad,
  pruebas sólidas y una defensa técnica clara.

## 14. Limitaciones y trabajo futuro

### Limitaciones actuales

- Solo se generan Markdown y HTML; no PDF, PPTX ni DOCX.
- La IA no está integrada: no genera preguntas ni corrige respuestas.
- Las plantillas son las incluidas en el paquete; no se pueden añadir plantillas
  externas sin modificar el código.
- El YAML se escribe a mano; no hay importación desde PDF, Word o Moodle.
- No hay base de datos, repetición espaciada ni estadísticas de aciertos.
- La fecha se guarda como texto; no se valida el formato ISO.
- No se admiten imágenes dentro del material; solo texto y listas.

### Ideas para siguientes versiones

- Añadir un directorio de plantillas externas configurable.
- Exportar a PDF con una herramienta externa (Pandoc o WeasyPrint), como
  dependencia opcional.
- Exportar a PPTX con `python-pptx` para diapositivas de repaso.
- Añadir IA opcional para proponer preguntas a partir de los temas, con revisión
  humana y sin guardar claves.
- Crear un banco de preguntas con etiquetas y selección aleatoria.
- Añadir un modo de práctica interactiva en la terminal.
- Importar preguntas desde CSV o Markdown.
- Validar la fecha y otros campos con un esquema más estricto.

## 15. Conclusiones

Separar el contenido de la presentación simplifica mucho el mantenimiento del
material. El YAML obliga a pensar qué se quiere decir y las plantillas evitan
repetir formato en cada documento. La validación estricta detecta erratas antes
de generar nada, y el autoescape de HTML evita sustos con contenido copiado.

El proyecto también demuestra que una CLI pequeña puede ser útil sin IA: primero
se resuelve el problema real (estructura, validación y renderizado) y después se
puede añadir automatización inteligente si aporta valor. La IA no debe ser el
centro del proyecto, sino una ayuda opcional y revisable.

## 16. Autoría y contexto académico

- **Autor:** Borja Herreros
- **Curso:** 1º DAM (semipresencial)
- **Proyecto:** CLI de material de estudio
- **Repositorios relacionados:** `cli-disco` (mantenimiento de discos) y
  `cli-tareas` (automatización de tareas con ficheros). Son proyectos separados.
- **Uso de IA:** documentado en [`docs/prompts.md`](docs/prompts.md).
- **Licencia:** proyecto académico; no se distribuye con una licencia específica.
