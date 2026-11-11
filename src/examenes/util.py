"""Funciones pequeñas que se usan en varias partes."""

import re
import unicodedata


def slugify(texto: str) -> str:
    """Convierte un título en un nombre de fichero seguro.

    «RA3 - Gestión de ficheros» -> «ra3-gestion-de-ficheros».
    """
    normalizado = unicodedata.normalize("NFKD", texto)
    sin_acentos = normalizado.encode("ascii", "ignore").decode("ascii")
    limpio = re.sub(r"[^a-zA-Z0-9]+", "-", sin_acentos).strip("-").lower()
    return limpio or "material"


def contar(cantidad: int, singular: str, plural: str) -> str:
    """Devuelve «1 tema» o «2 temas»."""
    return f"{cantidad} {singular if cantidad == 1 else plural}"


def tamano_legible(n: int) -> str:
    """Convierte bytes en texto: 532 B, 1.2 KB, 3.4 MB..."""
    if n < 1024:
        return f"{n} B"

    tamano = float(n)
    unidad = "B"
    for unidad in ("KB", "MB", "GB", "TB"):
        tamano /= 1024
        if tamano < 1024:
            break
    return f"{tamano:.1f} {unidad}"
