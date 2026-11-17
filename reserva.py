"""
reserva.py
Clase Reserva: une a un cliente con un servicio, por una cantidad de horas.
Maneja su estado (pendiente, confirmada, procesada o cancelada) y usa
try/except, try/except/else, try/except/finally y encadenamiento de errores.
"""

from entidades import Cliente, EntidadBase
from excepciones import (CalculoInconsistenteError, OperacionNoPermitidaError,
                         ReservaInvalidaError, ServicioInvalidoError,
                         ServicioNoDisponibleError, SoftwareFJError)
from registro_logs import logger
from servicios import Servicio


class Reserva(EntidadBase):
    """Reserva de un servicio hecha por un cliente."""

    # Los cuatro estados por los que puede pasar una reserva
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"

    def __init__(self, cliente, servicio, horas):
        # El id se genera en la clase padre
        super().__init__()
        # Revisamos que el cliente sea realmente un Cliente
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido.")
        # Y que el servicio sea realmente un Servicio
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido.")
        # No se puede reservar algo que no está disponible
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible.")
        try:
            # Cada servicio revisa las horas con su propia regla (polimorfismo)
            servicio.validar_parametros(horas)
        except ServicioInvalidoError as causa:
            # Cambiamos a un error de reserva, pero sin perder la causa original
            raise ReservaInvalidaError(
                f"Duración inválida para la reserva: {causa.mensaje}") from causa
        # Si todo salió bien, guardamos los datos de la reserva
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        # Toda reserva nueva empieza como pendiente
        self._estado = self.PENDIENTE
        # Todavía no hay costo final, se calcula al procesar
        self._costo_final = None
        # Agregamos la reserva al historial del cliente
        cliente.agregar_a_historial(self)
        # Dejamos constancia en el log
        logger.info(f"Reserva #{self.id} creada: {cliente.nombre} -> "
                    f"{servicio.nombre} ({horas} h)")

    @property
    def estado(self) -> str:
        # Estado actual de la reserva
        return self._estado

    @property
    def costo_final(self):
        # Costo final (None hasta que se procese)
        return self._costo_final

    def confirmar(self) -> None:
        """Pasa la reserva de PENDIENTE a CONFIRMADA."""
        # Solo se confirma lo que está pendiente
        if self._estado != self.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self._estado}.")
        # Revisamos otra vez que el servicio siga disponible
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' dejó de estar disponible.")
        # Cambiamos el estado
        self._estado = self.CONFIRMADA
        # Lo anotamos en el log
        logger.info(f"Reserva #{self.id} confirmada.")

    def cancelar(self) -> None:
        """Cancela la reserva mientras no esté procesada ni cancelada."""
        # Si ya está procesada o cancelada, no se puede cancelar
        if self._estado in (self.PROCESADA, self.CANCELADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva en estado {self._estado}.")
        # Cambiamos el estado
        self._estado = self.CANCELADA
        # Lo anotamos en el log
        logger.info(f"Reserva #{self.id} cancelada.")

    def procesar(self, impuesto=None, descuento=None):
        """
        Calcula el costo final y cierra la reserva.
        Aquí usamos try/except/else/finally y el encadenamiento de excepciones.
        """
        try:
            # Solo se procesan reservas que ya estén confirmadas
            if self._estado != self.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se procesan reservas CONFIRMADAS (actual: {self._estado}).")
            # Pedimos el costo total al servicio (con impuesto y descuento opcionales)
            costo = self._servicio.calcular_costo_total(self._horas, impuesto, descuento)
        except CalculoInconsistenteError as causa:
            # Convertimos el error de cálculo en un error de reserva, guardando la causa
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva #{self.id}: {causa.mensaje}") from causa
        except SoftwareFJError:
            # Cualquier otro error del sistema lo dejamos pasar tal como está
            raise
        else:
            # El else solo corre si NO hubo errores: aquí se cierra la reserva
            self._costo_final = costo
            self._estado = self.PROCESADA
            # Lo anotamos en el log con el total
            logger.info(f"Reserva #{self.id} procesada. Total: ${costo:,.2f}")
            return costo
        finally:
            # El finally corre siempre, haya o no error
            logger.debug(f"Fin de intento de procesamiento de reserva #{self.id} "
                         f"(estado: {self._estado})")

    def describir(self) -> str:
        # Si ya hay costo lo mostramos; si no, ponemos una raya
        total = f"${self._costo_final:,.2f}" if self._costo_final else "—"
        # Resumen de la reserva en una línea
        return (f"Reserva #{self.id} | {self._cliente.nombre} | "
                f"{self._servicio.nombre} | {self._horas} h | "
                f"{self._estado} | Total: {total}")
