import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, UploadFile

from app.api.deps import CurrentUser, DBSession
from app.core.exceptions import BadRequestException
from app.models.image import Image
from app.models.project import ProjectAsset
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.image import ImageCreate, ImageResponse, ImageUpdate
from app.services.image import ImageService, _get_project_ids, _to_response
from app.utils.pagination import PaginationParams
from app.utils.storage import ALLOWED_IMAGE, save_uploaded_image

router = APIRouter()


@router.post("", response_model=ImageResponse, status_code=201)
async def create_image(
    body: ImageCreate,
    session: DBSession,
    current_user: CurrentUser,
) -> ImageResponse:
    svc = ImageService(session)
    return await svc.create(current_user, body)


@router.post("/import", response_model=list[ImageResponse], status_code=201)
async def import_images(
    files: list[UploadFile],
    session: DBSession,
    current_user: CurrentUser,
    project_id: uuid.UUID = Form(...),
):
    if not current_user.tenant_id:
        raise BadRequestException("No tenant context")
    results: list[ImageResponse] = []
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in ALLOWED_IMAGE:
            raise BadRequestException(f"Invalid image file type: {f.filename}")
        data = await f.read()
        url = save_uploaded_image(data, f.filename or "image.png")
        title = Path(f.filename or "image").stem
        image = Image(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            project_id=project_id,
            title=title,
            file_url=url,
        )
        session.add(image)
        await session.flush()
        await session.refresh(image)
        session.add(ProjectAsset(project_id=project_id, asset_type="image", asset_id=image.id))
        await session.flush()
        pids = await _get_project_ids(session, image.id, "image")
        results.append(_to_response(image, pids))
    return results


@router.get("", response_model=PaginatedResponse[ImageResponse])
async def list_images(
    session: DBSession,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    project_id: str | None = Query(default=None),
) -> PaginatedResponse[ImageResponse]:
    svc = ImageService(session)
    return await svc.list_for_tenant(current_user, pagination.page, pagination.size, project_id=project_id)


@router.put("/{image_id}", response_model=ImageResponse)
async def update_image(
    image_id: uuid.UUID,
    body: ImageUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> ImageResponse:
    svc = ImageService(session)
    return await svc.update(current_user, image_id, body)


@router.delete("/{image_id}", response_model=MessageResponse)
async def delete_image(
    image_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
) -> MessageResponse:
    svc = ImageService(session)
    await svc.delete(current_user, image_id)
    return MessageResponse(detail="Image deleted")
