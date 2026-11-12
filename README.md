
# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto del curso **Programación (213023)** – UNAD, Fase 4.

Es una aplicación hecha en Python 3 con programación orientada a objetos. No usa base de datos: todo
se maneja con objetos y listas en memoria, y el único archivo que se escribe es el registro de
eventos y errores (`logs/software_fj.log`).

## Cómo ejecutarlo
```bash
python main.py
```
Necesita Python 3.8 o superior. No hay que instalar nada extra (solo biblioteca estándar).

## Qué hay en cada archivo
| Archivo | Qué contiene |
|---|---|
| `excepciones.py` | Las excepciones propias del sistema (`SoftwareFJError` y las que heredan de ella) |
| `registro_logs.py` | Configuración del archivo de logs |
| `entidades.py` | Clase abstracta `EntidadBase` y clase `Cliente` |
| `servicios.py` | Clase abstracta `Servicio` y sus tres hijas: `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` |
| `reserva.py` | Clase `Reserva` (confirmar, cancelar y procesar) |
| `main.py` | Simulación de 12 operaciones (más la 7b), unas válidas y otras con errores a propósito |

## Conceptos que aplicamos
- **Abstracción:** `EntidadBase` y `Servicio` son clases abstractas (usan `ABC`).
- **Herencia y polimorfismo:** los tres servicios sobrescriben `calcular_costo`, `validar_parametros` y `describir`.
- **Encapsulación:** los datos del cliente son privados y se validan en los setters.
- **Sobrecarga:** `calcular_costo_total(horas, impuesto=None, descuento=None)` se puede llamar de varias formas (solo con IVA, con otro impuesto, con descuento numérico o en texto como `"10%"`).
- **Excepciones:** personalizadas, con `try/except`, `try/except/else`, `try/except/finally` y encadenamiento (`raise ... from ...`).
- **Estabilidad:** `GestorFJ.ejecutar` aísla cada operación, así un error nunca detiene el programa.

## Integrantes
- Integrante 1 – (Jhon Lopez Ortiz)
- Integrante 2 – (Sherol Natalia Oviedo León)
- Integrante 3 – (Andrey Yair Maldonado)
- Integrante 4 – (módulo a cargo)
- Integrante 5 – (módulo a cargo)
