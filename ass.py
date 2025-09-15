.env
DB_HOST=sd-rami-kmat.nam.nsroot.net
DB_PORT=1524
DB_USERNAME=postgres_dev_179442
DB_PASSWORD=ppdVEB9ACb
DB_NAME=gssp_common
DB_SESSION_ROLE=citi_pg_app_owner

dB.py
# db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

model.py
# models.py
from sqlalchemy import Column, Integer, Text, JSON, TIMESTAMP, func
from db import Base


class Feedback(Base):
    __tablename__ = "feedback_json"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Text, nullable=True)
    consumer_id = Column(Text, nullable=True)
    full_json = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


schema.py
# schemas.py
from pydantic import BaseModel
from typing import Any, Optional


class FeedbackIn(BaseModel):
    x_application_id: Optional[str] = None
    x_correlation_id: Optional[str] = None
    payload: Any

    class Config:
        extra = "allow"


class FeedbackOut(BaseModel):
    id: int
    application_id: Optional[str]
    consumer_id: Optional[str]
    full_json: Any

    class Config:
        orm_mode = True


crud.py
# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Feedback
from schemas import FeedbackIn


async def create_feedback(db: AsyncSession, feedback: FeedbackIn):
    db_feedback = Feedback(
        application_id=feedback.x_application_id,
        consumer_id=feedback.x_correlation_id,
        full_json=feedback.dict(),
    )
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    return db_feedback


async def get_feedbacks(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Feedback).offset(skip).limit(limit))
    return result.scalars().all()


fast.py
# fast.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import Base, engine, get_db
from models import Feedback
from schemas import FeedbackIn, FeedbackOut
import crud

app = FastAPI(title="GSSP Feedback API with ORM")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # Creates tables if they don’t exist
        await conn.run_sync(Base.metadata.create_all)


@app.post("/feedback/", response_model=FeedbackOut, status_code=201)
async def create_feedback(feedback: FeedbackIn, db: AsyncSession = Depends(get_db)):
    try:
        fb = await crud.create_feedback(db, feedback)
        return fb
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/", response_model=list[FeedbackOut])
async def list_feedbacks(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud.get_feedbacks(db, skip=skip, limit=limit)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fast:app", host="0.0.0.0", port=8000, reload=True)
