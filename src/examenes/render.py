"""Renderizado de materiales con plantillas Jinja2."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from examenes.errores import ExamenError
from examenes.modelos import Material
from examenes.util import slugify

DIRECTORIO_PLANTILLAS = Path(__file__).resolve().parent / "plantillas"

DESCRIPCIONES = {
    "material": "Guía completa con temario, preguntas y ejercicios",
    "cuestionario": "Solo enunciados, sin respuestas ni soluciones",
    "soluciones": "Respuestas y soluciones para corregir",
}


def plantillas_disponibles() -> dict[str, list[str]]:
    """Devuelve las plantillas y sus formatos, por ejemplo material: [html, md]."""
    disponibles: dict[str, list[str]] = {}

    if not DIRECTORIO_PLANTILLAS.is_dir():
        return disponibles

    for ruta in sorted(DIRECTORIO_PLANTILLAS.glob("*.j2")):
        partes = ruta.name.split(".")
        if len(partes) != 3:
            continue
        plantilla, formato = partes[0], partes[1]
        disponibles.setdefault(plantilla, []).append(formato)

    return {
        plantilla: sorted(formatos)
        for plantilla, formatos in sorted(disponibles.items())
    }


def _entorno() -> Environment:
    """Prepara Jinja2 con autoescape solo para las plantillas HTML."""
    return Environment(
        loader=FileSystemLoader(str(DIRECTORIO_PLANTILLAS)),
        autoescape=lambda nombre: nombre.endswith((".html.j2", ".htm.j2")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def renderizar_material(
    material: Material,
    plantilla: str = "material",
    formato: str = "md",
    mostrar_soluciones: bool = True,
) -> str:
    """Renderiza un material con la plantilla y el formato pedidos."""
    disponibles = plantillas_disponibles()

    if plantilla not in disponibles:
        raise ExamenError(
            f"Plantilla desconocida: «{plantilla}». "
            f"Disponibles: {', '.join(disponibles)}."
        )
    if formato not in disponibles[plantilla]:
        raise ExamenError(
            f"El formato «{formato}» no existe para «{plantilla}». "
            f"Formatos: {', '.join(disponibles[plantilla])}."
        )

    nombre = f"{plantilla}.{formato}.j2"
    try:
        plantilla_jinja = _entorno().get_template(nombre)
    except TemplateNotFound as error:
        raise ExamenError(f"No encuentro la plantilla «{nombre}».") from error

    return plantilla_jinja.render(
        material=material,
        mostrar_soluciones=mostrar_soluciones,
    )


def renderizar_indice(materiales: list[Material], base: Path) -> str:
    """Renderiza un índice Markdown con todos los materiales."""
    registros: list[dict[str, object]] = []

    for material in materiales:
        archivo = ""
        if material.ruta is not None:
            try:
                archivo = str(material.ruta.relative_to(base))
            except ValueError:
                archivo = str(material.ruta)
        registros.append({"material": material, "archivo": archivo})

    try:
        plantilla = _entorno().get_template("internas/indice.md.j2")
    except TemplateNotFound as error:
        raise ExamenError("No encuentro la plantilla del índice.") from error

    return plantilla.render(registros=registros, base=base)


def nombre_salida(material: Material, formato: str) -> str:
    """Calcula un nombre de fichero estable a partir del título."""
    return f"{slugify(material.titulo)}.{formato}"


def destino_salida(
    salida: Path | None,
    material: Material,
    formato: str,
) -> Path:
    """Decide si «salida» es un fichero, una carpeta o el destino por defecto."""
    nombre = nombre_salida(material, formato)

    if salida is None:
        return Path("salida") / nombre

    salida = salida.expanduser()
    if salida.is_dir() or not salida.suffix:
        return salida / nombre
    return salida


def escribir_salida(texto: str, destino: Path, forzar: bool = False) -> Path:
    """Escribe el texto en UTF-8 sin sobrescribir salvo con --forzar."""
    destino = destino.expanduser()

    if destino.is_dir():
        raise ExamenError(f"«{destino}» es una carpeta; indica un fichero.")
    if destino.exists() and not forzar:
        raise ExamenError(
            f"«{destino}» ya existe. Usa --forzar para sobrescribirlo."
        )

    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
    except OSError as error:
        raise ExamenError(f"No puedo escribir «{destino}»: {error}") from error

    return destino
