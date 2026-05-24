from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CallStatus(str, Enum):
    PENDING = "pending"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NO_ANSWER = "no-answer"


class InitiateCallRequest(BaseModel):
    phone_number: str = Field(
        ...,
        description="E.164 format phone number, e.g. +12025551234",
        examples=["+12025551234"],
    )
    scenario_id: str = Field(
        ...,
        description="Scenario identifier from the scenarios registry",
        examples=["appointment_reminder"],
    )
    customer_name: Optional[str] = Field(
        None,
        description="Customer's name to personalise the conversation",
        examples=["Jane"],
    )
    additional_context: Optional[str] = Field(
        None,
        description="Extra context injected into the agent's system prompt",
        examples=["Patient has a dog allergy, avoid discussing pets."],
    )


class InitiateCallResponse(BaseModel):
    call_id: str
    status: CallStatus
    phone_number: str
    scenario_id: str
    scenario_name: str
    agent_name: str
    message: str
    initiated_at: datetime


class CallStatusResponse(BaseModel):
    call_id: str
    status: CallStatus
    phone_number: str
    scenario_id: str
    duration_seconds: Optional[int] = None
    ended_reason: Optional[str] = None
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class ScenarioInfo(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    agent_name: str


class WebhookEvent(BaseModel):
    """Vapi webhook payload (simplified)."""
    message: dict


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
