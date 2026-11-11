"""Pruebas de la interfaz de línea de órdenes."""

from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from examenes.cargador import cargar_material
from examenes.cli import app

runner = CliRunner()


def _escribir(ruta: Path, datos: dict) -> Path:
    ruta.write_text(
        yaml.safe_dump(datos, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return ruta


def test_version() -> None:
    resultado = runner.invoke(app, ["version"])

    assert resultado.exit_code == 0
    assert "examenes 0.1.0" in resultado.output


def test_validar_valido(archivo_valido: Path) -> None:
    resultado = runner.invoke(app, ["validar", str(archivo_valido)])

    assert resultado.exit_code == 0
    assert "OK" in resultado.output


def test_validar_invalido(copia_datos: dict, tmp_path: Path) -> None:
    del copia_datos["titulo"]
    ruta = _escribir(tmp_path / "invalido.yaml", copia_datos)

    resultado = runner.invoke(app, ["validar", str(ruta)])

    assert resultado.exit_code == 1
    assert "titulo" in resultado.output
    assert "obligatorio" in resultado.output


def test_listar(archivo_valido: Path) -> None:
    resultado = runner.invoke(
        app,
        ["listar", str(archivo_valido)],
        env={"COLUMNS": "200"},
    )

    assert resultado.exit_code == 0
    assert "Material de prueba" in resultado.output
    assert "Programación" in resultado.output


def test_listar_con_error(copia_datos: dict, tmp_path: Path) -> None:
    del copia_datos["modulo"]
    ruta = _escribir(tmp_path / "invalido.yaml", copia_datos)

    resultado = runner.invoke(app, ["listar", str(ruta)])

    assert resultado.exit_code == 1
    assert "error" in resultado.output


def test_plantillas() -> None:
    resultado = runner.invoke(app, ["plantillas"])

    assert resultado.exit_code == 0
    assert "material" in resultado.output
    assert "cuestionario" in resultado.output
    assert "soluciones" in resultado.output
    assert "html" in resultado.output


def test_renderizar_crea_archivo(archivo_valido: Path, tmp_path: Path) -> None:
    salida = tmp_path / "salida.md"

    resultado = runner.invoke(
        app,
        ["renderizar", str(archivo_valido), "--salida", str(salida)],
    )

    assert resultado.exit_code == 0
    assert salida.is_file()
    assert "Material de prueba" in salida.read_text(encoding="utf-8")


def test_renderizar_no_sobrescribe(archivo_valido: Path, tmp_path: Path) -> None:
    salida = tmp_path / "salida.md"

    primero = runner.invoke(
        app,
        ["renderizar", str(archivo_valido), "--salida", str(salida)],
    )
    segundo = runner.invoke(
        app,
        ["renderizar", str(archivo_valido), "--salida", str(salida)],
    )
    tercero = runner.invoke(
        app,
        [
            "renderizar",
            str(archivo_valido),
            "--salida",
            str(salida),
            "--forzar",
        ],
    )

    assert primero.exit_code == 0
    assert segundo.exit_code == 1
    assert "ya existe" in segundo.output
    assert tercero.exit_code == 0


def test_renderizar_sin_soluciones(archivo_valido: Path, tmp_path: Path) -> None:
    salida = tmp_path / "sin-soluciones.md"

    resultado = runner.invoke(
        app,
        [
            "renderizar",
            str(archivo_valido),
            "--sin-soluciones",
            "--salida",
            str(salida),
        ],
    )

    assert resultado.exit_code == 0
    texto = salida.read_text(encoding="utf-8")
    assert "**Respuesta:**" not in texto
    assert "Solución del ejercicio." not in texto


def test_renderizar_plantilla_invalida(
    archivo_valido: Path,
    tmp_path: Path,
) -> None:
    resultado = runner.invoke(
        app,
        [
            "renderizar",
            str(archivo_valido),
            "--plantilla",
            "inventada",
            "--salida",
            str(tmp_path / "salida.md"),
        ],
    )

    assert resultado.exit_code == 1
    assert "Plantilla desconocida" in resultado.output


def test_renderizar_soluciones_sin_soluciones(
    archivo_valido: Path,
    tmp_path: Path,
) -> None:
    resultado = runner.invoke(
        app,
        [
            "renderizar",
            str(archivo_valido),
            "--plantilla",
            "soluciones",
            "--sin-soluciones",
            "--salida",
            str(tmp_path / "salida.md"),
        ],
    )

    assert resultado.exit_code == 1
    assert "sin soluciones" in resultado.output


def test_nuevo_crea_yaml_valido(tmp_path: Path) -> None:
    destino = tmp_path / "material-nuevo"

    resultado = runner.invoke(
        app,
        [
            "nuevo",
            str(destino),
            "--titulo",
            "Material nuevo",
            "--modulo",
            "Programación",
            "--autor",
            "Alumno",
            "--fecha",
            "2026-11-20",
        ],
    )

    assert resultado.exit_code == 0
    ruta = destino.with_suffix(".yaml")
    assert ruta.is_file()
    material = cargar_material(ruta)
    assert material.titulo == "Material nuevo"


def test_nuevo_no_sobrescribe(tmp_path: Path) -> None:
    destino = tmp_path / "material-nuevo.yaml"
    argumentos = [
        "nuevo",
        str(destino),
        "--titulo",
        "Material nuevo",
        "--modulo",
        "Programación",
    ]

    primero = runner.invoke(app, argumentos)
    segundo = runner.invoke(app, argumentos)
    tercero = runner.invoke(app, [*argumentos, "--forzar"])

    assert primero.exit_code == 0
    assert segundo.exit_code == 1
    assert "ya existe" in segundo.output
    assert tercero.exit_code == 0


def test_indice(tmp_path: Path, archivo_valido: Path, copia_datos: dict) -> None:
    copia_datos["titulo"] = "Segundo material"
    _escribir(tmp_path / "segundo.yaml", copia_datos)
    salida = tmp_path / "INDICE.md"

    resultado = runner.invoke(
        app,
        ["indice", str(tmp_path), "--salida", str(salida)],
    )

    assert resultado.exit_code == 0
    texto = salida.read_text(encoding="utf-8")
    assert "Material de prueba" in texto
    assert "Segundo material" in texto


def test_indice_con_error(copia_datos: dict, tmp_path: Path) -> None:
    del copia_datos["titulo"]
    _escribir(tmp_path / "invalido.yaml", copia_datos)

    resultado = runner.invoke(
        app,
        ["indice", str(tmp_path), "--salida", str(tmp_path / "INDICE.md")],
    )

    assert resultado.exit_code == 1
    assert "Error" in resultado.output
