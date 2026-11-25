from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import HealthReading, Parent, User, UserRole
from app.schemas.schemas import HealthReadingCreate, HealthReadingResponse

router = APIRouter(prefix="/health-readings", tags=["health-readings"])


def _format_reading(reading: HealthReading) -> HealthReadingResponse:
    response = HealthReadingResponse.model_validate(reading)
    response.parent_name = reading.parent.name if reading.parent else None
    return response


@router.get("", response_model=list[HealthReadingResponse])
def get_health_readings(
    parent_id: Optional[int] = None,
    metric: Optional[
        Literal["blood_pressure", "blood_glucose", "temperature", "weight", "heart_rate"]
    ] = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(HealthReading).join(Parent)
    if current_user.role != UserRole.ADMIN.value:
        query = query.filter(Parent.user_id == current_user.id)
    if parent_id is not None:
        query = query.filter(HealthReading.parent_id == parent_id)
    if metric:
        query = query.filter(HealthReading.metric == metric)

    readings = (
        query.order_by(HealthReading.recorded_at.desc(), HealthReading.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_format_reading(reading) for reading in readings]


@router.post("", response_model=HealthReadingResponse, status_code=status.HTTP_201_CREATED)
def create_health_reading(
    reading_in: HealthReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parent = db.query(Parent).filter(Parent.id == reading_in.parent_id).first()
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent not found")
    if current_user.role != UserRole.ADMIN.value and parent.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    reading = HealthReading(
        parent_id=parent.id,
        metric=reading_in.metric,
        value=reading_in.value,
        secondary_value=(
            reading_in.secondary_value
            if reading_in.secondary_value is not None
            else None
        ),
        unit=reading_in.unit.strip(),
        recorded_at=reading_in.recorded_at,
        notes=reading_in.notes.strip() if reading_in.notes else None,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return _format_reading(reading)


@router.delete("/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = (
        db.query(HealthReading)
        .join(Parent)
        .filter(HealthReading.id == reading_id)
        .first()
    )
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health reading not found")
    if current_user.role != UserRole.ADMIN.value and reading.parent.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(reading)
    db.commit()
    return None
