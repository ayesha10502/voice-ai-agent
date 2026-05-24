"""
Vapi sends POST webhooks to this endpoint for call lifecycle events.
Events: call-started, call-ended, transcript, etc.
"""
import logging
from fastapi import APIRouter, Request, Response

from app.models.call_store import call_store
from app.schemas.call import CallStatus

router = APIRouter(prefix="/webhook", tags=["webhook"])
logger = logging.getLogger(__name__)


@router.post("/vapi", summary="Vapi webhook receiver")
async def vapi_webhook(request: Request):
    """
    Receives real-time events from Vapi.
    Configure WEBHOOK_BASE_URL in .env and set serverUrl in Vapi dashboard.
    """
    try:
        body = await request.json()
    except Exception:
        return Response(status_code=400)

    message = body.get("message", {})
    event_type = message.get("type", "")
    call_data = message.get("call", {})
    call_id = call_data.get("id", "")

    logger.info(f"Vapi webhook: type={event_type} call_id={call_id}")

    if event_type == "call-started":
        call_store.update_status(call_id, CallStatus.IN_PROGRESS)

    elif event_type == "call-ended":
        ended_reason = message.get("endedReason", "")
        duration = call_data.get("duration")
        analysis = message.get("analysis", {})
        summary = analysis.get("summary") if analysis else None

        # Map Vapi end reasons to our statuses
        if ended_reason in ("customer-did-not-answer", "no-answer"):
            status = CallStatus.NO_ANSWER
        elif ended_reason in ("customer-ended-call", "assistant-ended-call", "silence-timed-out"):
            status = CallStatus.COMPLETED
        elif ended_reason in ("error", "pipeline-error"):
            status = CallStatus.FAILED
        else:
            status = CallStatus.COMPLETED

        call_store.update_status(
            call_id,
            status,
            ended_reason=ended_reason,
            duration_seconds=int(duration) if duration else None,
            summary=summary,
        )

    elif event_type == "status-update":
        vapi_status = message.get("status", "")
        if vapi_status == "in-progress":
            call_store.update_status(call_id, CallStatus.IN_PROGRESS)

    # Vapi expects a 200 response
    return {"received": True}
