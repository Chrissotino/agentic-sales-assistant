from sqlalchemy.orm import Session

from app.repositories.interaction_repository import InteractionRepository
from app.schemas.extraction import ExtractedActionPlan
from app.services.extraction_service import ExtractionService


class IntakeService:
    def __init__(self, db: Session) -> None:
        self.repo = InteractionRepository(db)
        self.extractor = ExtractionService()

    def process_text(self, message: str, persist: bool) -> tuple[int | None, ExtractedActionPlan]:
        extracted = self.extractor.extract_from_text(message)
        if not persist:
            return None, extracted
        row = self.repo.create(raw_input=message, extracted_payload=extracted.model_dump(), status="extracted")
        return row.id, extracted

    def process_voice(self, transcript: str, persist: bool) -> tuple[int | None, ExtractedActionPlan]:
        extracted = self.extractor.extract_from_text(transcript)
        if not persist:
            return None, extracted
        row = self.repo.create(transcript=transcript, extracted_payload=extracted.model_dump(), status="extracted")
        return row.id, extracted
