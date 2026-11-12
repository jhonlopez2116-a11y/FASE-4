"""
excepciones.py
Aquí definimos todas las excepciones propias de Software FJ.
Todas heredan de SoftwareFJError, así podemos atrapar cualquier error del
sistema con un solo except, o uno específico cuando necesitemos más detalle.
"""


class SoftwareFJError(Exception):
    """Excepción base: de ella salen todos los errores del sistema."""

    def __init__(self, mensaje: str, codigo: str = "FJ-000"):
        # Le pasamos el mensaje a Exception para que Python lo maneje normal
        super().__init__(mensaje)
        # Guardamos un código para reconocer el tipo de error en el log
        self.codigo = codigo
        # Guardamos el mensaje aparte para poder usarlo sin el código
        self.mensaje = mensaje

    def __str__(self) -> str:
        # Así se ve el error al imprimirlo: [CODIGO] mensaje
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoError(SoftwareFJError):
    """Se usa cuando algún dato del cliente no pasa las validaciones."""

    def __init__(self, mensaje: str):
        # FJ-101 identifica los errores de datos del cliente
        super().__init__(mensaje, "FJ-101")


class ParametroFaltanteError(SoftwareFJError):
    """Se usa cuando falta un dato obligatorio."""

    def __init__(self, mensaje: str):
        # FJ-102 identifica los parámetros que no llegaron
        super().__init__(mensaje, "FJ-102")


class ServicioInvalidoError(SoftwareFJError):
    """Se usa cuando un servicio se crea con valores equivocados."""

    def __init__(self, mensaje: str):
        # FJ-201 identifica los errores al crear o validar servicios
        super().__init__(mensaje, "FJ-201")


class ServicioNoDisponibleError(SoftwareFJError):
    """Se usa cuando se quiere reservar un servicio que no está disponible."""

    def __init__(self, mensaje: str):
        # FJ-202 identifica los servicios no disponibles
        super().__init__(mensaje, "FJ-202")


class CalculoInconsistenteError(SoftwareFJError):
    """Se usa cuando un cálculo de costos da un resultado que no tiene sentido."""

    def __init__(self, mensaje: str):
        # FJ-203 identifica los errores de cálculo
        super().__init__(mensaje, "FJ-203")


class ReservaInvalidaError(SoftwareFJError):
    """Se usa cuando una reserva no se puede crear o procesar."""

    def __init__(self, mensaje: str):
        # FJ-301 identifica los errores de reservas
        super().__init__(mensaje, "FJ-301")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se usa cuando la operación no se puede hacer en el estado actual."""

    def __init__(self, mensaje: str):
        # FJ-302 identifica las operaciones que el estado no permite
        super().__init__(mensaje, "FJ-302")
