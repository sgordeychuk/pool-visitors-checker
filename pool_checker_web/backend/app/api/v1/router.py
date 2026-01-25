from fastapi import APIRouter

from app.api.v1.endpoints import auth, pools, visitors, analytics

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(pools.router)
api_router.include_router(visitors.router)
api_router.include_router(analytics.router)
