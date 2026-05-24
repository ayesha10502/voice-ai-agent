from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging

from app.schemas.call import (
    InitiateCallRequest,
    InitiateCallResponse,
    CallStatusResponse,
    CallStatus,
)
from app.services.vapi_service import vapi_service, VapiError
from app.models.call_store import call_store, CallRecord
from app.core.scenarios import get_scenario

router = APIRouter(prefix="/calls", tags=["calls"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=InitiateCallResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate an outbound call",
)
async def initiate_call(payload: InitiateCallRequest):
    """
    Trigger an outbound AI voice call to the given phone number
    using the specified scenario.
    """
    scenario = get_scenario(payload.scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario '{payload.scenario_id}'. "
                   "Use GET /api/scenarios to list available scenarios.",
        )

    # Basic E.164 validation
    phone = payload.phone_number.strip()
    if not phone.startswith("+") or len(phone) < 8:
        raise HTTPException(
            status_code=422,
            detail="Phone number must be in E.164 format, e.g. +12025551234",
        )

    try:
        vapi_call = await vapi_service.initiate_call(
            phone_number=phone,
            scenario_id=payload.scenario_id,
            customer_name=payload.customer_name,
            additional_context=payload.additional_context,
        )
    except VapiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    call_id = vapi_call.get("id", "unknown")
    record = CallRecord(
        call_id=call_id,
        phone_number=phone,
        scenario_id=payload.scenario_id,
        scenario_name=scenario["name"],
        agent_name=scenario["agent"]["name"],
    )
    record.status = CallStatus.RINGING
    call_store.save(record)

    logger.info(f"Call initiated: {call_id} → {phone} [{payload.scenario_id}]")

    return InitiateCallResponse(
        call_id=call_id,
        status=CallStatus.RINGING,
        phone_number=phone,
        scenario_id=payload.scenario_id,
        scenario_name=scenario["name"],
        agent_name=scenario["agent"]["name"],
        message=f"{scenario['agent']['name']} is calling {phone} now.",
        initiated_at=datetime.utcnow(),
    )


@router.get(
    "/{call_id}",
    response_model=CallStatusResponse,
    summary="Get call status",
)
async def get_call_status(call_id: str):
    """
    Fetch the current status of a call.
    Tries the local store first, then falls back to Vapi's API.
    """
    local = call_store.get(call_id)

    # Try to get fresh data from Vapi
    try:
        vapi_data = await vapi_service.get_call(call_id)
        vapi_status_raw = vapi_data.get("status", "unknown")

        # Map Vapi statuses → our enum
        status_map = {
            "queued": CallStatus.PENDING,
            "ringing": CallStatus.RINGING,
            "in-progress": CallStatus.IN_PROGRESS,
            "forwarding": CallStatus.IN_PROGRESS,
            "ended": CallStatus.COMPLETED,
        }
        mapped_status = status_map.get(vapi_status_raw, CallStatus.IN_PROGRESS)

        ended_reason = vapi_data.get("endedReason")
        duration = vapi_data.get("duration")
        summary = (vapi_data.get("analysis") or {}).get("summary")

        if local:
            call_store.update_status(
                call_id,
                mapped_status,
                ended_reason=ended_reason,
                duration_seconds=int(duration) if duration else None,
                summary=summary,
            )
            record = call_store.get(call_id)
        else:
            # Build a transient record from Vapi data
            return CallStatusResponse(
                call_id=call_id,
                status=mapped_status,
                phone_number=vapi_data.get("customer", {}).get("number", "unknown"),
                scenario_id="unknown",
                ended_reason=ended_reason,
                duration_seconds=int(duration) if duration else None,
                summary=summary,
            )

    except VapiError:
        if not local:
            raise HTTPException(status_code=404, detail=f"Call {call_id} not found")
        record = local

    return CallStatusResponse(
        call_id=record.call_id,
        status=record.status,
        phone_number=record.phone_number,
        scenario_id=record.scenario_id,
        duration_seconds=record.duration_seconds,
        ended_reason=record.ended_reason,
        summary=record.summary,
        created_at=record.created_at,
        ended_at=record.ended_at,
    )


@router.delete(
    "/{call_id}",
    summary="End an active call",
)
async def end_call(call_id: str):
    """Terminate an active call."""
    try:
        result = await vapi_service.end_call(call_id)
    except VapiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    call_store.update_status(call_id, CallStatus.CANCELLED)
    return result


@router.get(
    "",
    response_model=list[CallStatusResponse],
    summary="List all calls",
)
async def list_calls():
    """Return all calls tracked in the local store."""
    records = call_store.list_all()
    return [
        CallStatusResponse(
            call_id=r.call_id,
            status=r.status,
            phone_number=r.phone_number,
            scenario_id=r.scenario_id,
            duration_seconds=r.duration_seconds,
            ended_reason=r.ended_reason,
            summary=r.summary,
            created_at=r.created_at,
            ended_at=r.ended_at,
        )
        for r in records
    ]
