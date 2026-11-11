"""Errores esperados de la CLI."""


class ExamenError(Exception):
    """Error humano, con el código de salida que debe devolver la CLI."""

    def __init__(self, mensaje: str, codigo_salida: int = 1) -> None:
        super().__init__(mensaje)
        self.codigo_salida = codigo_salida


class ErrorValidacion(ExamenError):
    """Un material no cumple el esquema; guarda todos los fallos juntos."""

    def __init__(self, errores: list[str]) -> None:
        self.errores = errores
        super().__init__("El material no cumple el esquema.", 1)
