"""API route definitions for Lessons."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.lesson import LessonCreate, LessonResponse
from app.services.lesson_service import LessonService

router = APIRouter(prefix="/api", tags=["lessons"])


@router.get(
    "/units/{unit_id}/lessons",
    response_model=list[LessonResponse],
)
def list_lessons(
    unit_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[LessonResponse]:
    """Return all lessons for a unit, ordered by lesson number."""
    service = LessonService(db)
    lessons = service.list_lessons(unit_id)
    return [LessonResponse.model_validate(l) for l in lessons]


@router.post(
    "/units/{unit_id}/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson(
    unit_id: uuid.UUID,
    payload: LessonCreate,
    db: Session = Depends(get_db),
) -> LessonResponse:
    """Create a new lesson within a unit.

    New lessons always start with status ``draft``.
    """
    service = LessonService(db)
    lesson = service.create_lesson(unit_id, payload)
    return LessonResponse.model_validate(lesson)


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> LessonResponse:
    """Return a single lesson by id."""
    service = LessonService(db)
    lesson = service.get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    return LessonResponse.model_validate(lesson)
