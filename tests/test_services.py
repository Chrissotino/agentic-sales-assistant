from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.services.action_service import ActionExecutionService
from app.services.intake_service import IntakeService


def setup_db() -> Session:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    local = sessionmaker(bind=engine, class_=Session)
    return local()


def test_intake_service_text() -> None:
    db = setup_db()
    service = IntakeService(db)
    interaction_id, extracted = service.process_text('Met ACME and they want follow-up.', persist=True)
    assert interaction_id is not None
    assert extracted.confidence_score >= 0.0


def test_hubspot_simulated_execution() -> None:
    db = setup_db()
    intake = IntakeService(db)
    interaction_id, extracted = intake.process_text('Customer asked for task and note.', persist=True)
    executor = ActionExecutionService(db)
    result = executor.execute(extracted, interaction_id)
    assert result.simulated is True
    assert len(result.operations) >= 1
