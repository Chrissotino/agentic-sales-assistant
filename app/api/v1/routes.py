from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.clients.openai_client import OpenAIClient
from app.db.session import get_db
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.actions import ExecuteActionsRequest, ExecuteActionsResponse
from app.schemas.extraction import IntakeTextRequest, IntakeTextResponse, IntakeVoiceResponse
from app.schemas.interaction import InteractionRead
from app.services.action_service import ActionExecutionService
from app.services.intake_service import IntakeService

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/intake/text", response_model=IntakeTextResponse)
def intake_text(payload: IntakeTextRequest, db: Session = Depends(get_db)) -> IntakeTextResponse:
    service = IntakeService(db)
    interaction_id, extracted = service.process_text(payload.message, payload.persist)
    return IntakeTextResponse(interaction_id=interaction_id, extracted=extracted)


@router.post("/intake/voice", response_model=IntakeVoiceResponse)
def intake_voice(file: UploadFile = File(...), persist: bool = True, db: Session = Depends(get_db)) -> IntakeVoiceResponse:
    openai_client = OpenAIClient()
    transcript = openai_client.transcribe_audio(file.file, file.filename)
    service = IntakeService(db)
    interaction_id, extracted = service.process_voice(transcript, persist)
    return IntakeVoiceResponse(interaction_id=interaction_id, transcript=transcript, extracted=extracted)


@router.post("/actions/execute", response_model=ExecuteActionsResponse)
def execute_actions(payload: ExecuteActionsRequest, db: Session = Depends(get_db)) -> ExecuteActionsResponse:
    service = ActionExecutionService(db)
    return service.execute(payload.payload, payload.interaction_id)


@router.get("/interactions", response_model=list[InteractionRead])
def list_interactions(db: Session = Depends(get_db), limit: int = 100) -> list[InteractionRead]:
    repo = InteractionRepository(db)
    return [InteractionRead.model_validate(item) for item in repo.list(limit)]
