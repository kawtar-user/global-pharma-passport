from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, billing, interactions, international_equivalents, medications, meta, passport, users

api_router = APIRouter()
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(medications.router, prefix="/medications", tags=["medications"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
api_router.include_router(passport.router, prefix="/passport", tags=["passport"])
api_router.include_router(
    international_equivalents.router,
    prefix="/international-equivalents",
    tags=["international-equivalents"],
)
