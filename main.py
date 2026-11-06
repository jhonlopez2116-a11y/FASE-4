"""
main.py
Programa principal de Software FJ.
Simula 12 operaciones (algunas válidas y otras con errores a propósito, más la 7b)
para comprobar que el programa no se detiene cuando algo falla y que todo
queda anotado en el archivo de logs.
"""

from entidades import Cliente
from excepciones import SoftwareFJError
from registro_logs import ARCHIVO_LOG, logger
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


class GestorFJ:
    """Guarda en memoria las listas de clientes, servicios y reservas."""

    def __init__(self):
        # Tres listas vacías: aquí vive toda la información (no hay base de datos)
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def ejecutar(self, titulo, operacion):
        """
        Corre una operación de forma aislada: si falla, registra el error
        y el programa sigue con la siguiente.
        """
        # Mostramos el título de la operación en pantalla
        print(f"\n--- {titulo} ---")
        # Anotamos en el log que la operación empezó
        logger.info(f"INICIO operación: {titulo}")
        try:
            # Ejecutamos la operación que nos pasaron
            resultado = operacion()
        except SoftwareFJError as error:
            # Error esperado de nuestro sistema: lo registramos con su causa si la tiene
            causa = f" | causa: {error.__cause__!r}" if error.__cause__ else ""
            logger.error(f"{titulo} -> {error}{causa}")
            # Lo mostramos en pantalla sin que el programa se caiga
            print(f"  [ERROR CONTROLADO] {error}")
            # Si hay un error original encadenado, también lo mostramos
            if error.__cause__:
                print(f"  (causa original: {error.__cause__})")
        except Exception as error:  # por si ocurre algo que no previmos
            # Un error inesperado se registra como crítico
            logger.critical(f"{titulo} -> Error inesperado: {error!r}")
            print(f"  [ERROR INESPERADO] {error!r}")
        else:
            # Si no hubo ningún error, mostramos el resultado
            print(f"  [OK] {resultado}")
        finally:
            # Pase lo que pase, anotamos que la operación terminó
            logger.info(f"FIN operación: {titulo}")


def main():
    # Creamos el gestor que guarda las listas
    g = GestorFJ()
    # Marcamos el inicio en el log
    logger.info("===== INICIO DE LA SIMULACIÓN SOFTWARE FJ =====")

    # --- Operaciones sobre clientes ---
    def op1():  # Cliente válido (el nombre se arregla con mayúsculas)
        c = Cliente("ana maría pérez", "1098765432", "ana.perez@mail.com", "3001234567")
        g.clientes.append(c)
        return c.describir()

    def op2():  # Correo mal escrito
        g.clientes.append(Cliente("Luis Gómez", "1012345678", "luis-correo-malo", "3109876543"))

    def op3():  # Documento con letras (error encadenado)
        g.clientes.append(Cliente("Carlos Ruiz", "ABC123XYZ", "carlos@mail.com", "3205551234"))

    def op4():  # Falta el documento
        g.clientes.append(Cliente("Marta Díaz", None, "marta@mail.com", "3157778899"))

    # --- Operaciones sobre servicios ---
    def op5():  # Sala válida de 25 personas
        s = ReservaSala("Sala Ejecutiva", 50000, 25)
        g.servicios.append(s)
        return s.describir()

    def op6():  # Alquiler válido de 3 portátiles
        s = AlquilerEquipo("Portátil Gamer", 8000, 3)
        g.servicios.append(s)
        return s.describir()

    def op7():  # Nivel de asesoría que no existe
        g.servicios.append(AsesoriaEspecializada("Asesoría Cloud", 70000, "maestro"))

    def op7b():  # Asesoría válida de nivel senior
        s = AsesoriaEspecializada("Asesoría Python", 70000, "senior")
        g.servicios.append(s)
        return s.describir()

    # --- Operaciones sobre reservas ---
    def op8():  # Reserva completa: crear, confirmar y procesar
        r = Reserva(g.clientes[0], g.servicios[0], 3)
        g.reservas.append(r)
        r.confirmar()
        r.procesar(0.19, "10%")  # impuesto del 19 % y descuento escrito como texto
        return r.describir()

    def op9():  # 20 horas en una asesoría (el máximo es 8)
        g.reservas.append(Reserva(g.clientes[0], g.servicios[2], 20))

    def op10():  # Reservar un servicio que no está disponible
        g.servicios[1].disponible = False
        g.reservas.append(Reserva(g.clientes[0], g.servicios[1], 5))

    def op11():  # Descuento del 100 %: el cálculo no tiene sentido
        r = Reserva(g.clientes[0], g.servicios[2], 2)
        g.reservas.append(r)
        r.confirmar()
        r.procesar(descuento=1.0)

    def op12():  # Cancelar y luego intentar confirmar (no se permite)
        g.servicios[1].disponible = True  # volvemos a habilitar el equipo
        r = Reserva(g.clientes[0], g.servicios[1], 10)
        g.reservas.append(r)
        r.cancelar()
        r.confirmar()

    # Lista con el título de cada operación y la función que la ejecuta
    operaciones = [
        ("1. Registro válido de cliente", op1),
        ("2. Registro inválido: correo mal formado", op2),
        ("3. Registro inválido: documento no numérico", op3),
        ("4. Registro inválido: parámetro faltante", op4),
        ("5. Creación válida de sala", op5),
        ("6. Creación válida de alquiler de equipo", op6),
        ("7. Creación inválida de asesoría (nivel)", op7),
        ("7b. Creación válida de asesoría", op7b),
        ("8. Reserva exitosa (confirmar y procesar)", op8),
        ("9. Reserva fallida: horas fuera de rango", op9),
        ("10. Reserva fallida: servicio no disponible", op10),
        ("11. Procesamiento fallido: cálculo inconsistente", op11),
        ("12. Operación no permitida: confirmar reserva cancelada", op12),
    ]
    # Recorremos la lista y ejecutamos cada operación de forma segura
    for titulo, funcion in operaciones:
        g.ejecutar(titulo, funcion)

    # Resumen final: demuestra que el programa siguió funcionando pese a los errores
    print("\n========== RESUMEN FINAL ==========")
    print(f"Clientes registrados : {len(g.clientes)}")
    print(f"Servicios creados    : {len(g.servicios)}")
    print(f"Reservas creadas     : {len(g.reservas)}")
    # Mostramos cada reserva que quedó en la lista
    for r in g.reservas:
        print("  ", r.describir())
    # Le decimos al usuario dónde quedó el registro
    print(f"\nRevise los registros en: {ARCHIVO_LOG}")
    # Marcamos el final en el log
    logger.info("===== FIN DE LA SIMULACIÓN SOFTWARE FJ =====")


# Esto hace que main() solo corra si ejecutamos este archivo directamente
if __name__ == "__main__":
    main()
