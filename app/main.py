from fastapi import FastAPI

from app.api.v1.routes import router as v1_router
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.include_router(v1_router, prefix=settings.api_v1_prefix, tags=["v1"])


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
