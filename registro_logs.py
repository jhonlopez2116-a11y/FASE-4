"""
registro_logs.py
Configura el archivo de logs donde queda el registro de eventos y errores.
Es lo único que el programa guarda en un archivo (no usamos base de datos).
"""

import logging  # librería estándar para registrar eventos
import os       # para armar rutas y crear la carpeta de logs

# La carpeta "logs" queda junto a este archivo, sin importar desde dónde se ejecute
DIRECTORIO_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
# Ruta completa del archivo donde se escribe todo
ARCHIVO_LOG = os.path.join(DIRECTORIO_LOGS, "software_fj.log")


def obtener_logger() -> logging.Logger:
    """Devuelve el logger del sistema y lo configura solo la primera vez."""
    # Si la carpeta no existe, la creamos para evitar un error al abrir el archivo
    os.makedirs(DIRECTORIO_LOGS, exist_ok=True)
    # Pedimos el logger por nombre; si ya existe, Python devuelve el mismo
    logger = logging.getLogger("software_fj")
    # Si ya tiene un manejador, ya se configuró antes y no repetimos el proceso
    if logger.handlers:
        return logger
    # Registramos desde el nivel más bajo (DEBUG) hacia arriba
    logger.setLevel(logging.DEBUG)
    # Cada línea del log muestra fecha y hora, nivel y mensaje
    formato = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s",
                                "%Y-%m-%d %H:%M:%S")
    # El manejador escribe en el archivo; UTF-8 para que salgan bien las tildes
    manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    # Le asignamos el formato que definimos arriba
    manejador.setFormatter(formato)
    # Conectamos el manejador al logger
    logger.addHandler(manejador)
    # Evitamos que cada mensaje se escriba dos veces
    logger.propagate = False
    # Entregamos el logger ya listo
    return logger


# Creamos el logger una sola vez; los demás módulos lo importan de aquí
logger = obtener_logger()
