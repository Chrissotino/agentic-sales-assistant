from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ExtractedActionPlan(BaseModel):
    account_name: str | None = None
    contact_name: str | None = None
    meeting_type: str | None = None
    meeting_summary: str | None = None
    customer_interest: str | None = None
    products_requested: list[str] = Field(default_factory=list)
    requested_follow_up_date: date | None = None
    create_task: bool = True
    create_note: bool = True
    create_or_update_deal: bool = False
    prepare_quote_request: bool = False
    prepare_email_draft: bool = False
    send_product_information: bool = False
    urgency: Literal["low", "medium", "high"] = "medium"
    next_steps: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)


class IntakeTextRequest(BaseModel):
    message: str
    persist: bool = True


class IntakeTextResponse(BaseModel):
    interaction_id: int | None = None
    extracted: ExtractedActionPlan


class IntakeVoiceResponse(BaseModel):
    interaction_id: int | None = None
    transcript: str
    extracted: ExtractedActionPlan
