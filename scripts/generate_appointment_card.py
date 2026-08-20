import json
import sys
from pathlib import Path

from healthtech_media_service.appointment_media import (
    AppointmentMediaRequest,
    AppointmentMediaWorkflow,
)


def main() -> None:
    request = AppointmentMediaRequest(
        request_id=sys.argv[1] if len(sys.argv) > 1 else "demo-20260818",
        appointment_ref="APT-4821",
        status="rescheduled",
        patient_name="Local demo patient",
        visit_reason="Local demo visit",
    )
    result = AppointmentMediaWorkflow(Path("generated/appointments")).generate_and_store(
        request
    )
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()

