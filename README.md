# PruebaAgente

Mi primer agente de IA con Cloudflare.

## Asistente de Citas

El paquete `asistente_citas` implementa un flujo reutilizable para automatizar
reservas médicas en la plataforma Snabb. El asistente orquesta los pasos
requeridos (inicio de sesión, búsqueda de especialistas, consulta de horarios y
reserva) a través de las herramientas expuestas por Snabb.

### Requisitos

- Python 3.10 o superior.
- (Opcional) `pytest` para ejecutar las pruebas automatizadas.

Se recomienda crear un entorno virtual antes de instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows usa `.venv\Scripts\activate`
python -m pip install --upgrade pip
python -m pip install pytest  # Solo si deseas correr las pruebas
```

> Nota: el paquete en sí no necesita dependencias externas; basta con clonar el
> repositorio y usar Python estándar.

### Ejecutar el flujo de ejemplo

El directorio `examples/` contiene un script de demostración con implementaciones
"dummy" de las herramientas de Snabb. Puedes ejecutarlo directamente para ver el
flujo completo en acción:

```bash
python examples/demo.py
```

El script imprimirá cada paso del proceso (inicio de sesión, búsqueda,
obtención de horarios y reserva) junto con una confirmación final.

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

### Pruebas

```bash
pytest -q
```
