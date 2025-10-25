from __future__ import annotations

from datetime import datetime

import pytest

from asistente_citas import AsistenteDeCitas, BookingConfirmation, Slot, Specialist, UserProfile
from asistente_citas.agent import AuthenticationError


class DummyTools:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def login_snabb(self, *, rut: str, password: str) -> str:
        self.calls.append(("login_snabb", {"rut": rut, "password": password}))
        if password != "secret":
            return ""
        return "token-123"

    def find_specialist(self, *, authToken: str, query: str):
        self.calls.append(("find_specialist", {"authToken": authToken, "query": query}))
        return [
            {"id": 1, "name": "Dra. Ana Pérez", "details": "Cardióloga"},
            {"id": 2, "name": "Cardiología Centro", "details": None},
        ]

    def get_available_slots(self, *, authToken: str, specialistId: str, startDate: str, endDate: str):
        self.calls.append(
            (
                "get_available_slots",
                {
                    "authToken": authToken,
                    "specialistId": specialistId,
                    "startDate": startDate,
                    "endDate": endDate,
                },
            )
        )
        return [
            {
                "slotId": "2",
                "datetime": "2024-07-15T15:30:00",
                "doctorName": "Dra. Ana Pérez",
                "location": "Clínica Central",
            },
            {
                "slotId": "1",
                "datetime": "2024-07-15T09:00:00",
                "doctorName": "Dra. Ana Pérez",
                "location": "Clínica Central",
            },
        ]

    def book_appointment(self, *, authToken: str, slotId: str, patientData: dict):
        self.calls.append(
            (
                "book_appointment",
                {
                    "authToken": authToken,
                    "slotId": slotId,
                    "patientData": patientData,
                },
            )
        )
        return {"id": "bk-1", "details": "Confirmed", "message": "Nos vemos pronto"}


def create_agent() -> tuple[AsistenteDeCitas, DummyTools]:
    tools = DummyTools()
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
        login_snabb=tools.login_snabb,
        find_specialist=tools.find_specialist,
        get_available_slots=tools.get_available_slots,
        book_appointment=tools.book_appointment,
    )
    return agent, tools


def test_authentication_failure():
    agent, _ = create_agent()
    agent.user_profile.snabb_password = "wrong"
    with pytest.raises(AuthenticationError):
        agent.authenticate()


def test_full_booking_flow():
    agent, tools = create_agent()
    token = agent.authenticate()
    assert token == "token-123"

    specialists = agent.search_specialists("cardiologia")
    assert [s.name for s in specialists] == ["Dra. Ana Pérez", "Cardiología Centro"]

    slots = agent.fetch_available_slots("1", "2024-07-10", "2024-07-20")
    assert [slot.slot_id for slot in slots] == ["1", "2"], "Slots must be sorted chronologically"

    suggestions = agent.suggest_slots(slots, limit=1)
    assert len(suggestions) == 1
    assert isinstance(suggestions[0], Slot)
    assert datetime.fromisoformat(suggestions[0].datetime)

    confirmation = agent.book_slot(suggestions[0].slot_id)
    assert isinstance(confirmation, BookingConfirmation)
    assert confirmation.id == "bk-1"

    called_actions = [name for name, _ in tools.calls]
    assert called_actions == [
        "login_snabb",
        "find_specialist",
        "get_available_slots",
        "book_appointment",
    ]


def test_asdict_contains_profile_and_state():
    agent, _ = create_agent()
    data = agent.asdict()
    assert data["user_profile"]["rut"] == "12.345.678-9"
    assert data["is_authenticated"] is False

    agent.authenticate()
    data = agent.asdict()
    assert data["is_authenticated"] is True
