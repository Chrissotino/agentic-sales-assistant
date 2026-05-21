"""OpenAI wrapper for transcription and extraction."""
import json
import logging
from typing import BinaryIO

from openai import OpenAI

from app.core.settings import get_settings
from app.prompts.extraction_prompt import SYSTEM_PROMPT
from app.schemas.extraction import ExtractedActionPlan

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.enabled = bool(settings.openai_api_key)
        self.client = OpenAI(api_key=settings.openai_api_key) if self.enabled else None

    def transcribe_audio(self, file: BinaryIO, filename: str) -> str:
        if not self.enabled or self.client is None:
            return f"[simulated transcript] {filename}"
        result = self.client.audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=(filename, file.read()))
        return result.text

    def extract_action_plan(self, message: str) -> ExtractedActionPlan:
        if not self.enabled or self.client is None:
            logger.warning("OpenAI key missing; using deterministic fallback extraction")
            return ExtractedActionPlan(
                meeting_summary=message[:180],
                next_steps=["Review update", "Confirm follow-up"],
                confidence_score=0.55,
            )

        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            text={"format": {"type": "json_object"}},
        )
        payload = json.loads(response.output_text)
        return ExtractedActionPlan.model_validate(payload)
