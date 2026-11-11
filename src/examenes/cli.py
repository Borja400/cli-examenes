"""Interfaz de línea de órdenes: órdenes, opciones y salida."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, NoReturn

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from examenes import __version__
from examenes.cargador import (
    cargar_carpeta,
    cargar_material,
    recolectar_yaml,
    validar_archivo,
)
from examenes.errores import ErrorValidacion, ExamenError
from examenes.esqueleto import crear_esqueleto
from examenes.render import (
    DESCRIPCIONES,
    destino_salida,
    escribir_salida,
    plantillas_disponibles,
    renderizar_indice,
    renderizar_material,
)
from examenes.util import contar, tamano_legible

app = typer.Typer(
    help="examenes: genera material de estudio desde YAML y plantillas.",
    no_args_is_help=True,
    add_completion=False,
)
consola = Console()
consola_err = Console(stderr=True)


def _salir_con_error(error: ExamenError) -> NoReturn:
    """Muestra un error humano en stderr y termina con su código."""
    if isinstance(error, ErrorValidacion):
        for mensaje in error.errores:
            consola_err.print(f"[red]Error:[/red] {escape(mensaje)}")
    else:
        consola_err.print(f"[red]Error:[/red] {escape(str(error))}")
    raise typer.Exit(code=error.codigo_salida)


@app.command()
def version() -> None:
    """Muestra la versión instalada."""
    consola.print(f"examenes {__version__}")


@app.command()
def validar(
    ruta: Annotated[
        Path,
        typer.Argument(help="Fichero YAML o carpeta con materiales"),
    ] = Path("."),
) -> None:
    """Valida uno o varios ficheros YAML."""
    try:
        archivos = recolectar_yaml(ruta)
    except ExamenError as error:
        _salir_con_error(error)

    tabla = Table(title="Validación de materiales")
    tabla.add_column("Archivo", overflow="fold")
    tabla.add_column("Estado", overflow="fold")

    fallos = 0
    for archivo in archivos:
        errores = validar_archivo(archivo)
        if not errores:
            tabla.add_row(escape(str(archivo)), "[green]OK[/green]")
            continue

        fallos += 1
        tabla.add_row(
            escape(str(archivo)),
            f"[red]{contar(len(errores), 'error', 'errores')}[/red]",
        )
        for mensaje in errores:
            tabla.add_row("", escape(mensaje))

    consola.print(tabla)

    if fallos:
        consola_err.print(
            f"[red]{contar(fallos, 'fichero con errores', 'ficheros con errores')}[/red]"
        )
        raise typer.Exit(code=1)

    consola.print(
        f"[green]{contar(len(archivos), 'fichero válido', 'ficheros válidos')}[/green]"
    )


@app.command()
def listar(
    ruta: Annotated[
        Path,
        typer.Argument(help="Fichero YAML o carpeta con materiales"),
    ] = Path("."),
) -> None:
    """Lista los materiales y sus datos principales."""
    try:
        archivos = recolectar_yaml(ruta)
    except ExamenError as error:
        _salir_con_error(error)

    tabla = Table(title="Materiales")
    tabla.add_column("Archivo", overflow="fold")
    tabla.add_column("Título", overflow="fold")
    tabla.add_column("Módulo", overflow="fold")
    tabla.add_column("Temas", justify="right")
    tabla.add_column("Preguntas", justify="right")
    tabla.add_column("Ejercicios", justify="right")
    tabla.add_column("Estado")

    fallos = 0
    for archivo in archivos:
        try:
            material = cargar_material(archivo)
        except ErrorValidacion:
            fallos += 1
            tabla.add_row(
                escape(str(archivo)),
                "—",
                "—",
                "—",
                "—",
                "—",
                "[red]error[/red]",
            )
            continue
        except ExamenError as error:
            fallos += 1
            tabla.add_row(
                escape(str(archivo)),
                "—",
                "—",
                "—",
                "—",
                "—",
                f"[red]{escape(str(error))}[/red]",
            )
            continue

        tabla.add_row(
            escape(str(archivo)),
            escape(material.titulo),
            escape(material.modulo),
            str(len(material.temas)),
            str(len(material.preguntas)),
            str(len(material.ejercicios)),
            "[green]OK[/green]",
        )

    consola.print(tabla)

    if fallos:
        consola_err.print(
            f"[red]{contar(fallos, 'material no válido', 'materiales no válidos')}[/red]"
        )
        raise typer.Exit(code=1)


@app.command()
def plantillas() -> None:
    """Muestra las plantillas disponibles y sus formatos."""
    disponibles = plantillas_disponibles()

    if not disponibles:
        consola.print("No hay plantillas instaladas.")
        return

    tabla = Table(title="Plantillas")
    tabla.add_column("Plantilla")
    tabla.add_column("Formatos")
    tabla.add_column("Uso", overflow="fold")

    for nombre, formatos in disponibles.items():
        tabla.add_row(
            nombre,
            ", ".join(formatos),
            DESCRIPCIONES.get(nombre, ""),
        )

    consola.print(tabla)


@app.command()
def renderizar(
    archivo: Annotated[Path, typer.Argument(help="Fichero YAML del material")],
    plantilla: Annotated[
        str,
        typer.Option("--plantilla", "-p", help="material, cuestionario o soluciones"),
    ] = "material",
    formato: Annotated[
        str,
        typer.Option("--formato", "-f", help="md o html"),
    ] = "md",
    salida: Annotated[
        Path | None,
        typer.Option("--salida", "-s", help="Fichero o carpeta de destino"),
    ] = None,
    sin_soluciones: Annotated[
        bool,
        typer.Option("--sin-soluciones", help="Oculta respuestas y soluciones"),
    ] = False,
    forzar: Annotated[
        bool,
        typer.Option("--forzar", help="Sobrescribe la salida si ya existe"),
    ] = False,
) -> None:
    """Genera un documento a partir de un YAML y una plantilla."""
    if sin_soluciones and plantilla == "soluciones":
        _salir_con_error(
            ExamenError(
                "La plantilla «soluciones» no se puede generar sin soluciones."
            )
        )

    try:
        material = cargar_material(archivo)
        texto = renderizar_material(
            material,
            plantilla,
            formato,
            mostrar_soluciones=not sin_soluciones,
        )
        destino = destino_salida(salida, material, formato)
        destino = escribir_salida(texto, destino, forzar)
    except ErrorValidacion as error:
        _salir_con_error(
            ErrorValidacion(
                [f"{archivo}: {mensaje}" for mensaje in error.errores]
            )
        )
    except ExamenError as error:
        _salir_con_error(error)

    consola.print(f"[green]Generado:[/green] {escape(str(destino))}")
    consola.print(
        f"{contar(len(material.temas), 'tema', 'temas')} · "
        f"{contar(len(material.preguntas), 'pregunta', 'preguntas')} · "
        f"{contar(len(material.ejercicios), 'ejercicio', 'ejercicios')} · "
        f"{tamano_legible(len(texto.encode('utf-8')))}"
    )


@app.command()
def nuevo(
    destino: Annotated[Path, typer.Argument(help="Fichero YAML que se crea")],
    titulo: Annotated[str, typer.Option("--titulo", help="Título del material")],
    modulo: Annotated[str, typer.Option("--modulo", help="Módulo del material")],
    curso: Annotated[
        str,
        typer.Option("--curso", help="Curso o grupo"),
    ] = "1º DAM",
    autor: Annotated[
        str,
        typer.Option("--autor", help="Nombre del autor"),
    ] = "",
    fecha: Annotated[
        str,
        typer.Option("--fecha", help="Fecha en formato ISO (por defecto, hoy)"),
    ] = "",
    forzar: Annotated[
        bool,
        typer.Option("--forzar", help="Sobrescribe el fichero si ya existe"),
    ] = False,
) -> None:
    """Crea un YAML de ejemplo listo para rellenar."""
    if not destino.suffix:
        destino = destino.with_suffix(".yaml")
    elif destino.suffix.lower() not in {".yaml", ".yml"}:
        _salir_con_error(
            ExamenError("El destino debe terminar en .yaml o .yml.")
        )

    try:
        texto = crear_esqueleto(titulo, modulo, curso, autor, fecha)
        destino = escribir_salida(texto, destino, forzar)
    except ExamenError as error:
        _salir_con_error(error)

    consola.print(f"[green]Creado:[/green] {escape(str(destino))}")
    consola.print("Rellena los temas, preguntas y ejercicios y ejecuta:")
    consola.print(f"  uv run examenes validar {escape(str(destino))}")


@app.command()
def indice(
    ruta: Annotated[
        Path,
        typer.Argument(help="Carpeta con materiales YAML"),
    ] = Path("."),
    salida: Annotated[
        Path,
        typer.Option("--salida", "-s", help="Fichero Markdown de índice"),
    ] = Path("INDICE.md"),
    forzar: Annotated[
        bool,
        typer.Option("--forzar", help="Sobrescribe el índice si ya existe"),
    ] = False,
) -> None:
    """Genera un índice Markdown con todos los materiales."""
    try:
        base, materiales = cargar_carpeta(ruta)
        texto = renderizar_indice(materiales, base)
        destino = escribir_salida(texto, salida, forzar)
    except ExamenError as error:
        _salir_con_error(error)

    consola.print(f"[green]Índice generado:[/green] {escape(str(destino))}")
    consola.print(
        f"{contar(len(materiales), 'material', 'materiales')} · "
        f"{tamano_legible(len(texto.encode('utf-8')))}"
    )


if __name__ == "__main__":
    app()
