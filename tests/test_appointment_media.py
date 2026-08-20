from healthtech_media_service.appointment_media import (
    AppointmentMediaRequest,
    plan_patient_safe_message,
)


def test_reschedule_copy_excludes_patient_and_clinical_details() -> None:
    request = AppointmentMediaRequest(
        request_id="req-safe-4821",
        appointment_ref="APT-4821",
        status="rescheduled",
        patient_name="Mina Example",
        visit_reason="cardiology follow-up",
    )

    plan = plan_patient_safe_message(request)

    assert plan.notification == (
        "Appointment APT-4821 was rescheduled. "
        "Open the secure patient portal for details and next steps."
    )
    combined = f"{plan.notification} {plan.image_prompt}".lower()
    assert "mina example" not in combined
    assert "cardiology" not in combined

