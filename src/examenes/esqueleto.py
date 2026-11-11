"""Creación de un YAML de ejemplo para empezar un material."""

from __future__ import annotations

import datetime as dt
import json

from examenes.errores import ExamenError


def _citar(texto: str) -> str:
    """Cita un texto como escalar YAML entre comillas dobles."""
    return json.dumps(texto, ensure_ascii=False)


def crear_esqueleto(
    titulo: str,
    modulo: str,
    curso: str = "1º DAM",
    autor: str = "",
    fecha: str = "",
) -> str:
    """Devuelve un YAML válido con las secciones principales vacías."""
    titulo = titulo.strip()
    modulo = modulo.strip()
    if not titulo:
        raise ExamenError("El título no puede estar vacío.")
    if not modulo:
        raise ExamenError("El módulo no puede estar vacío.")

    fecha = fecha.strip() or dt.date.today().isoformat()

    return f"""# Material de estudio · esquema versión 1
version: 1
titulo: {_citar(titulo)}
modulo: {_citar(modulo)}
curso: {_citar(curso.strip())}
autor: {_citar(autor.strip())}
fecha: {_citar(fecha)}
descripcion: ""
objetivos:
  - "..."

temas:
  - id: "tema-1"
    titulo: "Tema 1"
    resumen: |
      Escribe aquí el resumen del tema.
    puntos_clave:
      - "..."
    recursos: []

preguntas:
  - id: "p1"
    tipo: "test"
    enunciado: "¿...?"
    opciones:
      - "a) ..."
      - "b) ..."
    respuesta: "a"
    explicacion: ""
    dificultad: "media"
    tema: "tema-1"

ejercicios:
  - id: "e1"
    titulo: "Ejercicio 1"
    enunciado: |
      Escribe aquí el enunciado del ejercicio.
    pistas: []
    solucion: ""
"""
