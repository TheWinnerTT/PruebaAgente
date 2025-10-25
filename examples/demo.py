"""Demostración interactiva mínima del asistente de citas.

Este script usa implementaciones "dummy" de las herramientas de Snabb para
mostrar cómo orquestar el flujo completo con :class:`AsistenteDeCitas`.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from asistente_citas import AsistenteDeCitas, UserProfile


# ---------------------------------------------------------------------------
# Implementaciones de ejemplo de las herramientas de Snabb
# ---------------------------------------------------------------------------

def login_snabb(*, rut: str, password: str) -> str:
    print(f"[login_snabb] Autenticando al RUT {rut}...")
    if not rut or not password:
        raise ValueError("Se requieren rut y password para iniciar sesión")
    return "dummy-token"


def find_specialist(*, authToken: str, query: str) -> List[Dict[str, Any]]:
    print(f"[find_specialist] Buscando especialistas que coincidan con '{query}'")
    if authToken != "dummy-token":
        raise ValueError("Token inválido")
    return [
        {"id": "1", "name": "Dra. Ana Cardióloga", "details": "Cardiología adultos"},
        {"id": "2", "name": "Dr. Luis Cardiólogo", "details": "Cardiología pediátrica"},
    ]


def get_available_slots(
    *, authToken: str, specialistId: str, startDate: str, endDate: str
) -> List[Dict[str, Any]]:
    print(
        "[get_available_slots] Obteniendo horarios del especialista",
        specialistId,
        "entre",
        startDate,
        "y",
        endDate,
    )
    if authToken != "dummy-token":
        raise ValueError("Token inválido")

    base = datetime.now().replace(minute=0, second=0, microsecond=0)
    return [
        {
            "slotId": f"{specialistId}-slot-{idx}",
            "datetime": (base + timedelta(days=idx, hours=9)).isoformat() + "Z",
            "doctorName": f"Doctor #{specialistId}",
            "location": "Clínica Central",
        }
        for idx in range(3)
    ]


def book_appointment(*, authToken: str, slotId: str, patientData: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[book_appointment] Reservando slot {slotId} para {patientData['firstName']}")
    if authToken != "dummy-token":
        raise ValueError("Token inválido")
    return {
        "id": f"booking-{slotId}",
        "details": f"Reserva confirmada para {patientData['firstName']} {patientData['lastName']}",
        "message": "Recibirás un correo con los detalles de la cita.",
    }


# ---------------------------------------------------------------------------
# Flujo principal
# ---------------------------------------------------------------------------

def main() -> None:
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
    chosen_specialist = specialists[0]
    print("Especialista seleccionado:", chosen_specialist)

    slots = agent.fetch_available_slots(chosen_specialist.id, "2024-07-01", "2024-07-31")
    suggestions = agent.suggest_slots(slots)
    chosen_slot = suggestions[0]
    print("Slot sugerido:", chosen_slot)

    confirmation = agent.book_slot(chosen_slot.slot_id)
    print("Confirmación recibida:", confirmation)


if __name__ == "__main__":
    main()
