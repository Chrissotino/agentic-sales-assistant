from datetime import datetime

from pydantic import BaseModel


class InteractionRead(BaseModel):
    id: int
    raw_input: str | None
    transcript: str | None
    extracted_payload: dict | None
    execution_result: dict | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
