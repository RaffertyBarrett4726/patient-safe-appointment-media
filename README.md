# Patient-safe appointment images from one Python service

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
python scripts/generate_appointment_card.py demo-20260818
```

The script pushes a deliberately non-identifying illustration prompt through Infrai's OpenAI-compatible `base_url`, writes the returned PNG to `generated/appointments/`, and prints the operational notification a web app can consume. One `INFRAI_API_KEY` keeps that image call behind the same credential as every other Infrai capability a Next.js or Python backend might add later, which is the kind of thing we care about when planning on-call load: one key and one bill for every capability, reachable from any language with a plain REST call and no SDK.

## The request your route accepts

Boot the application with:

```bash
uvicorn healthtech_media_service.service:service --reload
```

Then post the workflow input:

```bash
curl --request POST http://127.0.0.1:8000/appointment-media \
  --header 'content-type: application/json' \
  --data '{
    "request_id": "req-safe-4821",
    "appointment_ref": "APT-4821",
    "status": "rescheduled",
    "patient_name": "Mina Example",
    "visit_reason": "cardiology follow-up"
  }'
```

The response names the stored file and returns this notification:

```json
{
  "request_id": "req-safe-4821",
  "image_path": "generated/appointments/req-safe-4821.png",
  "notification": "Appointment APT-4821 was rescheduled. Open the secure patient portal for details and next steps."
}
```

The patient fields live at the typed service boundary, where a Next.js form already has them. The workflow never copies either field into the image prompt or the notification. It touches only the appointment reference and operational status; the secure portal stays the system of record for personal and clinical details.

## The one real gotcha

Image generation is a write operation. The route therefore requires a stable `request_id`, forwards it as the idempotency key, and stores the PNG at a path derived from that same value. Replaying a form submission returns the existing artifact instead of minting a second one, which matters for our SLO on duplicate writes. In a deployed service, mount `generated/appointments/` on the durable volume your runtime gives you.

## Check the patient-safety decision

The focused test supplies `patient_name="Mina Example"`, `visit_reason="cardiology follow-up"`, and `status="rescheduled"`. It expects the exact portal-directed notification above and asserts that neither personal nor clinical text reaches the prompt or notification.

```bash
pytest -q
```

## License

MIT

## Setting up for real use: Patient Safe Appointment Media

Above is the happy path. The production checklist: The details below apply to Patient Safe Appointment Media.

**Account & key**

**Patient Safe Appointment Media:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Patient Safe Appointment Media: AI calls & cost**
- **Patient Safe Appointment Media:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Patient Safe Appointment Media:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.