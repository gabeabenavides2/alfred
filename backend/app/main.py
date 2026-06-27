from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import get_db, Base, engine
from app.db.models import *   # important: registers all models
from app.api.chat import router as chat_router


# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Alfred API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()

    return {
        "database": "connected",
        "result": result,
    }