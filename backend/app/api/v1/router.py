from fastapi import APIRouter

from app.api.v1 import attempts, exercises

api_router = APIRouter()
api_router.include_router(exercises.router)
api_router.include_router(attempts.router)
