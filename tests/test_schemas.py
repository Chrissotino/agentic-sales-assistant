import pytest
from pydantic import ValidationError

from app.schemas.extraction import ExtractedActionPlan


def test_extraction_schema_valid() -> None:
    payload = ExtractedActionPlan(confidence_score=0.9)
    assert payload.confidence_score == 0.9


def test_extraction_schema_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        ExtractedActionPlan(confidence_score=2.0)
