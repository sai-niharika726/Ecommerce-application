from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth_router, products_router, cart_router, orders_router, admin_router

app = FastAPI(title="ShopKart", description="A full-featured ecommerce demo app", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(cart_router.router)
app.include_router(orders_router.router)
app.include_router(admin_router.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    if settings.SEED_DEMO_DATA:
        from app.seed import seed
        seed()


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Server-rendered frontend pages ----------

@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/product/{product_id}")
def product_page(request: Request, product_id: int):
    return templates.TemplateResponse("product.html", {"request": request, "product_id": product_id})


@app.get("/cart")
def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})


@app.get("/checkout")
def checkout_page(request: Request):
    return templates.TemplateResponse("checkout.html", {"request": request})


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/orders")
def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})


@app.get("/admin")
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
