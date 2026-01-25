# Pool Checker - Claude Context

## Project Overview

Pool Visitor Tracker is a full-stack web application for tracking and analyzing swimming pool visitor counts. The system scrapes visitor data from pool websites, stores it in PostgreSQL, and provides analytics visualizations.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 17 + SQLAlchemy ORM
- **Cache/Queue**: Redis 7 + Celery
- **Scraping**: Selenium 4.17 with ChromeDriver
- **Auth**: JWT (python-jose) + bcrypt
- **Migrations**: Alembic

### Frontend
- **Framework**: SvelteKit 2.5 + TypeScript
- **UI**: Skeleton Labs + Tailwind CSS 3.4
- **Charts**: Chart.js 4.4
- **Build**: Vite 5

### Infrastructure
- Docker Compose (6 services)
- Nginx reverse proxy

## Directory Structure

```
pool_checker/
├── pool_checker_web/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py           # FastAPI entry
│   │   │   ├── config.py         # Settings
│   │   │   ├── models/           # SQLAlchemy models
│   │   │   ├── schemas/          # Pydantic schemas
│   │   │   ├── api/v1/endpoints/ # API routes
│   │   │   ├── services/         # Business logic
│   │   │   └── core/security.py  # JWT/auth
│   │   ├── celery_app/tasks/     # Scheduled scraping
│   │   └── alembic/              # DB migrations
│   ├── frontend/
│   │   └── src/
│   │       ├── lib/              # API client, stores, components
│   │       └── routes/           # SvelteKit pages
│   └── nginx/                    # Reverse proxy config
```

## Key Files

- `backend/app/main.py` - FastAPI app initialization, CORS, routing
- `backend/app/api/v1/endpoints/analytics.py` - Analytics calculations
- `backend/celery_app/tasks/scraper_tasks.py` - Selenium scraping logic
- `frontend/src/lib/api.ts` - Typed API client
- `frontend/src/routes/analytics/+page.svelte` - Analytics dashboard

## Database Models

- **User**: email, username, hashed_password, is_active, is_superuser
- **Pool**: name, url, element_id, timezone, scrape schedule config
- **VisitorRecord**: pool_id, timestamp, weekday, visitor_count, week_number

## API Endpoints

- `POST /api/v1/auth/login` - JWT login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/pools/` - List pools
- `POST /api/v1/pools/` - Create pool
- `GET /api/v1/visitors/{pool_id}` - Get visitor records
- `GET /api/v1/analytics/trends/{pool_id}` - Trend analysis
- `GET /api/v1/analytics/heatmap/{pool_id}` - Weekday heatmap

## Development Commands

```bash
# Start all services
cd pool_checker_web
docker compose up -d

# Run backend only (dev)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Run frontend only (dev)
cd frontend
npm install
npm run dev

# Database migrations
cd backend
alembic upgrade head

# Import sample data
python scripts/import_csv.py
```

## Environment Variables

Required in `.env`:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `SECRET_KEY` - JWT signing key
- `REDIS_URL` - Redis connection
- `ADMIN_EMAIL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`

## Common Tasks

### Adding a new API endpoint
1. Create schema in `backend/app/schemas/`
2. Add service method in `backend/app/services/`
3. Create endpoint in `backend/app/api/v1/endpoints/`
4. Register route in `backend/app/api/v1/router.py`

### Adding a new frontend page
1. Create route in `frontend/src/routes/{name}/+page.svelte`
2. Add API method in `frontend/src/lib/api.ts`
3. Update navigation in `frontend/src/routes/+layout.svelte`

### Modifying database schema
1. Update model in `backend/app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply: `alembic upgrade head`

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend type check
cd frontend
npm run check
```

## Notes

- Celery Beat handles scheduled scraping (configurable per pool)
- Selenium runs headless Chrome for web scraping
- Frontend uses Skeleton UI components with dark theme support
- All API responses use Pydantic schemas for validation
