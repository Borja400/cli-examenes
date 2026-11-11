# ADR 0001 · Arquitectura de examenes

- **Estado:** aceptada
- **Fecha:** 2026-11-11
- **Contexto:** proyecto de 1º DAM, CLI de material de estudio

## Contexto

El material de estudio existente está repartido en PDF, PPTX, DOCX y apuntes.
Regenerar un cuestionario o un solucionario a partir de esos formatos obliga a
copiar y pegar, y cualquier cambio en una pregunta hay que repetirlo en varios
sitios. Además, el proyecto debía ser pequeño, comprensible y sin depender de
una IA o de servicios externos.

Había que decidir tres cosas:

1. Dónde vive el contenido.
2. Cómo se valida antes de generar nada.
3. Cómo se separa el contenido de la presentación.

## Decisión

Se adopta una arquitectura en capas ligera, con **src layout** y un módulo por
responsabilidad:

```text
src/examenes/
├─ cli.py            Interfaz: órdenes, opciones y tablas
├─ cargador.py       Lectura YAML, validación y construcción
├─ modelos.py        Material, Tema, Pregunta y Ejercicio
├─ render.py         Jinja2, destinos y escritura
├─ esqueleto.py      YAML de ejemplo para «nuevo»
├─ errores.py        ExamenError y ErrorValidacion
├─ util.py           slugify, tamaños y recuentos
└─ plantillas/
   ├─ material.md.j2
   ├─ material.html.j2
   ├─ cuestionario.md.j2
   ├─ soluciones.md.j2
   └─ internas/indice.md.j2
```

Reglas de la decisión:

- **El YAML es la fuente de verdad.** El contenido se escribe una vez; las
  plantillas solo deciden cómo se presenta.
- **Validar antes de renderizar.** `cargador.validar` acumula todos los errores
  con la ruta del campo y no construye el `Material` si hay alguno.
- **Carga segura.** Se usa un `SafeLoader` propio que, además, rechaza claves
  duplicadas en el mismo objeto YAML.
- **Modelos sin dependencias de interfaz.** `modelos.py` no importa Typer, Rich
  ni Jinja2. La CLI y el renderizador trabajan con objetos del dominio.
- **Plantillas externas.** Jinja2 carga las plantillas desde el paquete. Añadir
  una plantilla no obliga a tocar la lógica de la CLI.
- **Autoescape en HTML.** El contenido del YAML se escapa al generar HTML; un
  título con `<script>` se muestra como texto.
- **Salidas protegidas.** `escribir_salida` no sobrescribe un fichero existente
  sin `--forzar`, y crea las carpetas necesarias.
- **Sin IA en la primera versión.** La IA se deja como trabajo futuro, siempre
  opcional y con revisión humana.

## Alternativas consideradas

### Un único diccionario o JSON como fuente

- **Ventaja:** no hace falta definir modelos.
- **Motivo para descartarla:** el acceso con claves sueltas reparte la validación
  por todo el código y los errores se detectan tarde. YAML admite comentarios y
  bloques multilínea, que son más cómodos para apuntes.

### Markdown como fuente y expresiones regulares para extraer preguntas

- **Ventaja:** se escribe directamente lo que se lee.
- **Motivo para descartarla:** el formato libre hace imposible validar de forma
  fiable. Una pregunta con una lista mal indentada se interpretaría como otra
  cosa y el error aparecería al renderizar.

### Generar directamente PDF o PPTX

- **Ventaja:** el resultado final es el que se entrega.
- **Motivo para descartarla:** añade dependencias pesadas y dificulta la
  revisión. Markdown y HTML son texto, se versionan bien y se pueden abrir en
  cualquier equipo. PDF y PPTX quedan como trabajo futuro.

### Usar f-strings en lugar de Jinja2

- **Ventaja:** menos dependencias.
- **Motivo para descartarla:** mezcla presentación y lógica, y cada formato
  nuevo obligaría a duplicar código. Jinja2 permite mantener las plantillas en
  ficheros separados y probarlas con el mismo modelo.

### IA desde el primer día

- **Ventaja:** podría proponer preguntas a partir de los temas.
- **Motivo para descartarla:** introduce claves, coste, latencia y resultados no
  deterministas. El problema principal —estructura, validación y renderizado—
  se resuelve sin IA. Añadirla después es más fácil que quitar dependencias.

### Guardar el material en una base de datos

- **Ventaja:** consultas y estadísticas.
- **Motivo para descartarla:** para el alcance del proyecto, un fichero YAML por
  material es suficiente, se revisa en Git y no necesita servidor.

## Consecuencias

### Positivas

- El contenido se escribe una vez y se generan varias versiones coherentes.
- Los errores del YAML se detectan antes de escribir nada.
- Las plantillas se pueden cambiar sin tocar los datos.
- La CLI se prueba con `tmp_path` y `CliRunner` sin escribir en el repositorio.
- El autoescape evita inyecciones al generar HTML.
- El proyecto funciona en Linux, Windows y macOS.

### Negativas

- Hay más ficheros y más imports que en un script único.
- El esquema obliga a escribir YAML; no se puede empezar con texto libre.
- Las plantillas incluidas no se pueden sustituir sin modificar el paquete.
- No hay PDF, PPTX, imágenes ni IA todavía.
- La validación de la fecha es básica: se guarda como texto y no se comprueba
  el formato ISO.

## Cumplimiento

- `uv run pytest -q` cubre carga, validación, render, esqueleto y CLI.
- `uv run examenes validar ejemplos` devuelve el ejemplo como válido.
- `uv run examenes plantillas` muestra las plantillas y formatos instalados.
- Las pruebas de HTML comprueban que el contenido peligroso se escapa.
- Las salidas se prueban sin `--forzar` y con `--forzar`.
