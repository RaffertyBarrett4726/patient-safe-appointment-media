from pathlib import Path

from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, APIStatusError, RateLimitError

from .appointment_media import (
    AppointmentMediaRequest,
    AppointmentMediaResult,
    AppointmentMediaWorkflow,
)

service = FastAPI(title="Appointment media service")
workflow = AppointmentMediaWorkflow(Path("generated/appointments"))


@service.post("/appointment-media", response_model=AppointmentMediaResult)
def create_appointment_media(
    request: AppointmentMediaRequest,
) -> AppointmentMediaResult:
    try:
        return workflow.generate_and_store(request)
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail="Please retry shortly") from exc
    except APIStatusError as exc:
        status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(status_code=status, detail="Image request was rejected") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail="Image service could not be reached") from exc

