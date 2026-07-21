from fastapi import APIRouter

from app.api.v1 import auth, users, audios, images, videos, projects, preferences

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(audios.router, prefix="/audios", tags=["audios"])
router.include_router(images.router, prefix="/images", tags=["images"])
router.include_router(videos.router, prefix="/videos", tags=["videos"])
router.include_router(projects.router, prefix="/projects", tags=["projects"])
router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
