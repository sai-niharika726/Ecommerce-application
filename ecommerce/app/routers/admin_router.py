from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/products", response_model=list[schemas.ProductOut])
def admin_list_products(
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    return db.query(models.Product).order_by(models.Product.id.desc()).all()


@router.post("/products", response_model=schemas.ProductOut, status_code=201)
def admin_create_product(
    payload: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=schemas.ProductOut)
def admin_update_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=204)
def admin_delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return None


@router.get("/orders", response_model=list[schemas.OrderOut])
def admin_list_orders(
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()


@router.post("/categories", response_model=schemas.CategoryOut, status_code=201)
def admin_create_category(
    payload: schemas.CategoryOut,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    existing = db.query(models.Category).filter(models.Category.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category slug already exists")
    category = models.Category(name=payload.name, slug=payload.slug, icon=payload.icon)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
