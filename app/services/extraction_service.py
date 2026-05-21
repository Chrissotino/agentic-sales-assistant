from app.clients.openai_client import OpenAIClient
from app.schemas.extraction import ExtractedActionPlan


class ExtractionService:
    def __init__(self, client: OpenAIClient | None = None) -> None:
        self.client = client or OpenAIClient()

    def extract_from_text(self, message: str) -> ExtractedActionPlan:
        return self.client.extract_action_plan(message)
