# Registro de uso de IA

Este documento deja constancia de cómo se ha usado la IA en el proyecto. No es
una transcripción literal de la conversación, sino un resumen de las peticiones,
el resultado y la verificación humana.

## Reglas acordadas

- La IA puede proponer código, pruebas y documentación, pero **no decide** qué
  se entrega ni sustituye la revisión del alumno.
- El contenido de los materiales lo escribe el alumno. La IA no copia exámenes,
  apuntes ni libros.
- No se comparten claves, contraseñas ni ficheros `.env`.
- La IA no hace `git commit` ni `git push`; eso lo hace el alumno.
- No se integra IA en la CLI en esta versión. La IA se usa como ayuda para
  programar y documentar, no como dependencia del producto.
- Todo cambio se revisa y se prueba antes de darlo por bueno.

## Sesiones

| Fecha | Objetivo | Petición resumida | Resultado | Verificación |
|---|---|---|---|---|
| 2026-11-11 | Diseñar el proyecto | Crear una CLI de exámenes separada de `cli-disco`, empezando por YAML y plantillas | Esquema, módulos y flujo de trabajo | Revisión del alcance y del ejemplo |
| 2026-11-11 | Implementar la carga | Leer YAML de forma segura, validar campos y detectar errores | `cargador.py`, `modelos.py` y `errores.py` | Pruebas de campos obligatorios, IDs y referencias |
| 2026-11-11 | Crear plantillas | Generar material, cuestionario, soluciones e índice | Plantillas Markdown/HTML con Jinja2 | Render manual y pruebas de autoescape |
| 2026-11-11 | Implementar la CLI | Órdenes `validar`, `listar`, `plantillas`, `renderizar`, `nuevo` e `indice` | `cli.py` y `esqueleto.py` | `uv run pytest -q` y pruebas en `pruebas-examenes` |
| 2026-11-11 | Documentar el CDI | Convertir el README en el CDI y añadir esquema, ADR, prompts y evidencias | `README.md`, `AGENTS.md`, `docs/` | Revisión de contenidos y enlaces |

## Ejemplos de peticiones

Estas son las ideas que se pidieron, resumidas:

- «Quiero dos repos separados: uno de disco y otro de exámenes. Termina primero
  el de disco y luego el de exámenes.»
- «El de exámenes debe empezar con YAML y plantillas; la IA puede ser opcional
  más adelante.»
- «No recrees los PPTX, PDF ni ejercicios que ya tengo: no los toques.»
- «El README y los docs deben servir como CDI: reto, objetivos, índice,
  actividades, evidencias, criterios y conclusiones.»
- «No hagas commits ni push; eso lo hago yo.»

## Qué hizo la IA

- Proponer la estructura de módulos y el esquema YAML.
- Escribir el cargador con `SafeLoader`, la validación acumulativa y los modelos.
- Escribir las plantillas Jinja2 y activar autoescape en HTML.
- Escribir las pruebas con `tmp_path` y `CliRunner`.
- Redactar la documentación a partir del código y de las pruebas reales.

## Qué verificó el alumno

- Que el ejemplo se valida y se lista correctamente.
- Que el material, el cuestionario y las soluciones contienen lo que deben.
- Que el cuestionario no filtra respuestas.
- Que el HTML se abre en el navegador y muestra bien los acentos.
- Que una salida existente no se sobrescribe sin `--forzar`.
- Que no se tocaron los materiales originales ni los otros repositorios.
- Que las pruebas pasan en su equipo.

## Limitaciones

- La IA no puede decidir si el contenido de un material es académicamente
  correcto; eso es responsabilidad del alumno.
- Las plantillas y el esquema son una propuesta inicial: si el profesor pide otro
  formato, habrá que adaptarlos.
- Las cifras y los tamaños de las evidencias cambian si se modifica el ejemplo.
- La IA no ha generado PDF ni PPTX en esta versión.
