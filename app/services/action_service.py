from sqlalchemy.orm import Session

from app.clients.hubspot_client import HubSpotClient
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.actions import ExecuteActionsResponse
from app.schemas.extraction import ExtractedActionPlan


class ActionExecutionService:
    def __init__(self, db: Session) -> None:
        self.hubspot = HubSpotClient()
        self.repo = InteractionRepository(db)

    def execute(self, payload: ExtractedActionPlan, interaction_id: int | None = None) -> ExecuteActionsResponse:
        ops: list[dict] = []
        if payload.create_note:
            ops.append(self.hubspot.create_note(payload.meeting_summary or "Meeting update"))
        if payload.create_task:
            ops.append(self.hubspot.create_task(subject="Sales follow-up", due_date=str(payload.requested_follow_up_date) if payload.requested_follow_up_date else None))
        if payload.create_or_update_deal and payload.account_name:
            ops.append(self.hubspot.create_deal({"dealname": f"{payload.account_name} opportunity"}))

        result = ExecuteActionsResponse(
            simulated=self.hubspot.simulated,
            summary=f"Executed {len(ops)} CRM operation(s)",
            operations=ops,
        )
        if interaction_id:
            row = self.repo.get(interaction_id)
            if row:
                self.repo.update(row, execution_result=result.model_dump(), status="executed")
        return result
