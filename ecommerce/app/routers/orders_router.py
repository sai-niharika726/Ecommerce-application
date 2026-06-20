from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/api", tags=["orders"])


# ---------- Addresses ----------

@router.get("/addresses", response_model=list[schemas.AddressOut])
def list_addresses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Address)
        .filter(models.Address.user_id == current_user.id)
        .order_by(models.Address.is_default.desc())
        .all()
    )


@router.post("/addresses", response_model=schemas.AddressOut, status_code=201)
def create_address(
    payload: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if payload.is_default:
        db.query(models.Address).filter(models.Address.user_id == current_user.id).update(
            {"is_default": False}
        )

    address = models.Address(user_id=current_user.id, **payload.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


# ---------- Orders / Checkout ----------

@router.post("/checkout", response_model=schemas.OrderOut, status_code=201)
def checkout(
    payload: schemas.CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    address = (
        db.query(models.Address)
        .filter(models.Address.id == payload.address_id, models.Address.user_id == current_user.id)
        .first()
    )
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    cart_items = (
        db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    )
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = sum(float(ci.product.price) * ci.quantity for ci in cart_items)

    order = models.Order(
        user_id=current_user.id,
        address_id=address.id,
        status=models.OrderStatus.PAID,
        total_amount=round(total, 2),
    )
    db.add(order)
    db.flush()  # get order.id before commit

    for ci in cart_items:
        if ci.product.stock < ci.quantity:
            raise HTTPException(
                status_code=400, detail=f"Insufficient stock for {ci.product.title}"
            )
        ci.product.stock -= ci.quantity
        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=ci.product.id,
                title_snapshot=ci.product.title,
                image_snapshot=ci.product.image_url,
                price_snapshot=ci.product.price,
                quantity=ci.quantity,
            )
        )
        db.delete(ci)

    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=list[schemas.OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


@router.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    order = (
        db.query(models.Order)
        .filter(models.Order.id == order_id, models.Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
