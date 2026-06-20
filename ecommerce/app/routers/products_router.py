from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/api", tags=["products"])


@router.get("/categories", response_model=list[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.name).all()


@router.get("/products", response_model=list[schemas.ProductOut])
def list_products(
    q: Optional[str] = Query(default=None, description="Search term"),
    category: Optional[str] = Query(default=None, description="Category slug"),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = Query(
        default=None, description="price_asc | price_desc | rating | newest"
    ),
    limit: int = Query(default=40, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models.Product).filter(models.Product.is_active.is_(True))

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(models.Product.title.like(like), models.Product.brand.like(like))
        )

    if category:
        query = query.join(models.Category).filter(models.Category.slug == category)

    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    if sort == "price_asc":
        query = query.order_by(models.Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(models.Product.price.desc())
    elif sort == "rating":
        query = query.order_by(models.Product.rating.desc())
    elif sort == "newest":
        query = query.order_by(models.Product.created_at.desc())

    return query.offset(offset).limit(limit).all()


@router.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/{product_id}/reviews", response_model=list[schemas.ReviewOut])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(models.Review)
        .filter(models.Review.product_id == product_id)
        .order_by(models.Review.created_at.desc())
        .all()
    )
    return [
        schemas.ReviewOut(
            id=r.id,
            rating=r.rating,
            comment=r.comment,
            user_name=r.user.name,
            created_at=r.created_at,
        )
        for r in reviews
    ]


@router.post("/products/{product_id}/reviews", response_model=schemas.ReviewOut, status_code=201)
def add_review(
    product_id: int,
    payload: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = (
        db.query(models.Review)
        .filter(models.Review.product_id == product_id, models.Review.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this product")

    review = models.Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)

    # Recompute aggregate rating
    total = product.rating_count or 0
    new_count = total + 1
    new_avg = ((float(product.rating or 0) * total) + payload.rating) / new_count
    product.rating = round(new_avg, 1)
    product.rating_count = new_count

    db.commit()
    db.refresh(review)

    return schemas.ReviewOut(
        id=review.id,
        rating=review.rating,
        comment=review.comment,
        user_name=current_user.name,
        created_at=review.created_at,
    )
