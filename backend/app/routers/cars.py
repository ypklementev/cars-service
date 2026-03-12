from app.utils.signature import check_signature

from ..auth import get_current_user
from fastapi import APIRouter, Depends, Query
from fastapi.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from ..db import get_db
from ..models import Car, User

router = APIRouter()


@router.get("/api/cars")
def get_cars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Car).all()

@router.get("/api/search")
def search_cars(
    brand: str | None = Query(None),
    color: str | None = Query(None),
    price_max: int | None = Query(None),
    year_min: int | None = Query(None),
    db: Session = Depends(get_db)
):

    query = db.query(Car)

    if brand:
        query = query.filter(Car.brand.ilike(f"%{brand}%"))

    if color:
        query = query.filter(Car.color.ilike(f"%{color}%"))

    if price_max:
        query = query.filter(Car.price <= price_max)

    if year_min:
        query = query.filter(Car.year >= year_min)

    return query.limit(50).all()


@router.post("/api/cars")
async def upsert_car(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(check_signature)
):

    car = await request.json()

    stmt = insert(Car).values(**car)

    stmt = stmt.on_conflict_do_update(
        index_elements=["url"],
        set_=car
    )

    db.execute(stmt)
    db.commit()

    return {"status": "ok"}

@router.delete("/api/delete_all")
def delete_all_cars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Car).delete()
    db.commit()

    return {"status": "ok"}