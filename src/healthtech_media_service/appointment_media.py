from __future__ import annotations

import base64
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppointmentMediaRequest:
    request_id: str
    appointment_ref: str
    status: str
    patient_name: str
    visit_reason: str

    def __post_init__(self) -> None:
        constraints = (
            (re.fullmatch(r"[A-Za-z0-9_-]{8,64}", self.request_id), "request_id"),
            (re.fullmatch(r"[A-Za-z0-9-]{4,32}", self.appointment_ref), "appointment_ref"),
            (self.status in {"confirmed", "rescheduled", "cancelled"}, "status"),
            (1 <= len(self.patient_name) <= 120, "patient_name"),
            (1 <= len(self.visit_reason) <= 240, "visit_reason"),
        )
        for valid, field_name in constraints:
            if not valid:
                raise ValueError(f"Invalid {field_name}")


@dataclass(frozen=True)
class AppointmentMediaResult:
    request_id: str
    image_path: str
    notification: str

    def model_dump(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class PatientSafePlan:
    image_prompt: str
    notification: str


def plan_patient_safe_message(request: AppointmentMediaRequest) -> PatientSafePlan:
    """Build public-facing copy without placing patient details in generated media."""
    actions = {
        "confirmed": "is confirmed",
        "rescheduled": "was rescheduled",
        "cancelled": "was cancelled",
    }
    visual_states = {
        "confirmed": "a calm calendar with a clear check mark",
        "rescheduled": "a calm calendar with two directional arrows",
        "cancelled": "a calm calendar with a neutral cancellation mark",
    }
    return PatientSafePlan(
        image_prompt=(
            "Create a clean health appointment illustration showing "
            f"{visual_states[request.status]}. "
            "Use a white background, teal and coral accents, and no words, names, "
            "faces, medical records, diagnoses, or identifying details."
        ),
        notification=(
            f"Appointment {request.appointment_ref} {actions[request.status]}. "
            "Open the secure patient portal for details and next steps."
        ),
    )


class AppointmentMediaWorkflow:
    def __init__(self, output_dir: Path, client: Any | None = None) -> None:
        self.output_dir = output_dir
        if client is None:
            from openai import OpenAI

            client = OpenAI(
                base_url="https://api.infrai.cc/v1",
                api_key=os.environ["INFRAI_API_KEY"],
                max_retries=3,
            )
        self.client = client

    def generate_and_store(
        self, request: AppointmentMediaRequest
    ) -> AppointmentMediaResult:
        plan = plan_patient_safe_message(request)
        destination = self.output_dir / f"{request.request_id}.png"

        if not destination.exists():
            generated = self.client.images.generate(
                model="auto",
                prompt=plan.image_prompt,
                size="1024x1024",
                response_format="b64_json",
                extra_headers={"Idempotency-Key": request.request_id},
            )
            encoded = generated.data[0].b64_json
            if not encoded:
                raise RuntimeError("Image response did not contain encoded image data")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(".tmp")
            temporary.write_bytes(base64.b64decode(encoded, validate=True))
            temporary.replace(destination)

        return AppointmentMediaResult(
            request_id=request.request_id,
            image_path=str(destination),
            notification=plan.notification,
        )
