from sqlalchemy.orm import Session

from app.models.interaction import Interaction


class InteractionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, **kwargs) -> Interaction:
        interaction = Interaction(**kwargs)
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def update(self, interaction: Interaction, **kwargs) -> Interaction:
        for key, value in kwargs.items():
            setattr(interaction, key, value)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def get(self, interaction_id: int) -> Interaction | None:
        return self.db.query(Interaction).filter(Interaction.id == interaction_id).first()

    def list(self, limit: int = 100) -> list[Interaction]:
        return self.db.query(Interaction).order_by(Interaction.created_at.desc()).limit(limit).all()
