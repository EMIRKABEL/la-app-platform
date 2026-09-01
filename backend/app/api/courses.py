"""API route definitions for Courses."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.course import CourseCreate, CourseResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("", response_model=list[CourseResponse])
def list_courses(db: Session = Depends(get_db)) -> list[CourseResponse]:
    """Return all courses, newest first."""
    service = CourseService(db)
    courses = service.list_courses()
    return [CourseResponse.model_validate(c) for c in courses]


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
) -> CourseResponse:
    """Create a new course."""
    service = CourseService(db)
    course = service.create_course(payload)
    return CourseResponse.model_validate(course)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CourseResponse:
    """Return a single course by id."""
    service = CourseService(db)
    course = service.get_course(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return CourseResponse.model_validate(course)
