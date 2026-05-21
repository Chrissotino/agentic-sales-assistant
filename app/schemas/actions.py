from pydantic import BaseModel

from app.schemas.extraction import ExtractedActionPlan


class ExecuteActionsRequest(BaseModel):
    payload: ExtractedActionPlan
    interaction_id: int | None = None


class ExecuteActionsResponse(BaseModel):
    simulated: bool
    summary: str
    operations: list[dict]
