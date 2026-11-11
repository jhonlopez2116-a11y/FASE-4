"""
entidades.py
Contiene la clase abstracta EntidadBase y la clase Cliente.
El cliente guarda sus datos de forma privada y los valida cada vez que cambian.
"""

import re                         # expresiones regulares para validar texto
from abc import ABC, abstractmethod  # para crear clases abstractas
from itertools import count       # contador para generar ids únicos

from excepciones import ClienteInvalidoError, ParametroFaltanteError
from registro_logs import logger


class EntidadBase(ABC):
    """Clase abstracta: representa cualquier cosa que maneje el sistema."""

    # Un solo contador compartido: así ningún id se repite entre clientes, servicios o reservas
    _contador_id = count(1)

    def __init__(self):
        # Cada objeto recibe el siguiente número disponible como id
        self._id = next(EntidadBase._contador_id)

    @property
    def id(self) -> int:
        """El id solo se puede leer, nadie puede cambiarlo desde afuera."""
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Cada clase hija debe explicar cómo se describe (polimorfismo)."""

    def __str__(self) -> str:
        # Al imprimir cualquier entidad se muestra su descripción
        return self.describir()


class Cliente(EntidadBase):
    """Cliente de Software FJ, con datos privados y validados."""

    # Patrón sencillo para revisar que el correo tenga forma de correo
    _PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")

    def __init__(self, nombre=None, documento=None, correo=None, telefono=None):
        # Primero se genera el id en la clase padre
        super().__init__()
        # Armamos la lista de datos que llegaron vacíos o sin enviar
        faltantes = [n for n, v in (("nombre", nombre), ("documento", documento),
                                    ("correo", correo), ("telefono", telefono))
                     if v is None or str(v).strip() == ""]
        # Si falta alguno, avisamos cuáles son antes de seguir
        if faltantes:
            raise ParametroFaltanteError(
                f"Faltan datos obligatorios del cliente: {', '.join(faltantes)}")
        # Cada asignación pasa por su setter, y ahí se valida el dato
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        # Lista privada con las reservas que ha hecho este cliente
        self.__historial = []
        # Dejamos constancia en el log de que el cliente se creó bien
        logger.info(f"Cliente creado: id={self.id}, nombre={self.nombre}")

    # ---------- nombre ----------
    @property
    def nombre(self) -> str:
        # Devuelve el nombre guardado
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        # El nombre tiene que ser texto
        if not isinstance(valor, str):
            raise ClienteInvalidoError("El nombre debe ser texto.")
        # Quitamos espacios sobrantes al inicio y al final
        valor = valor.strip()
        # Mínimo 3 caracteres y solo letras (con tildes y ñ) o espacios
        if len(valor) < 3 or not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+", valor):
            raise ClienteInvalidoError(
                f"Nombre inválido: '{valor}'. Use solo letras (mínimo 3).")
        # Guardamos con la primera letra de cada palabra en mayúscula
        self.__nombre = valor.title()

    # ---------- documento ----------
    @property
    def documento(self) -> str:
        # Devuelve el documento guardado
        return self.__documento

    @documento.setter
    def documento(self, valor):
        # Lo pasamos a texto y quitamos espacios
        valor = str(valor).strip()
        try:
            # Si int() falla, el documento tiene letras o símbolos
            numero = int(valor)
        except ValueError as causa:
            # Con "from causa" guardamos el error original dentro del nuestro
            raise ClienteInvalidoError(
                f"El documento '{valor}' debe ser numérico.") from causa
        # El documento debe tener entre 6 y 12 dígitos y ser positivo
        if not 6 <= len(valor) <= 12 or numero <= 0:
            raise ClienteInvalidoError(
                f"El documento '{valor}' debe tener entre 6 y 12 dígitos.")
        # Si todo está bien, lo guardamos
        self.__documento = valor

    # ---------- correo ----------
    @property
    def correo(self) -> str:
        # Devuelve el correo guardado
        return self.__correo

    @correo.setter
    def correo(self, valor):
        # Lo dejamos en minúsculas y sin espacios para que sea uniforme
        valor = str(valor).strip().lower()
        # Si no encaja con el patrón, no es un correo válido
        if not self._PATRON_CORREO.match(valor):
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        # Si es válido, lo guardamos
        self.__correo = valor

    # ---------- teléfono ----------
    @property
    def telefono(self) -> str:
        # Devuelve el teléfono guardado
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        # Lo pasamos a texto y quitamos espacios
        valor = str(valor).strip()
        # Solo dígitos, entre 7 y 10
        if not valor.isdigit() or not 7 <= len(valor) <= 10:
            raise ClienteInvalidoError(
                f"Teléfono inválido: '{valor}'. Debe tener entre 7 y 10 dígitos.")
        # Si cumple, lo guardamos
        self.__telefono = valor

    # ---------- historial ----------
    @property
    def historial(self) -> tuple:
        """Entrega una copia en tupla para que nadie modifique la lista original."""
        return tuple(self.__historial)

    def agregar_a_historial(self, reserva) -> None:
        """Guarda una reserva en el historial del cliente."""
        self.__historial.append(reserva)

    def describir(self) -> str:
        # Una sola línea con todos los datos del cliente
        return (f"Cliente #{self.id} | {self.nombre} | Doc: {self.documento} | "
                f"{self.correo} | Tel: {self.telefono}")
