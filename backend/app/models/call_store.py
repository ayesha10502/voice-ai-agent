"""
Simple in-memory call store.
In production, replace with PostgreSQL / Redis.
"""
from datetime import datetime
from typing import Optional
from app.schemas.call import CallStatus


class CallRecord:
    def __init__(
        self,
        call_id: str,
        phone_number: str,
        scenario_id: str,
        scenario_name: str,
        agent_name: str,
    ):
        self.call_id = call_id
        self.phone_number = phone_number
        self.scenario_id = scenario_id
        self.scenario_name = scenario_name
        self.agent_name = agent_name
        self.status: CallStatus = CallStatus.PENDING
        self.duration_seconds: Optional[int] = None
        self.ended_reason: Optional[str] = None
        self.summary: Optional[str] = None
        self.created_at: datetime = datetime.utcnow()
        self.ended_at: Optional[datetime] = None


class CallStore:
    def __init__(self):
        self._store: dict[str, CallRecord] = {}

    def save(self, record: CallRecord) -> None:
        self._store[record.call_id] = record

    def get(self, call_id: str) -> Optional[CallRecord]:
        return self._store.get(call_id)

    def update_status(
        self,
        call_id: str,
        status: CallStatus,
        ended_reason: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        summary: Optional[str] = None,
    ) -> Optional[CallRecord]:
        record = self._store.get(call_id)
        if record:
            record.status = status
            if ended_reason:
                record.ended_reason = ended_reason
            if duration_seconds is not None:
                record.duration_seconds = duration_seconds
            if summary:
                record.summary = summary
            if status in (
                CallStatus.COMPLETED,
                CallStatus.FAILED,
                CallStatus.CANCELLED,
                CallStatus.NO_ANSWER,
            ):
                record.ended_at = datetime.utcnow()
        return record

    def list_all(self) -> list[CallRecord]:
        return sorted(self._store.values(), key=lambda r: r.created_at, reverse=True)


# Singleton instance
call_store = CallStore()
