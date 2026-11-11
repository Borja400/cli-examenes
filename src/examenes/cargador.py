"""Carga y validación de los ficheros YAML."""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import yaml

from examenes.errores import ErrorValidacion, ExamenError
from examenes.modelos import Ejercicio, Material, Pregunta, Tema

VERSION = 1
TIPOS_PREGUNTA = ("test", "corta", "practica")
DIFICULTADES = ("baja", "media", "alta")

CAMPOS_RAIZ = {
    "version",
    "titulo",
    "modulo",
    "curso",
    "autor",
    "fecha",
    "descripcion",
    "objetivos",
    "temas",
    "preguntas",
    "ejercicios",
}
CAMPOS_TEMA = {"id", "titulo", "resumen", "puntos_clave", "recursos"}
CAMPOS_PREGUNTA = {
    "id",
    "tipo",
    "enunciado",
    "opciones",
    "respuesta",
    "explicacion",
    "dificultad",
    "tema",
}
CAMPOS_EJERCICIO = {"id", "titulo", "enunciado", "pistas", "solucion"}
CARPETAS_IGNORADAS = {"__pycache__", "node_modules"}


class _CargadorSinDuplicados(yaml.SafeLoader):
    """SafeLoader que rechaza claves repetidas en el mismo objeto YAML."""

    def construct_mapping(self, node, deep=False):
        claves: set[object] = set()
        for clave_nodo, _ in node.value:
            clave = self.construct_object(clave_nodo, deep=deep)
            try:
                repetida = clave in claves
            except TypeError:
                repetida = False

            if repetida:
                raise yaml.constructor.ConstructorError(
                    "al leer un mapa",
                    node.start_mark,
                    f"clave duplicada: {clave!r}",
                    clave_nodo.start_mark,
                )

            try:
                claves.add(clave)
            except TypeError:
                # Una clave no hashable la rechazará PyYAML con su propio error.
                pass

        return super().construct_mapping(node, deep=deep)


def _validar_campos(
    datos: dict,
    permitidos: set[str],
    ruta: str,
    errores: list[str],
) -> None:
    """Avisa de campos desconocidos para detectar erratas."""
    for campo in datos:
        if campo not in permitidos:
            errores.append(f"{ruta}: campo desconocido «{campo}»")


def _texto(
    datos: dict,
    campo: str,
    ruta: str,
    errores: list[str],
    *,
    obligatorio: bool = False,
    defecto: str = "",
) -> str:
    """Lee un campo de texto y lo devuelve limpio."""
    valor = datos.get(campo, defecto)
    if valor is None:
        valor = ""

    if not isinstance(valor, str):
        errores.append(f"{ruta}.{campo}: debe ser texto")
        return ""

    limpio = valor.strip()
    if obligatorio and not limpio:
        errores.append(f"{ruta}.{campo}: es obligatorio")
    return limpio


def _lista_textos(
    datos: dict,
    campo: str,
    ruta: str,
    errores: list[str],
) -> list[str]:
    """Lee una lista de textos no vacíos."""
    valor = datos.get(campo, [])
    if valor is None:
        return []
    if not isinstance(valor, list):
        errores.append(f"{ruta}.{campo}: debe ser una lista")
        return []

    salida: list[str] = []
    for indice, elemento in enumerate(valor):
        if not isinstance(elemento, str) or not elemento.strip():
            errores.append(f"{ruta}.{campo}[{indice}]: debe ser texto no vacío")
            continue
        salida.append(elemento.strip())
    return salida


def _fecha(datos: dict, errores: list[str]) -> str:
    """Acepta texto o una fecha YAML y la convierte a ISO 8601."""
    valor = datos.get("fecha", "")
    if valor is None or valor == "":
        return ""
    if isinstance(valor, dt.datetime):
        return valor.date().isoformat()
    if isinstance(valor, dt.date):
        return valor.isoformat()
    if isinstance(valor, str):
        return valor.strip()

    errores.append("raíz.fecha: debe ser texto o una fecha YAML")
    return ""


def _registrar_id(
    identificador: str,
    ruta: str,
    ids: set[str],
    errores: list[str],
) -> None:
    """Comprueba que un identificador no esté repetido."""
    if not identificador:
        return
    if identificador in ids:
        errores.append(
            f"{ruta}.id: el identificador «{identificador}» está repetido"
        )
    else:
        ids.add(identificador)


def validar(datos: object) -> list[str]:
    """Valida el contenido de un YAML y devuelve todos los errores."""
    if not isinstance(datos, dict):
        return ["raíz: el YAML debe ser un objeto con claves y valores"]

    errores: list[str] = []
    _validar_campos(datos, CAMPOS_RAIZ, "raíz", errores)

    version = datos.get("version", VERSION)
    if isinstance(version, bool) or version != VERSION:
        errores.append("raíz.version: solo se admite la versión 1")

    _texto(datos, "titulo", "raíz", errores, obligatorio=True)
    _texto(datos, "modulo", "raíz", errores, obligatorio=True)
    _texto(datos, "curso", "raíz", errores)
    _texto(datos, "autor", "raíz", errores)
    _texto(datos, "descripcion", "raíz", errores)
    _fecha(datos, errores)
    _lista_textos(datos, "objetivos", "raíz", errores)

    ids: set[str] = set()
    ids_temas: set[str] = set()

    temas = datos.get("temas")
    if not isinstance(temas, list) or not temas:
        errores.append("raíz.temas: debe ser una lista con al menos un tema")
        temas = []

    for indice, tema in enumerate(temas):
        ruta_tema = f"temas[{indice}]"
        if not isinstance(tema, dict):
            errores.append(f"{ruta_tema}: debe ser un objeto")
            continue

        _validar_campos(tema, CAMPOS_TEMA, ruta_tema, errores)
        id_tema = _texto(tema, "id", ruta_tema, errores, obligatorio=True)
        _texto(tema, "titulo", ruta_tema, errores, obligatorio=True)
        _texto(tema, "resumen", ruta_tema, errores)
        _lista_textos(tema, "puntos_clave", ruta_tema, errores)
        _lista_textos(tema, "recursos", ruta_tema, errores)

        _registrar_id(id_tema, ruta_tema, ids, errores)
        if id_tema:
            ids_temas.add(id_tema)

    preguntas = datos.get("preguntas", [])
    if preguntas is None:
        preguntas = []
    if not isinstance(preguntas, list):
        errores.append("raíz.preguntas: debe ser una lista")
        preguntas = []

    for indice, pregunta in enumerate(preguntas):
        ruta_pregunta = f"preguntas[{indice}]"
        if not isinstance(pregunta, dict):
            errores.append(f"{ruta_pregunta}: debe ser un objeto")
            continue

        _validar_campos(pregunta, CAMPOS_PREGUNTA, ruta_pregunta, errores)
        id_pregunta = _texto(
            pregunta, "id", ruta_pregunta, errores, obligatorio=True
        )
        tipo = _texto(pregunta, "tipo", ruta_pregunta, errores, obligatorio=True)
        _texto(pregunta, "enunciado", ruta_pregunta, errores, obligatorio=True)
        opciones = _lista_textos(pregunta, "opciones", ruta_pregunta, errores)
        respuesta = _texto(pregunta, "respuesta", ruta_pregunta, errores)
        _texto(pregunta, "explicacion", ruta_pregunta, errores)
        dificultad = _texto(
            pregunta,
            "dificultad",
            ruta_pregunta,
            errores,
            defecto="media",
        )
        tema = _texto(pregunta, "tema", ruta_pregunta, errores)

        if tipo and tipo not in TIPOS_PREGUNTA:
            errores.append(
                f"{ruta_pregunta}.tipo: debe ser uno de "
                f"{', '.join(TIPOS_PREGUNTA)}"
            )
        if tipo == "test":
            if len(opciones) < 2:
                errores.append(
                    f"{ruta_pregunta}.opciones: un test necesita al menos dos opciones"
                )
            if not respuesta:
                errores.append(
                    f"{ruta_pregunta}.respuesta: es obligatoria en un test"
                )
        if dificultad and dificultad not in DIFICULTADES:
            errores.append(
                f"{ruta_pregunta}.dificultad: debe ser una de "
                f"{', '.join(DIFICULTADES)}"
            )
        if tema and tema not in ids_temas:
            errores.append(
                f"{ruta_pregunta}.tema: no existe el tema «{tema}»"
            )

        _registrar_id(id_pregunta, ruta_pregunta, ids, errores)

    ejercicios = datos.get("ejercicios", [])
    if ejercicios is None:
        ejercicios = []
    if not isinstance(ejercicios, list):
        errores.append("raíz.ejercicios: debe ser una lista")
        ejercicios = []

    for indice, ejercicio in enumerate(ejercicios):
        ruta_ejercicio = f"ejercicios[{indice}]"
        if not isinstance(ejercicio, dict):
            errores.append(f"{ruta_ejercicio}: debe ser un objeto")
            continue

        _validar_campos(ejercicio, CAMPOS_EJERCICIO, ruta_ejercicio, errores)
        id_ejercicio = _texto(
            ejercicio, "id", ruta_ejercicio, errores, obligatorio=True
        )
        _texto(ejercicio, "titulo", ruta_ejercicio, errores, obligatorio=True)
        _texto(ejercicio, "enunciado", ruta_ejercicio, errores, obligatorio=True)
        _lista_textos(ejercicio, "pistas", ruta_ejercicio, errores)
        _texto(ejercicio, "solucion", ruta_ejercicio, errores)

        _registrar_id(id_ejercicio, ruta_ejercicio, ids, errores)

    return errores


def _fecha_plana(valor: object) -> str:
    """Convierte una fecha YAML a texto ISO."""
    if isinstance(valor, dt.datetime):
        return valor.date().isoformat()
    if isinstance(valor, dt.date):
        return valor.isoformat()
    return str(valor or "").strip()


def _construir(datos: dict, ruta: Path) -> Material:
    """Convierte un diccionario ya validado en objetos del dominio."""
    temas = [
        Tema(
            id=str(tema.get("id", "")).strip(),
            titulo=str(tema.get("titulo", "")).strip(),
            resumen=str(tema.get("resumen", "") or "").strip(),
            puntos_clave=[
                str(punto).strip() for punto in (tema.get("puntos_clave") or [])
            ],
            recursos=[
                str(recurso).strip() for recurso in (tema.get("recursos") or [])
            ],
        )
        for tema in (datos.get("temas") or [])
    ]

    preguntas = [
        Pregunta(
            id=str(pregunta.get("id", "")).strip(),
            tipo=str(pregunta.get("tipo", "")).strip(),
            enunciado=str(pregunta.get("enunciado", "")).strip(),
            opciones=[
                str(opcion).strip() for opcion in (pregunta.get("opciones") or [])
            ],
            respuesta=str(pregunta.get("respuesta", "") or "").strip(),
            explicacion=str(pregunta.get("explicacion", "") or "").strip(),
            dificultad=str(pregunta.get("dificultad", "media") or "media").strip(),
            tema=str(pregunta.get("tema", "") or "").strip(),
        )
        for pregunta in (datos.get("preguntas") or [])
    ]

    ejercicios = [
        Ejercicio(
            id=str(ejercicio.get("id", "")).strip(),
            titulo=str(ejercicio.get("titulo", "")).strip(),
            enunciado=str(ejercicio.get("enunciado", "")).strip(),
            pistas=[
                str(pista).strip() for pista in (ejercicio.get("pistas") or [])
            ],
            solucion=str(ejercicio.get("solucion", "") or "").strip(),
        )
        for ejercicio in (datos.get("ejercicios") or [])
    ]

    return Material(
        titulo=str(datos.get("titulo", "")).strip(),
        modulo=str(datos.get("modulo", "")).strip(),
        curso=str(datos.get("curso", "") or "").strip(),
        autor=str(datos.get("autor", "") or "").strip(),
        fecha=_fecha_plana(datos.get("fecha", "")),
        descripcion=str(datos.get("descripcion", "") or "").strip(),
        objetivos=[
            str(objetivo).strip() for objetivo in (datos.get("objetivos") or [])
        ],
        temas=temas,
        preguntas=preguntas,
        ejercicios=ejercicios,
        ruta=ruta,
    )


def cargar_yaml(ruta: Path) -> object:
    """Lee un YAML con un cargador seguro y sin claves duplicadas."""
    ruta = ruta.expanduser()
    if not ruta.is_file():
        raise ExamenError(f"El fichero «{ruta}» no existe o no es un fichero.")

    try:
        texto = ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ExamenError(f"No puedo leer «{ruta}»: {error}") from error

    try:
        return yaml.load(texto, Loader=_CargadorSinDuplicados)
    except yaml.YAMLError as error:
        raise ExamenError(f"El YAML de «{ruta}» no es válido: {error}") from error


def cargar_material(ruta: Path) -> Material:
    """Carga un YAML, lo valida y devuelve el material."""
    ruta = ruta.expanduser()
    datos = cargar_yaml(ruta)

    if not isinstance(datos, dict):
        raise ErrorValidacion(
            ["raíz: el YAML debe ser un objeto con claves y valores"]
        )

    errores = validar(datos)
    if errores:
        raise ErrorValidacion(errores)

    return _construir(datos, ruta)


def validar_archivo(ruta: Path) -> list[str]:
    """Devuelve los errores de un fichero, o una lista vacía si es válido."""
    try:
        cargar_material(ruta)
    except ErrorValidacion as error:
        return error.errores
    except ExamenError as error:
        return [str(error)]
    return []


def recolectar_yaml(ruta: Path) -> list[Path]:
    """Devuelve un fichero YAML o todos los de una carpeta, ordenados."""
    ruta = ruta.expanduser()

    if ruta.is_file():
        return [ruta]
    if not ruta.is_dir():
        raise ExamenError(f"«{ruta}» no existe o no es un fichero ni una carpeta.")

    archivos: list[Path] = []
    try:
        for actual, dirs, nombres in os.walk(ruta):
            dirs[:] = sorted(
                carpeta
                for carpeta in dirs
                if not carpeta.startswith(".") and carpeta not in CARPETAS_IGNORADAS
            )
            for nombre in nombres:
                if Path(nombre).suffix.lower() in {".yaml", ".yml"}:
                    archivos.append(Path(actual) / nombre)
    except OSError as error:
        raise ExamenError(f"No puedo leer «{ruta}»: {error}") from error

    if not archivos:
        raise ExamenError(
            f"No encuentro ficheros .yaml o .yml en «{ruta}»."
        )

    return sorted(archivos, key=lambda archivo: str(archivo).lower())


def cargar_carpeta(ruta: Path) -> tuple[Path, list[Material]]:
    """Carga todos los YAML de una carpeta; falla si alguno no es válido."""
    archivos = recolectar_yaml(ruta)
    base = ruta.expanduser() if ruta.is_dir() else ruta.expanduser().parent

    materiales: list[Material] = []
    errores: list[str] = []

    for archivo in archivos:
        try:
            materiales.append(cargar_material(archivo))
        except ErrorValidacion as error:
            errores.extend(f"{archivo}: {mensaje}" for mensaje in error.errores)
        except ExamenError as error:
            errores.append(f"{archivo}: {error}")

    if errores:
        raise ErrorValidacion(errores)

    return base, materiales
