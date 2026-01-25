# Pool Visitor Tracker

A full-stack web application for tracking and analyzing swimming pool visitor counts. Automatically scrapes visitor data from pool websites, stores historical records, and provides analytics with trend visualizations and heatmaps.

## Features

- **Automated Data Collection**: Scheduled web scraping using Selenium to capture visitor counts
- **Multi-Pool Support**: Track multiple pools with individual configurations
- **Analytics Dashboard**: Visualize visitor trends, patterns, and peak hours
- **Heatmap Visualization**: See visitor patterns by day of week and time
- **User Authentication**: Secure JWT-based authentication
- **RESTful API**: Full-featured API with OpenAPI documentation

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.11, SQLAlchemy |
| Frontend | SvelteKit, TypeScript, Tailwind CSS |
| Database | PostgreSQL 17 |
| Cache/Queue | Redis 7, Celery |
| Scraping | Selenium, ChromeDriver |
| Charts | Chart.js |
| Infrastructure | Docker, Docker Compose, Nginx |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pool_checker
```

2. Create environment file:
```bash
cp pool_checker_web/.env.example pool_checker_web/.env
```

3. Edit `.env` with your configuration:
```env
POSTGRES_USER=pool_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=pool_checker
SECRET_KEY=your_jwt_secret_key
ADMIN_EMAIL=admin@example.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password
```

4. Start all services:
```bash
cd pool_checker_web
docker compose up -d
```

5. Access the application:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Import Sample Data (Optional)

```bash
docker compose exec backend python scripts/import_csv.py
```

## Development

### Backend Development

```bash
cd pool_checker_web/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd pool_checker_web/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests

```bash
# Backend tests
cd pool_checker_web/backend
pytest

# Frontend type checking
cd pool_checker_web/frontend
npm run check
```

## Project Structure

```
pool_checker/
├── pool_checker_web/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/v1/endpoints/  # API routes
│   │   │   ├── models/            # Database models
│   │   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── services/          # Business logic
│   │   │   └── core/              # Security utilities
│   │   ├── celery_app/            # Background tasks
│   │   └── alembic/               # Database migrations
│   ├── frontend/
│   │   └── src/
│   │       ├── lib/               # Components & utilities
│   │       └── routes/            # SvelteKit pages
│   ├── nginx/                     # Reverse proxy config
│   └── docker-compose.yml
├── CLAUDE.md                      # AI assistant context
└── README.md
```

## API Documentation

Once running, visit `/docs` for interactive Swagger documentation.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/register` | User registration |
| GET | `/api/v1/pools/` | List all pools |
| POST | `/api/v1/pools/` | Create a new pool |
| GET | `/api/v1/visitors/{pool_id}` | Get visitor records |
| GET | `/api/v1/analytics/trends/{pool_id}` | Get trend analysis |
| GET | `/api/v1/analytics/heatmap/{pool_id}` | Get heatmap data |

## Configuration

### Pool Configuration

Each pool can be configured with:
- **URL**: Website to scrape
- **Element ID**: CSS selector for visitor count element
- **Timezone**: Pool's local timezone
- **Scrape Schedule**: Start time, end time, interval

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `POSTGRES_USER` | Database username | Yes |
| `POSTGRES_PASSWORD` | Database password | Yes |
| `POSTGRES_DB` | Database name | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `REDIS_URL` | Redis connection URL | Yes |
| `ADMIN_EMAIL` | Initial admin email | Yes |
| `ADMIN_USERNAME` | Initial admin username | Yes |
| `ADMIN_PASSWORD` | Initial admin password | Yes |

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | SvelteKit application |
| backend | 8000 | FastAPI server |
| db | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache/broker |
| celery-worker | - | Background task processor |
| celery-beat | - | Task scheduler |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License
