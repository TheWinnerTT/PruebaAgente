# PruebaAgente

Mi primer agente de IA con Cloudflare.

## Asistente de Citas

El paquete `asistente_citas` implementa un flujo reutilizable para automatizar
reservas médicas en la plataforma Snabb. El asistente orquesta los pasos
requeridos (inicio de sesión, búsqueda de especialistas, consulta de horarios y
reserva) a través de las herramientas expuestas por Snabb.

### Requisitos

- Python 3.10 o superior instalado en tu equipo.
- (Opcional) `pytest` para ejecutar las pruebas automatizadas.

### Pasos para ponerlo en marcha

1. **Clona el repositorio** (o descarga el código).
   ```bash
   git clone https://github.com/<tu-usuario>/PruebaAgente.git
   cd PruebaAgente
   ```

2. **(Opcional) Crea un entorno virtual** para aislar la instalación de Python.
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows usa `.venv\\Scripts\\activate`
   python -m pip install --upgrade pip
   ```

3. **Instala dependencias de desarrollo si quieres correr pruebas**.
   ```bash
   python -m pip install pytest
   ```

> Nota: El paquete no requiere librerías externas para ejecutarse; todo se basa
> en la biblioteca estándar de Python.

4. **Ejecuta el flujo de ejemplo** con herramientas simuladas para validar que
   el asistente funciona de punta a punta.
   ```bash
   python examples/demo.py
   ```

   Verás en la terminal cada paso: autenticación, búsqueda de especialista,
   consulta de horarios y confirmación de la cita.

### Uso rápido en tu propio proyecto

```python
from asistente_citas import AsistenteDeCitas, UserProfile

def login_snabb(**kwargs): ...
def find_specialist(**kwargs): ...
def get_available_slots(**kwargs): ...
def book_appointment(**kwargs): ...

profile = UserProfile(
    full_name="Maria Jose Lopez",
    rut="12.345.678-9",
    email="maria@example.com",
    phone="123456789",
    date_of_birth="1990-05-01",
    snabb_password="secret",
)

agent = AsistenteDeCitas(
    user_profile=profile,
    login_snabb=login_snabb,
    find_specialist=find_specialist,
    get_available_slots=get_available_slots,
    book_appointment=book_appointment,
)

agent.authenticate()
specialists = agent.search_specialists("Cardiología")
slots = agent.fetch_available_slots(specialists[0].id, "2024-07-01", "2024-07-31")
options = agent.suggest_slots(slots)
confirmation = agent.book_slot(options[0].slot_id)
print(confirmation)
```

### Cómo conectarlo con las herramientas reales de Snabb

1. **Completa tu perfil real** con los datos exactos del paciente que se usarán
   en Snabb (nombre completo, RUT, correo, teléfono y fecha de nacimiento).
   El método `patient_payload` divide automáticamente el nombre y apellido.

2. **Implementa cada herramienta** (`login_snabb`, `find_specialist`,
   `get_available_slots`, `book_appointment`) con llamadas a la API oficial de
   Snabb o al SDK que utilices. Respeta la firma de parámetros que ves en el
   ejemplo para que el agente pueda invocarlas sin cambios adicionales.

3. **Autentica primero** llamando a `agent.authenticate()`. El token se guarda en
   la instancia y se reutiliza para las demás operaciones.

4. **Busca especialistas y horarios** con los métodos del agente. Puedes mostrar
   al usuario todas las alternativas o quedarte con algunas usando
   `agent.suggest_slots(slots, limit=3)`.

5. **Reserva la cita seleccionada** con `agent.book_slot(slot_id)` y maneja la
   respuesta `BookingConfirmation` para informar el resultado al usuario final.

### Pruebas

```bash
pytest -q
```

Si configuraste funciones simuladas (como en `tests/`), las pruebas comprobarán
que el flujo del asistente sigue el orden esperado.
