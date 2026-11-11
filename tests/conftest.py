"""Fixtures compartidas por las pruebas."""

import copy
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def datos_validos() -> dict:
    """Un material mínimo pero completo."""
    return {
        "version": 1,
        "titulo": "Material de prueba",
        "modulo": "Programación",
        "curso": "1º DAM",
        "autor": "Alumno",
        "fecha": "2026-11-20",
        "descripcion": "Descripción de prueba.",
        "objetivos": ["Objetivo 1", "Objetivo 2"],
        "temas": [
            {
                "id": "tema-1",
                "titulo": "Tema 1",
                "resumen": "Resumen del tema.",
                "puntos_clave": ["Punto clave 1", "Punto clave 2"],
                "recursos": ["Recurso 1"],
            }
        ],
        "preguntas": [
            {
                "id": "p1",
                "tipo": "test",
                "enunciado": "¿Cuál es la respuesta correcta?",
                "opciones": ["a) Primera", "b) Segunda"],
                "respuesta": "a",
                "explicacion": "La primera es correcta.",
                "dificultad": "baja",
                "tema": "tema-1",
            },
            {
                "id": "p2",
                "tipo": "corta",
                "enunciado": "Explica el concepto.",
                "respuesta": "Es un concepto de prueba.",
                "dificultad": "media",
                "tema": "tema-1",
            },
        ],
        "ejercicios": [
            {
                "id": "e1",
                "titulo": "Ejercicio 1",
                "enunciado": "Haz algo con los datos.",
                "pistas": ["Pista 1"],
                "solucion": "Solución del ejercicio.",
            }
        ],
    }


@pytest.fixture
def archivo_valido(tmp_path: Path, datos_validos: dict) -> Path:
    """Escribe el material válido en un YAML temporal."""
    ruta = tmp_path / "material.yaml"
    ruta.write_text(
        yaml.safe_dump(datos_validos, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return ruta


@pytest.fixture
def copia_datos(datos_validos: dict) -> dict:
    """Copia profunda para modificar sin afectar a otras pruebas."""
    return copy.deepcopy(datos_validos)
