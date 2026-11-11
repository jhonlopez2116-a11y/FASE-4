"""
servicios.py
Clase abstracta Servicio y los tres servicios que heredan de ella:
ReservaSala, AlquilerEquipo y AsesoriaEspecializada.
Cada uno calcula su costo y valida las horas a su manera (polimorfismo).
"""

from abc import abstractmethod  # para marcar métodos que las hijas deben escribir

from entidades import EntidadBase
from excepciones import (CalculoInconsistenteError, ParametroFaltanteError,
                         ServicioInvalidoError)
from registro_logs import logger


class Servicio(EntidadBase):
    """Clase abstracta: lo que tienen en común todos los servicios de la empresa."""

    IVA_POR_DEFECTO = 0.19  # si no nos dan un impuesto, usamos el IVA del 19 %

    def __init__(self, nombre=None, tarifa_hora=None):
        # El id se genera en la clase padre
        super().__init__()
        # Sin nombre no hay servicio
        if nombre is None or str(nombre).strip() == "":
            raise ParametroFaltanteError("El servicio requiere un nombre.")
        # Tampoco puede faltar la tarifa
        if tarifa_hora is None:
            raise ParametroFaltanteError("El servicio requiere una tarifa por hora.")
        # La tarifa debe ser un número mayor que cero (y no un True/False)
        if isinstance(tarifa_hora, bool) or not isinstance(tarifa_hora, (int, float)) \
                or tarifa_hora <= 0:
            raise ServicioInvalidoError(
                f"Tarifa inválida: {tarifa_hora!r}. Debe ser un número mayor que 0.")
        # Guardamos el nombre sin espacios sobrantes
        self._nombre = str(nombre).strip()
        # Guardamos la tarifa como decimal
        self._tarifa_hora = float(tarifa_hora)
        # Al crearse, el servicio queda disponible para reservar
        self._disponible = True

    # ---------- propiedades ----------
    @property
    def nombre(self) -> str:
        # Solo lectura: el nombre no cambia después de crear el servicio
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        # Solo lectura: la tarifa tampoco cambia
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        # Dice si el servicio se puede reservar ahora
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool):
        # Solo aceptamos True o False, cualquier otra cosa es un error
        if not isinstance(valor, bool):
            raise ServicioInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = valor

    # ---------- métodos abstractos ----------
    @abstractmethod
    def calcular_costo(self, horas: float) -> float:
        """Costo base, sin impuestos ni descuentos. Cada hija lo define."""

    @abstractmethod
    def validar_parametros(self, horas: float) -> None:
        """Revisa que las horas tengan sentido para ese servicio."""

    # ---------- método "sobrecargado" ----------
    def calcular_costo_total(self, horas, impuesto=None, descuento=None) -> float:
        """
        Python no tiene sobrecarga real, así que usamos parámetros opcionales
        para tener varias formas de llamar al mismo método:
          calcular_costo_total(2)                    -> costo base + IVA 19 %
          calcular_costo_total(2, 0.05)              -> costo base + impuesto del 5 %
          calcular_costo_total(2, 0.19, 0.10)        -> impuesto y 10 % de descuento
          calcular_costo_total(2, descuento="15%")   -> descuento escrito como texto
        """
        # Primero se validan las horas con la regla de cada servicio
        self.validar_parametros(horas)
        # Si no mandaron impuesto, se usa el IVA por defecto
        impuesto = self.IVA_POR_DEFECTO if impuesto is None else impuesto
        # El descuento puede llegar como texto ("15%")
        if isinstance(descuento, str):
            try:
                # Quitamos el % y lo pasamos a fracción (15 -> 0.15)
                descuento = float(descuento.strip().rstrip("%")) / 100
            except ValueError as causa:
                # Si no se puede leer, lanzamos nuestro error guardando la causa
                raise CalculoInconsistenteError(
                    f"Descuento ilegible: '{descuento}'.") from causa
        # Si no hay descuento, lo tomamos como cero
        descuento = 0.0 if descuento is None else descuento
        # El impuesto debe estar entre 0 y 1
        if not 0 <= impuesto <= 1:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango: {impuesto}.")
        # El descuento va de 0 hasta menos de 1 (un 100 % dejaría el costo en cero)
        if not 0 <= descuento < 1:
            raise CalculoInconsistenteError(
                f"Descuento fuera de rango (0 a <100%): {descuento}.")
        # Costo base según el tipo de servicio
        base = self.calcular_costo(horas)
        # Primero se aplica el descuento y después el impuesto
        total = base * (1 - descuento) * (1 + impuesto)
        # Un total de cero o negativo no tiene sentido
        if total <= 0:
            raise CalculoInconsistenteError(f"El costo calculado no es válido: {total}.")
        # Redondeamos a dos decimales
        return round(total, 2)

    def describir(self) -> str:
        # Escribimos el estado en palabras
        estado = "Disponible" if self._disponible else "No disponible"
        # Datos comunes a todos los servicios
        return f"Servicio #{self.id} | {self.nombre} | ${self.tarifa_hora:,.0f}/h | {estado}"

    @staticmethod
    def _validar_horas(horas, maximo):
        """Validación de horas que comparten las tres clases hijas."""
        # Las horas deben ser un número (y no True/False)
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise ServicioInvalidoError(f"Las horas deben ser numéricas, no {horas!r}.")
        # No se aceptan cero ni negativos
        if horas <= 0:
            raise ServicioInvalidoError("Las horas deben ser mayores que 0.")
        # Cada servicio tiene su tope de horas
        if horas > maximo:
            raise ServicioInvalidoError(
                f"Las horas ({horas}) superan el máximo permitido ({maximo}).")


class ReservaSala(Servicio):
    """Servicio de reserva de salas de reuniones."""

    def __init__(self, nombre=None, tarifa_hora=None, capacidad=None):
        # Nombre y tarifa los valida la clase padre
        super().__init__(nombre, tarifa_hora)
        # La capacidad debe ser un entero positivo
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}.")
        # Guardamos la capacidad (protegida)
        self._capacidad = capacidad
        # Dejamos constancia en el log
        logger.info(f"Servicio creado: Sala '{self.nombre}' (cap. {capacidad})")

    def validar_parametros(self, horas):
        # Una sala se puede reservar máximo 12 horas
        self._validar_horas(horas, 12)

    def calcular_costo(self, horas):
        # Las salas de más de 20 personas tienen un recargo del 15 %
        recargo = 1.15 if self._capacidad > 20 else 1.0
        # Costo = tarifa por horas por recargo
        return self.tarifa_hora * horas * recargo

    def describir(self):
        # Reutilizamos la descripción del padre y le sumamos la capacidad
        return super().describir() + f" | Sala para {self._capacidad} personas"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos (portátiles, proyectores, etc.)."""

    def __init__(self, nombre=None, tarifa_hora=None, cantidad=None):
        # Nombre y tarifa los valida la clase padre
        super().__init__(nombre, tarifa_hora)
        # La cantidad debe ser un entero positivo
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ServicioInvalidoError(f"Cantidad de equipos inválida: {cantidad!r}.")
        # Guardamos la cantidad de equipos
        self._cantidad = cantidad
        # Dejamos constancia en el log
        logger.info(f"Servicio creado: Equipo '{self.nombre}' x{cantidad}")

    def validar_parametros(self, horas):
        # Un equipo se alquila máximo 72 horas (3 días)
        self._validar_horas(horas, 72)

    def calcular_costo(self, horas):
        # El costo crece con las horas y con la cantidad de equipos
        costo = self.tarifa_hora * horas * self._cantidad
        # A eso se le suma un cargo fijo de 20.000 por mantenimiento
        return costo + 20000

    def describir(self):
        # Descripción del padre más la cantidad de equipos
        return super().describir() + f" | {self._cantidad} equipo(s)"


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría con distintos niveles de experiencia."""

    # Cuánto se multiplica la tarifa según el nivel del asesor
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre=None, tarifa_hora=None, nivel=None):
        # Nombre y tarifa los valida la clase padre
        super().__init__(nombre, tarifa_hora)
        # El nivel debe ser texto y estar en la lista de niveles permitidos
        if not isinstance(nivel, str) or nivel.lower() not in self.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel inválido: {nivel!r}. Opciones: {', '.join(self.NIVELES)}.")
        # Guardamos el nivel en minúsculas
        self._nivel = nivel.lower()
        # Dejamos constancia en el log
        logger.info(f"Servicio creado: Asesoría '{self.nombre}' nivel {self._nivel}")

    def validar_parametros(self, horas):
        # Una asesoría dura máximo 8 horas
        self._validar_horas(horas, 8)

    def calcular_costo(self, horas):
        # Tarifa por horas, multiplicada por el factor del nivel
        return self.tarifa_hora * horas * self.NIVELES[self._nivel]

    def describir(self):
        # Descripción del padre más el nivel
        return super().describir() + f" | Nivel {self._nivel}"
