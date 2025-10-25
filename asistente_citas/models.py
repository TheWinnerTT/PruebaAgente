"""Model definitions for the Asistente de Citas agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True)
class UserProfile:
    """Stores the personal data required to complete a booking."""

    full_name: str
    rut: str
    email: str
    phone: str
    date_of_birth: str
    snabb_password: str

    def patient_payload(self) -> Dict[str, str]:
        """Return the payload expected by ``book_appointment``.

        The Snabb booking API expects the patient data broken down into
        individual fields.  Snabb does not specify how names should be split,
        so we apply a defensive strategy that keeps as much information as
        possible while still providing ``firstName`` and ``lastName`` keys.
        """

        names = [part for part in self.full_name.strip().split() if part]
        first_name = names[0] if names else ""
        last_name = " ".join(names[1:]) if len(names) > 1 else ""

        return {
            "firstName": first_name,
            "lastName": last_name,
            "rut": self.rut,
            "email": self.email,
            "phone": self.phone,
            "dateOfBirth": self.date_of_birth,
        }


@dataclass(slots=True)
class Specialist:
    """Represents a doctor or speciality result returned by Snabb."""

    id: str
    name: str
    details: str | None = None


@dataclass(slots=True)
class Slot:
    """Encapsulates an available appointment slot."""

    slot_id: str
    datetime: str
    doctor_name: str
    location: str | None = None


@dataclass(slots=True)
class BookingConfirmation:
    """Represents the response returned by ``book_appointment``."""

    id: str
    details: str | None = None
    message: str | None = None
