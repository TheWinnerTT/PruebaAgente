"""Core logic for the Asistente de Citas agent."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Callable, Iterable, List, Sequence

from .models import BookingConfirmation, Slot, Specialist, UserProfile


class AuthenticationError(RuntimeError):
    """Raised when authentication fails or is required but missing."""


class AsistenteDeCitas:
    """High level orchestration for the Snabb medical booking flow.

    The class wraps the four tools exposed by Snabb's public API.  Each tool is
    injected as a callable so that the agent can be unit tested with doubles
    and used with any transport layer (HTTP, SDK, mocked functions, etc.).
    """

    def __init__(
        self,
        *,
        user_profile: UserProfile,
        login_snabb: Callable[..., str],
        find_specialist: Callable[..., Sequence[dict]],
        get_available_slots: Callable[..., Sequence[dict]],
        book_appointment: Callable[..., dict],
    ) -> None:
        self._user_profile = user_profile
        self._login_snabb = login_snabb
        self._find_specialist = find_specialist
        self._get_available_slots = get_available_slots
        self._book_appointment = book_appointment
        self._auth_token: str | None = None

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    def authenticate(self) -> str:
        """Authenticate the user and cache the resulting token."""

        token = self._login_snabb(rut=self._user_profile.rut, password=self._user_profile.snabb_password)
        if not token:
            raise AuthenticationError("Snabb did not return an authentication token.")

        self._auth_token = token
        return token

    def _require_token(self) -> str:
        if not self._auth_token:
            raise AuthenticationError("The agent must be authenticated before performing this action.")
        return self._auth_token

    # ------------------------------------------------------------------
    # Specialist search and slot retrieval
    # ------------------------------------------------------------------
    def search_specialists(self, query: str) -> List[Specialist]:
        """Return the list of specialists that match *query*."""

        token = self._require_token()
        results = self._find_specialist(authToken=token, query=query)
        specialists = [
            Specialist(id=str(raw.get("id")), name=str(raw.get("name")), details=raw.get("details"))
            for raw in results
        ]
        return specialists

    def fetch_available_slots(self, specialist_id: str, start_date: str, end_date: str) -> List[Slot]:
        """Fetch every available slot for *specialist_id* within the date range."""

        token = self._require_token()
        raw_slots = self._get_available_slots(
            authToken=token,
            specialistId=str(specialist_id),
            startDate=start_date,
            endDate=end_date,
        )
        slots = [
            Slot(
                slot_id=str(raw.get("slotId")),
                datetime=str(raw.get("datetime")),
                doctor_name=str(raw.get("doctorName", "")),
                location=raw.get("location"),
            )
            for raw in raw_slots
        ]
        # Sorting helps suggest the earliest options to the user.
        slots.sort(key=lambda slot: _parse_datetime(slot.datetime))
        return slots

    # ------------------------------------------------------------------
    # Slot suggestion and booking
    # ------------------------------------------------------------------
    def suggest_slots(self, slots: Iterable[Slot], limit: int = 3) -> List[Slot]:
        """Return up to ``limit`` slots sorted by their datetime."""

        if limit <= 0:
            return []

        sorted_slots = sorted(slots, key=lambda slot: _parse_datetime(slot.datetime))
        return sorted_slots[:limit]

    def book_slot(self, slot_id: str) -> BookingConfirmation:
        """Confirm the reservation for *slot_id*."""

        token = self._require_token()
        payload = {
            "authToken": token,
            "slotId": str(slot_id),
            "patientData": self._user_profile.patient_payload(),
        }
        confirmation_data = self._book_appointment(**payload)
        return BookingConfirmation(
            id=str(confirmation_data.get("id")),
            details=confirmation_data.get("details"),
            message=confirmation_data.get("message"),
        )

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    @property
    def user_profile(self) -> UserProfile:
        return self._user_profile

    def asdict(self) -> dict:
        """Expose the agent configuration as a dictionary."""

        return {
            "user_profile": asdict(self._user_profile),
            "is_authenticated": self._auth_token is not None,
        }


def _parse_datetime(value: str) -> datetime:
    """Parse Snabb's ISO formatted strings into :class:`datetime` objects."""

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)
