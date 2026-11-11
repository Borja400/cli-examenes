"""Modelos de datos del material de estudio."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Tema:
    """Un apartado del temario."""

    id: str
    titulo: str
    resumen: str = ""
    puntos_clave: list[str] = field(default_factory=list)
    recursos: list[str] = field(default_factory=list)


@dataclass
class Pregunta:
    """Una pregunta de test, corta o práctica."""

    id: str
    tipo: str
    enunciado: str
    opciones: list[str] = field(default_factory=list)
    respuesta: str = ""
    explicacion: str = ""
    dificultad: str = "media"
    tema: str = ""


@dataclass
class Ejercicio:
    """Un ejercicio con pistas y solución opcional."""

    id: str
    titulo: str
    enunciado: str
    pistas: list[str] = field(default_factory=list)
    solucion: str = ""


@dataclass
class Material:
    """Todo el contenido de un fichero YAML ya validado."""

    titulo: str
    modulo: str
    curso: str = ""
    autor: str = ""
    fecha: str = ""
    descripcion: str = ""
    objetivos: list[str] = field(default_factory=list)
    temas: list[Tema] = field(default_factory=list)
    preguntas: list[Pregunta] = field(default_factory=list)
    ejercicios: list[Ejercicio] = field(default_factory=list)
    ruta: Path | None = None
