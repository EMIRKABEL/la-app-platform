"""API route definitions for Units."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.unit import UnitCreate, UnitResponse, UnitUpdate
from app.services.unit_service import UnitService

router = APIRouter(prefix="/api", tags=["units"])


@router.get(
    "/courses/{course_id}/units",
    response_model=list[UnitResponse],
)
def list_units(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[UnitResponse]:
    """Return all units for a course, ordered by unit number."""
    service = UnitService(db)
    units = service.list_units(course_id)
    return [UnitResponse.model_validate(u) for u in units]


@router.post(
    "/courses/{course_id}/units",
    response_model=UnitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_unit(
    course_id: uuid.UUID,
    payload: UnitCreate,
    db: Session = Depends(get_db),
) -> UnitResponse:
    """Create a new unit within a course."""
    service = UnitService(db)
    unit = service.create_unit(course_id, payload)
    return UnitResponse.model_validate(unit)


@router.get("/units/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> UnitResponse:
    """Return a single unit by id."""
    service = UnitService(db)
    unit = service.get_unit(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found",
        )
    return UnitResponse.model_validate(unit)


@router.put("/units/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: uuid.UUID,
    payload: UnitUpdate,
    db: Session = Depends(get_db),
) -> UnitResponse:
    """Update an existing unit by id."""
    service = UnitService(db)
    unit = service.update_unit(unit_id, payload)
    if unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found",
        )
    return UnitResponse.model_validate(unit)


@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Response:
    """Delete a unit by id."""
    service = UnitService(db)
    deleted = service.delete_unit(unit_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
