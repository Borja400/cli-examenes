"""Pruebas del YAML de ejemplo que crea la CLI."""

from pathlib import Path

import pytest

from examenes.cargador import cargar_material
from examenes.errores import ExamenError
from examenes.esqueleto import crear_esqueleto


def test_esqueleto_es_valido(tmp_path: Path) -> None:
    texto = crear_esqueleto(
        "Material nuevo",
        "Programación",
        autor="Alumno",
        fecha="2026-11-20",
    )
    ruta = tmp_path / "nuevo.yaml"
    ruta.write_text(texto, encoding="utf-8")

    material = cargar_material(ruta)

    assert material.titulo == "Material nuevo"
    assert material.modulo == "Programación"
    assert material.autor == "Alumno"
    assert material.fecha == "2026-11-20"
    assert len(material.temas) == 1


def test_esqueleto_sin_titulo() -> None:
    with pytest.raises(ExamenError, match="título"):
        crear_esqueleto("", "Programación")


def test_esqueleto_sin_modulo() -> None:
    with pytest.raises(ExamenError, match="módulo"):
        crear_esqueleto("Material", "")
