"""API route definitions for curriculum uploads."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.curriculum_source import CurriculumSourceResponse
from app.services.curriculum_service import CurriculumService

router = APIRouter(prefix="/api", tags=["curriculum"])


@router.post(
    "/lessons/{lesson_id}/curriculum",
    response_model=CurriculumSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_curriculum(
    lesson_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> CurriculumSourceResponse:
    """Upload a curriculum source file to a lesson.

    Accepted file types: ``.pptx``, ``.pdf``, ``.docx``, ``.xlsx``.
    """
    service = CurriculumService(db)
    try:
        record = service.upload_curriculum(lesson_id, file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        )
    return CurriculumSourceResponse.model_validate(record)


@router.get(
    "/lessons/{lesson_id}/curriculum",
    response_model=list[CurriculumSourceResponse],
)
def list_curriculum(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[CurriculumSourceResponse]:
    """Return all curriculum source files for a lesson."""
    service = CurriculumService(db)
    sources = service.list_curriculum(lesson_id)
    return [CurriculumSourceResponse.model_validate(s) for s in sources]
