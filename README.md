# ShopKart — Full-Stack Ecommerce App

A complete ecommerce application: FastAPI backend, MySQL database, server-rendered
frontend styled like Myntra/Amazon (product grid, cart, checkout, ratings, admin panel).

## Stack
- **Backend**: FastAPI (Python 3.12)
- **Database**: MySQL 8.0 (via SQLAlchemy + PyMySQL)
- **Frontend**: Server-rendered HTML/CSS/JS (Jinja2 templates, no build step)
- **Auth**: JWT bearer tokens, bcrypt password hashing
- **Containerization**: Docker + docker-compose

## Features
- Product catalog with categories, search, filters, sorting
- Product detail pages with ratings & reviews
- Cart (add/update/remove), persisted per user
- Address book + checkout flow, order placement and history
- User signup/login (JWT)
- Admin panel: create/delete products, view all orders (RBAC protected)
- Auto-seeds 18 demo products across 6 categories with real product photos on first run

## Project structure
```
app/
  main.py              # FastAPI app entrypoint, page routes
  config.py            # env-based settings
  database.py          # SQLAlchemy engine/session
  models.py            # ORM models
  schemas.py           # Pydantic request/response schemas
  auth.py              # JWT + password hashing
  seed.py              # demo data seeding
  routers/             # API route modules (auth, products, cart, orders, admin)
  templates/           # Jinja2 HTML pages
  static/css/          # stylesheet
  static/js/           # frontend logic (fetch-based API client)
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

## Run locally with Docker (recommended)

1. Copy the env file and edit secrets:
   ```bash
   cp .env.example .env
   # edit .env — set MYSQL_PASSWORD, MYSQL_ROOT_PASSWORD, SECRET_KEY to real values
   ```

2. Build and start everything:
   ```bash
   docker compose up --build
   ```

3. Open **http://localhost:8000**

   The app auto-creates tables and seeds demo data on first boot.

   Demo admin login: `admin@shopkart.com` / `admin123` — go to **/admin** after logging in.

## Run without Docker (dev mode)

Requires a running MySQL instance.

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# point DATABASE_URL at your local MySQL, e.g.:
# DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/shopkart

uvicorn app.main:app --reload
```

Visit http://localhost:8000

## Environment variables (.env)
| Variable | Description |
|---|---|
| `DATABASE_URL` | Full SQLAlchemy MySQL connection string |
| `SECRET_KEY` | JWT signing secret — set a long random value in production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry, default 1440 (24h) |
| `SEED_DEMO_DATA` | `true`/`false` — seed demo products on startup |

## Deploying

This app is container-ready as-is:
- `docker build -t shopkart .` then push to any registry (ECR, GCR, Docker Hub)
- `docker-compose.yml` works on any Docker host (EC2, a VPS, etc.) or adapt the two
  services into separate deployments on ECS/Cloud Run/Kubernetes — the `web` service
  just needs a reachable MySQL and the `DATABASE_URL` env var
- For managed MySQL (RDS, Cloud SQL, PlanetScale), drop the `db` service from
  docker-compose and point `DATABASE_URL` at your managed instance
- Set `SEED_DEMO_DATA=false` in production after the first run, or remove the seed
  call once you have real catalog data

## Notes
- Product images are hotlinked from Unsplash for the demo catalog — replace
  `image_url` values via the admin panel for production use.
- This demo does not integrate a real payment gateway; checkout marks orders as
  `paid` immediately. Wire in Stripe/Razorpay in `app/routers/orders_router.py`
  before going live.
- API docs available at `/docs` (Swagger) and `/redoc`.
