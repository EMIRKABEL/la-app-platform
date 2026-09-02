"""API route definitions for course-level curriculum uploads and extraction."""

from __future__ import annotations

import uuid
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.course_curriculum_source import (
    CourseCurriculumSourceResponse,
    CourseExtractionResponse,
)
from app.services.course_curriculum_service import CourseCurriculumService

router = APIRouter(prefix="/api", tags=["course-curriculum"])


@router.post(
    "/courses/{course_id}/curriculum",
    response_model=List[CourseCurriculumSourceResponse],
    status_code=status.HTTP_201_CREATED,
)
def upload_course_curriculum(
    course_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> list[CourseCurriculumSourceResponse]:
    """Upload one or more curriculum source files to a course.

    Accepted file types: ``.pptx``, ``.pdf``, ``.docx``, ``.xlsx``.
    """
    service = CourseCurriculumService(db)
    try:
        records = service.upload_multiple_curriculum(course_id, files)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        )
    return [CourseCurriculumSourceResponse.model_validate(r) for r in records]


@router.get(
    "/courses/{course_id}/curriculum",
    response_model=List[CourseCurriculumSourceResponse],
)
def list_course_curriculum(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[CourseCurriculumSourceResponse]:
    """Return all curriculum source files for a course."""
    service = CourseCurriculumService(db)
    sources = service.list_curriculum(course_id)
    return [CourseCurriculumSourceResponse.model_validate(s) for s in sources]


@router.post(
    "/course-curriculum/{source_id}/extract",
    response_model=CourseExtractionResponse,
)
def extract_course_curriculum(
    source_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CourseExtractionResponse:
    """Extract structured content from a course curriculum source file.

    Currently supports ``.pptx`` only.  Other file types return 415.
    """
    service = CourseCurriculumService(db)
    try:
        record = service.extract_curriculum(source_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course curriculum source not found",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Extraction failed",
        )
    return CourseExtractionResponse.model_validate(record)


@router.get(
    "/course-curriculum/{source_id}/extraction",
    response_model=CourseExtractionResponse,
)
def get_course_extraction(
    source_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CourseExtractionResponse:
    """Return the saved structured extraction for a course curriculum source."""
    service = CourseCurriculumService(db)
    record = service.get_extraction(source_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course curriculum source not found",
        )
    return CourseExtractionResponse.model_validate(record)
