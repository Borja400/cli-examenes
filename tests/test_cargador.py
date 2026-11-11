"""Pruebas de carga y validación de YAML."""

from pathlib import Path

import pytest
import yaml

from examenes.cargador import (
    cargar_carpeta,
    cargar_material,
    cargar_yaml,
    recolectar_yaml,
    validar,
    validar_archivo,
)
from examenes.errores import ErrorValidacion, ExamenError


def _escribir(ruta: Path, datos: dict) -> Path:
    ruta.write_text(
        yaml.safe_dump(datos, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return ruta


def test_carga_material_valido(archivo_valido: Path) -> None:
    material = cargar_material(archivo_valido)

    assert material.titulo == "Material de prueba"
    assert material.modulo == "Programación"
    assert len(material.temas) == 1
    assert len(material.preguntas) == 2
    assert len(material.ejercicios) == 1
    assert material.preguntas[0].opciones == ["a) Primera", "b) Segunda"]


def test_carga_el_ejemplo_del_repositorio() -> None:
    ruta = Path(__file__).parents[1] / "ejemplos" / "ejemplo-entornos.yaml"

    material = cargar_material(ruta)

    assert material.titulo == "Pruebas y depuración en entornos de desarrollo"
    assert material.modulo == "Entornos de desarrollo"
    assert len(material.temas) == 2
    assert len(material.preguntas) == 3


def test_falta_titulo(copia_datos: dict, tmp_path: Path) -> None:
    del copia_datos["titulo"]
    ruta = _escribir(tmp_path / "sin-titulo.yaml", copia_datos)

    errores = validar_archivo(ruta)

    assert any("titulo" in error and "obligatorio" in error for error in errores)


def test_test_sin_opciones(copia_datos: dict, tmp_path: Path) -> None:
    copia_datos["preguntas"][0]["opciones"] = []
    ruta = _escribir(tmp_path / "test-sin-opciones.yaml", copia_datos)

    errores = validar_archivo(ruta)

    assert any("opciones" in error for error in errores)


def test_test_sin_respuesta(copia_datos: dict, tmp_path: Path) -> None:
    copia_datos["preguntas"][0]["respuesta"] = ""
    ruta = _escribir(tmp_path / "test-sin-respuesta.yaml", copia_datos)

    errores = validar_archivo(ruta)

    assert any("respuesta" in error for error in errores)


def test_tema_referenciado_inexistente(copia_datos: dict, tmp_path: Path) -> None:
    copia_datos["preguntas"][1]["tema"] = "tema-9"
    ruta = _escribir(tmp_path / "tema-inexistente.yaml", copia_datos)

    errores = validar_archivo(ruta)

    assert any("tema-9" in error for error in errores)


def test_ids_duplicados(copia_datos: dict, tmp_path: Path) -> None:
    copia_datos["preguntas"][1]["id"] = "p1"
    ruta = _escribir(tmp_path / "ids-duplicados.yaml", copia_datos)

    errores = validar_archivo(ruta)

    assert any("repetido" in error for error in errores)


def test_campo_desconocido(copia_datos: dict, tmp_path: Path) -> None:
    copia_datos["inventado"] = "valor"
    ruta = _escribir(tmp_path / "campo-desconocido.yaml", copia_datos)

    errores = validar_archivo(ruta)

    assert any("campo desconocido" in error for error in errores)


def test_clave_duplicada(tmp_path: Path) -> None:
    ruta = tmp_path / "duplicada.yaml"
    ruta.write_text(
        'version: 1\ntitulo: "Uno"\ntitulo: "Dos"\n',
        encoding="utf-8",
    )

    with pytest.raises(ExamenError, match="duplicada"):
        cargar_yaml(ruta)


def test_fecha_yaml_se_convierte(tmp_path: Path) -> None:
    ruta = tmp_path / "fecha.yaml"
    ruta.write_text(
        "\n".join(
            [
                "version: 1",
                'titulo: "Material"',
                'modulo: "Módulo"',
                "fecha: 2026-11-20",
                "temas:",
                '  - id: "tema-1"',
                '    titulo: "Tema"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    material = cargar_material(ruta)

    assert material.fecha == "2026-11-20"


def test_validar_devuelve_varios_errores() -> None:
    errores = validar({"titulo": "", "temas": []})

    assert len(errores) >= 3


def test_cargar_carpeta(archivo_valido: Path, copia_datos: dict) -> None:
    copia_datos["titulo"] = "Otro material"
    _escribir(archivo_valido.parent / "otro.yaml", copia_datos)

    base, materiales = cargar_carpeta(archivo_valido.parent)

    assert base == archivo_valido.parent
    assert len(materiales) == 2
    assert {material.titulo for material in materiales} == {
        "Material de prueba",
        "Otro material",
    }


def test_cargar_carpeta_con_error(archivo_valido: Path, copia_datos: dict) -> None:
    del copia_datos["titulo"]
    _escribir(archivo_valido.parent / "invalido.yaml", copia_datos)

    with pytest.raises(ErrorValidacion) as error:
        cargar_carpeta(archivo_valido.parent)

    assert any("invalido.yaml" in mensaje for mensaje in error.value.errores)


def test_recolectar_yaml_ignora_carpetas_ocultas(
    archivo_valido: Path,
    copia_datos: dict,
) -> None:
    oculta = archivo_valido.parent / ".venv"
    oculta.mkdir()
    _escribir(oculta / "dependencia.yaml", copia_datos)

    archivos = recolectar_yaml(archivo_valido.parent)

    assert archivos == [archivo_valido]
