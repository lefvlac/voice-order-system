from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request
)

from app.config import VONAGE_EVENT_URL
from app.services.whisper_service import handle_call


router = APIRouter(
    tags=["Vonage"]
)

processed_uuids: set[str] = set()
call_metadata: dict[str, dict[str, str]] = {}


@router.get("/vonage-answer")
async def vonage_answer(request: Request):

    conversation_uuid = request.query_params.get(
        "conversation_uuid",
        ""
    )

    customer_phone = request.query_params.get(
        "from",
        "Unknown"
    )

    called_number = request.query_params.get(
        "to",
        ""
    )

    if conversation_uuid:
        call_metadata[conversation_uuid] = {
            "customer_phone": customer_phone,
            "called_number": called_number
        }

    return [
        {
            "action": "talk",
            "text": (
                "Παρακαλώ πείτε την παραγγελία σας "
                "μετά τον χαρακτηριστικό ήχο."
            ),
            "language": "el-GR"
        },
        {
            "action": "record",
            "eventUrl": [
                VONAGE_EVENT_URL
            ],
            "beepStart": True,
            "format": "wav",
            "endOnSilence": 3,
            "maxDuration": 15
        }
    ]

@router.post("/vonage-event")
async def vonage_event_handler(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Λαμβάνει το webhook της Vonage μετά
    την ολοκλήρωση της ηχογράφησης.

    Η επεξεργασία της κλήσης εκτελείται
    στο παρασκήνιο, ώστε το webhook να
    απαντήσει άμεσα στη Vonage.
    """

    event_data = await request.json()

    conversation_uuid = event_data.get(
        "conversation_uuid"
    )
    metadata = call_metadata.get(
        conversation_uuid,
        {}
    )
    customer_phone = metadata.get(
        "customer_phone",
        event_data.get("from", "Unknown")
    )
    called_number = metadata.get(
       "called_number",
        event_data.get("to", "")
    )
    
    recording_url = event_data.get(
        "recording_url"
    )

    
    print("📞 Customer phone:", customer_phone)
    print("🏪 Called Vonage number:", called_number)

    if not recording_url:
        return {
            "status": "ok",
            "message": (
                "Το event δεν περιείχε "
                "recording_url."
            )
        }

    if (
        conversation_uuid
        and conversation_uuid in processed_uuids
    ):
        return {
            "status": "already_processed"
        }

    if conversation_uuid:
        processed_uuids.add(
            conversation_uuid
        )

    background_tasks.add_task(
        handle_call,
        recording_url,
        customer_phone,
        called_number
    )

    return {
        "status": "processing_started"
    }