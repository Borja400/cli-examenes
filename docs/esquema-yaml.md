# Esquema YAML · versión 1

Este documento es la referencia completa del fichero que lee `examenes`. La
validación está implementada en `src/examenes/cargador.py`; si cambias una regla,
actualiza también este documento y las pruebas.

## Reglas generales

- El fichero debe estar en **UTF-8**.
- La raíz debe ser un objeto YAML con claves y valores.
- `version` es opcional; si se indica, debe ser `1` (por defecto se asume 1).
- No se admiten **campos desconocidos**: sirven para detectar erratas.
- No se admiten **claves duplicadas** en el mismo objeto.
- Los campos de texto deben ser texto. Un número o un booleano en un campo de
  texto es un error.
- Los identificadores (`id`) son únicos entre temas, preguntas y ejercicios.
- Los textos vacíos no cuentan como contenido: una lista con `""` es un error.

## Estructura

```yaml
version: 1
titulo: "Título del material"
modulo: "Nombre del módulo"
curso: "1º DAM"
autor: "Nombre del autor"
fecha: 2026-11-20
descripcion: |
  Texto libre.
objetivos:
  - "Objetivo 1"

temas:
  - id: "tema-1"
    titulo: "Título del tema"
    resumen: |
      Texto libre.
    puntos_clave:
      - "Punto clave"
    recursos:
      - "Recurso"

preguntas:
  - id: "p1"
    tipo: "test"
    enunciado: "¿...?"
    opciones:
      - "a) ..."
      - "b) ..."
    respuesta: "b"
    explicacion: "Por qué es correcta."
    dificultad: "media"
    tema: "tema-1"

ejercicios:
  - id: "e1"
    titulo: "Título del ejercicio"
    enunciado: |
      Texto libre.
    pistas:
      - "Pista"
    solucion: |
      Solución.
```

## Raíz

| Campo | Tipo | Obligatorio | Por defecto | Descripción |
|---|---|---|---|---|
| `version` | entero | No | `1` | Solo se admite 1 |
| `titulo` | texto | Sí | — | Título del material |
| `modulo` | texto | Sí | — | Módulo o asignatura |
| `curso` | texto | No | `""` | Curso o grupo |
| `autor` | texto | No | `""` | Autor del material |
| `fecha` | texto o fecha YAML | No | `""` | Se normaliza a ISO 8601 |
| `descripcion` | texto | No | `""` | Descripción libre |
| `objetivos` | lista de textos | No | `[]` | Objetivos de aprendizaje |
| `temas` | lista de objetos | Sí | — | Al menos un tema |
| `preguntas` | lista de objetos | No | `[]` | Preguntas del material |
| `ejercicios` | lista de objetos | No | `[]` | Ejercicios del material |

### Fecha

Se aceptan las tres formas siguientes:

```yaml
fecha: 2026-11-20          # fecha YAML -> "2026-11-20"
fecha: "2026-11-20"        # texto -> "2026-11-20"
fecha: 2026-11-20T10:30:00 # fecha y hora YAML -> "2026-11-20"
```

La fecha se guarda como texto y no se valida el formato ISO. Si necesitas otro
formato, escríbelo como texto.

## Temas

Cada elemento de `temas` es un objeto:

| Campo | Tipo | Obligatorio | Por defecto | Descripción |
|---|---|---|---|---|
| `id` | texto | Sí | — | Identificador único |
| `titulo` | texto | Sí | — | Título del tema |
| `resumen` | texto | No | `""` | Explicación del tema |
| `puntos_clave` | lista de textos | No | `[]` | Ideas que hay que recordar |
| `recursos` | lista de textos | No | `[]` | Enlaces o referencias |

`temas` debe ser una lista con al menos un elemento. Un tema sin `id` o sin
`titulo` invalida el material.

## Preguntas

Cada elemento de `preguntas` es un objeto:

| Campo | Tipo | Obligatorio | Por defecto | Descripción |
|---|---|---|---|---|
| `id` | texto | Sí | — | Identificador único |
| `tipo` | texto | Sí | — | `test`, `corta` o `practica` |
| `enunciado` | texto | Sí | — | Texto de la pregunta |
| `opciones` | lista de textos | No | `[]` | Opciones de un test |
| `respuesta` | texto | Según el tipo | `""` | Respuesta correcta |
| `explicacion` | texto | No | `""` | Justificación |
| `dificultad` | texto | No | `media` | `baja`, `media` o `alta` |
| `tema` | texto | No | `""` | `id` de un tema existente |

Reglas específicas:

- Si `tipo` es `test`, `opciones` debe tener al menos dos elementos y
  `respuesta` no puede estar vacía.
- Si `tipo` es `corta` o `practica`, `opciones` puede estar vacía.
- Si se indica `tema`, debe coincidir con el `id` de un tema del mismo fichero.
- `dificultad` solo admite `baja`, `media` o `alta`.

## Ejercicios

Cada elemento de `ejercicios` es un objeto:

| Campo | Tipo | Obligatorio | Por defecto | Descripción |
|---|---|---|---|---|
| `id` | texto | Sí | — | Identificador único |
| `titulo` | texto | Sí | — | Título del ejercicio |
| `enunciado` | texto | Sí | — | Qué hay que hacer |
| `pistas` | lista de textos | No | `[]` | Ayudas graduales |
| `solucion` | texto | No | `""` | Solución propuesta |

## Ejemplo mínimo válido

```yaml
version: 1
titulo: "Repaso de bases de datos"
modulo: "Base de datos"
temas:
  - id: "tema-1"
    titulo: "Modelo relacional"
```

## Ejemplo completo

El repositorio incluye
[`ejemplos/ejemplo-entornos.yaml`](../ejemplos/ejemplo-entornos.yaml), un material
original de 2 temas, 3 preguntas y 1 ejercicio. Es la mejor referencia para
copiar la estructura.

## Errores frecuentes

| Mensaje | Causa | Solución |
|---|---|---|
| `raíz.titulo: es obligatorio` | Falta el título o está vacío | Añade un `titulo` no vacío |
| `raíz.temas: debe ser una lista con al menos un tema` | No hay temas | Añade al menos un tema |
| `temas[0].id: es obligatorio` | El tema no tiene `id` | Añade un identificador |
| `...id: el identificador «x» está repetido` | Dos elementos usan el mismo `id` | Cambia uno de los dos |
| `preguntas[0].opciones: un test necesita al menos dos opciones` | Test con menos de dos opciones | Añade opciones o cambia el tipo |
| `preguntas[0].respuesta: es obligatoria en un test` | Test sin respuesta | Escribe la respuesta correcta |
| `preguntas[0].tema: no existe el tema «x»` | Referencia a un tema inexistente | Corrige el `id` o crea el tema |
| `...campo desconocido «x»` | Errata en el nombre de un campo | Revisa el esquema |
| `clave duplicada` | La misma clave aparece dos veces | Deja solo una |
| `...debe ser texto` | Número o booleano en un campo de texto | Escribe el valor entre comillas |

## Cómo comprobar un fichero

```bash
uv run examenes validar mi-material.yaml
uv run examenes listar mi-material.yaml
uv run examenes renderizar mi-material.yaml --salida pruebas-examenes/material.md
```
