# examenes · CLI de material de estudio (proyecto de 1º DAM)

## Stack y órdenes

- Python 3.12 + Typer + Rich + PyYAML + Jinja2, gestionado con uv
  (src layout, paquete `src/examenes`).
- Ejecutar: `uv run examenes --help` · Pruebas: `uv run pytest`.
- Validar el ejemplo: `uv run examenes validar ejemplos`.
- Comprobar una orden concreta: `uv run examenes <orden> --help`.

## Normas

- Mensajes y comentarios en español; código claro antes que listo.
- `pathlib` siempre, `encoding="utf-8"`, nada de `os.system` ni `shell=True`:
  tiene que funcionar en Linux, Windows y macOS.
- El YAML se lee con `yaml.safe_load` (a través del `SafeLoader` propio) y se
  rechazan las claves duplicadas. Nunca uses `yaml.load` sin cargador seguro.
- No sobrescribas una salida existente sin `--forzar`. La protección está en
  `render.escribir_salida`.
- Las plantillas viven en `src/examenes/plantillas/`. Si añades una, debe tener
  el formato `nombre.formato.j2` para que `plantillas_disponibles` la detecte.
- El HTML se renderiza con autoescape. No lo desactives para contenido del YAML.
- No toques los materiales originales del alumno: PDF, PPTX, DOCX, apuntes ni
  carpetas de `E:\01-ESTUDIOS\FP-INFORMATICA\SEMIPRESENCIAL`. Este proyecto solo
  lee los YAML que se crean para la CLI.
- No copies contenido de exámenes, apuntes o libros al repositorio. Los ejemplos
  deben ser originales.
- No integres IA, claves ni servicios externos sin que el alumno lo pida y sin
  revisión humana. No escribas claves en ningún fichero.
- No hagas `git push` ni commits: los hace el alumno.
- Antes de cambiar un fichero, explica en 2-3 líneas qué vas a hacer.
- No borres ni sobrescribas trabajo del alumno sin permiso. Si encuentras cambios
  que no conoces, investígalos antes de tocarlos.

## Validación y seguridad

- `cargador.validar` devuelve una lista con todos los errores; no se para en el
  primero. Añade un mensaje claro con la ruta del campo (`temas[0].id`).
- Los identificadores son únicos entre temas, preguntas y ejercicios.
- Una pregunta de tipo `test` necesita al menos dos opciones y una respuesta.
- Si una pregunta referencia un `tema`, ese tema debe existir.
- Los campos desconocidos son un error: sirven para detectar erratas.
- La fecha puede ser texto o una fecha YAML; se normaliza a ISO 8601.
- Las carpetas ocultas, `.venv`, `__pycache__` y `node_modules` se ignoran al
  recorrer una carpeta.

## Pruebas

- `uv run pytest -q` debe quedar en verde antes de dar un cambio por terminado.
- Añade una prueba por cada fallo corregido y por cada orden o plantilla nueva.
- Usa `tmp_path` para ficheros y `CliRunner` para la CLI.
- No escribas salidas de prueba en el repositorio: usa `tmp_path` o
  `pruebas-examenes/`, que está ignorada por Git.
- Para el HTML, comprueba que el contenido peligroso se escapa.
- Para las salidas, comprueba el caso normal, el fichero existente sin
  `--forzar` y la sobrescritura con `--forzar`.
