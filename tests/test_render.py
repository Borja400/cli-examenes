"""Pruebas de las plantillas y de la escritura de salidas."""

from pathlib import Path

import pytest
import yaml

from examenes.cargador import cargar_material
from examenes.errores import ExamenError
from examenes.render import (
    destino_salida,
    escribir_salida,
    nombre_salida,
    plantillas_disponibles,
    renderizar_indice,
    renderizar_material,
)
from examenes.util import slugify


def test_plantillas_disponibles() -> None:
    disponibles = plantillas_disponibles()

    assert disponibles["material"] == ["html", "md"]
    assert disponibles["cuestionario"] == ["md"]
    assert disponibles["soluciones"] == ["md"]
    assert "indice" not in disponibles


def test_material_incluye_todas_las_secciones(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    texto = renderizar_material(material)

    assert "# Material de prueba" in texto
    assert "## Objetivos" in texto
    assert "## Temario" in texto
    assert "## Preguntas" in texto
    assert "## Ejercicios" in texto
    assert "**Respuesta:** a" in texto
    assert "Solución del ejercicio." in texto


def test_material_sin_soluciones(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    texto = renderizar_material(material, mostrar_soluciones=False)

    assert "**Respuesta:**" not in texto
    assert "**Explicación:**" not in texto
    assert "**Solución:**" not in texto
    assert "Solución del ejercicio." not in texto


def test_cuestionario_no_incluye_respuestas(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    texto = renderizar_material(material, plantilla="cuestionario")

    assert "Cuestionario · Material de prueba" in texto
    assert "**Respuesta:**" not in texto
    assert "**Solución:**" not in texto
    assert "¿Cuál es la respuesta correcta?" in texto


def test_soluciones_incluye_respuestas(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    texto = renderizar_material(material, plantilla="soluciones")

    assert "**Respuesta:** a" in texto
    assert "La primera es correcta." in texto
    assert "Haz algo con los datos." in texto
    assert "Solución del ejercicio." in texto


def test_html_escapa_contenido(
    copia_datos: dict,
    tmp_path: Path,
) -> None:
    copia_datos["titulo"] = "<script>alert(1)</script>"
    copia_datos["preguntas"][0]["enunciado"] = "<b>Peligro</b>"
    ruta = tmp_path / "html.yaml"
    ruta.write_text(
        yaml.safe_dump(copia_datos, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    material = cargar_material(ruta)

    texto = renderizar_material(material, formato="html")

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in texto
    assert "<script>alert(1)</script>" not in texto
    assert "&lt;b&gt;Peligro&lt;/b&gt;" in texto
    assert "<b>Peligro</b>" not in texto


def test_formato_no_disponible(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    with pytest.raises(ExamenError, match="formato"):
        renderizar_material(material, plantilla="cuestionario", formato="html")


def test_plantilla_desconocida(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    with pytest.raises(ExamenError, match="Plantilla desconocida"):
        renderizar_material(material, plantilla="inventada")


def test_indice(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    texto = renderizar_indice([material], archivo_valido.parent)

    assert "# Índice de materiales" in texto
    assert "Material de prueba" in texto
    assert "**Temas:** 1" in texto
    assert "**Preguntas:** 2" in texto
    assert "`material.yaml`" in texto


def test_slugify() -> None:
    assert slugify("RA3 - Gestión de ficheros") == "ra3-gestion-de-ficheros"
    assert slugify("???") == "material"


def test_nombre_salida(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    assert nombre_salida(material, "md") == "material-de-prueba.md"


def test_destino_salida_fichero_y_carpeta(
    archivo_valido: Path,
    tmp_path: Path,
) -> None:
    material = cargar_material(archivo_valido)
    carpeta = tmp_path / "salida"
    carpeta.mkdir()

    assert destino_salida(carpeta, material, "md") == carpeta / "material-de-prueba.md"
    assert destino_salida(tmp_path / "otro.md", material, "md") == tmp_path / "otro.md"
    assert destino_salida(None, material, "md") == Path("salida") / "material-de-prueba.md"


def test_escribir_salida_no_sobrescribe(tmp_path: Path) -> None:
    destino = tmp_path / "salida.md"

    escribir_salida("primera", destino)
    assert destino.read_text(encoding="utf-8") == "primera"

    with pytest.raises(ExamenError, match="ya existe"):
        escribir_salida("segunda", destino)

    escribir_salida("segunda", destino, forzar=True)
    assert destino.read_text(encoding="utf-8") == "segunda"


def test_escribir_salida_en_carpeta(tmp_path: Path) -> None:
    with pytest.raises(ExamenError, match="carpeta"):
        escribir_salida("hola", tmp_path)
