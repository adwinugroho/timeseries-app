from fastapi import APIRouter

from app.api.v1.routes import sandbox

router = APIRouter(prefix="/api/v1")
router.include_router(sandbox.router)
