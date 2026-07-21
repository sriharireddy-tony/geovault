import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DBSession
from app.domains.knowledge.schemas import (
    ConversationCreate,
    ConversationResponse,
    KnowledgeSpaceCreate,
    KnowledgeSpaceResponse,
    KnowledgeSpaceUpdate,
    MessageCreate,
    MessageResponse,
    SearchHit,
    SearchRequest,
    SourceCreateText,
    SourceResponse,
)
from app.domains.knowledge.services.chat import stream_chat_response
from app.domains.knowledge.services.knowledge import KnowledgeService
from app.domains.knowledge.models import SourceType
from app.schemas.common import MessageResponse as SimpleMessage, PaginatedResponse
from app.utils.pagination import PaginationParams

router = APIRouter()


def _detect_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    mapping = {
        ".txt": SourceType.TXT.value,
        ".md": SourceType.MARKDOWN.value,
        ".markdown": SourceType.MARKDOWN.value,
        ".pdf": SourceType.PDF.value,
        ".docx": SourceType.DOCX.value,
        ".pptx": SourceType.PPTX.value,
        ".csv": SourceType.CSV.value,
        ".xlsx": SourceType.XLSX.value,
        ".xls": SourceType.XLSX.value,
        ".png": SourceType.IMAGE.value,
        ".jpg": SourceType.IMAGE.value,
        ".jpeg": SourceType.IMAGE.value,
        ".webp": SourceType.IMAGE.value,
        ".gif": SourceType.IMAGE.value,
        ".bmp": SourceType.IMAGE.value,
        ".tiff": SourceType.IMAGE.value,
    }
    return mapping.get(ext, SourceType.TXT.value)


@router.post("/spaces", response_model=KnowledgeSpaceResponse, status_code=201)
async def create_space(body: KnowledgeSpaceCreate, session: DBSession, current_user: CurrentUser):
    return await KnowledgeService(session).create_space(current_user, body)


@router.get("/spaces", response_model=PaginatedResponse[KnowledgeSpaceResponse])
async def list_spaces(
    session: DBSession,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
):
    return await KnowledgeService(session).list_spaces(current_user, pagination.page, pagination.size)


@router.get("/spaces/{space_id}", response_model=KnowledgeSpaceResponse)
async def get_space(space_id: uuid.UUID, session: DBSession, current_user: CurrentUser):
    return await KnowledgeService(session).get_space(current_user, space_id)


@router.patch("/spaces/{space_id}", response_model=KnowledgeSpaceResponse)
async def update_space(
    space_id: uuid.UUID,
    body: KnowledgeSpaceUpdate,
    session: DBSession,
    current_user: CurrentUser,
):
    return await KnowledgeService(session).update_space(current_user, space_id, body)


@router.delete("/spaces/{space_id}", response_model=SimpleMessage)
async def delete_space(space_id: uuid.UUID, session: DBSession, current_user: CurrentUser):
    await KnowledgeService(session).delete_space(current_user, space_id)
    return SimpleMessage(detail="Knowledge space deleted")


@router.post("/spaces/{space_id}/sources/text", response_model=SourceResponse, status_code=201)
async def create_text_source(
    space_id: uuid.UUID,
    body: SourceCreateText,
    session: DBSession,
    current_user: CurrentUser,
):
    return await KnowledgeService(session).create_text_source(current_user, space_id, body)


@router.post("/spaces/{space_id}/sources/upload", response_model=SourceResponse, status_code=201)
async def upload_source(
    space_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
):
    data = await file.read()
    filename = file.filename or "upload.txt"
    stype = _detect_type(filename)
    display = name or Path(filename).stem
    return await KnowledgeService(session).create_file_source(
        current_user,
        space_id,
        name=display,
        source_type=stype,
        data=data,
        original_filename=filename,
        mime_type=file.content_type,
    )


@router.get("/spaces/{space_id}/sources", response_model=PaginatedResponse[SourceResponse])
async def list_sources(
    space_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
):
    return await KnowledgeService(session).list_sources(current_user, space_id, pagination.page, pagination.size)


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(source_id: uuid.UUID, session: DBSession, current_user: CurrentUser):
    return await KnowledgeService(session).get_source(current_user, source_id)


@router.delete("/sources/{source_id}", response_model=SimpleMessage)
async def delete_source(source_id: uuid.UUID, session: DBSession, current_user: CurrentUser):
    await KnowledgeService(session).delete_source(current_user, source_id)
    return SimpleMessage(detail="Source deleted")


@router.post("/sources/{source_id}/retry", response_model=SourceResponse)
async def retry_source(source_id: uuid.UUID, session: DBSession, current_user: CurrentUser):
    return await KnowledgeService(session).retry_source(current_user, source_id)


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(body: ConversationCreate, session: DBSession, current_user: CurrentUser):
    return await KnowledgeService(session).create_conversation(current_user, body)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    session: DBSession,
    current_user: CurrentUser,
    space_id: uuid.UUID | None = Query(default=None),
):
    return await KnowledgeService(session).list_conversations(current_user, space_id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(conversation_id: uuid.UUID, session: DBSession, current_user: CurrentUser):
    return await KnowledgeService(session).list_messages(current_user, conversation_id)


@router.post("/conversations/{conversation_id}/messages")
async def post_message(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    session: DBSession,
    current_user: CurrentUser,
):
    async def event_gen():
        async for line in stream_chat_response(
            session, current_user, conversation_id, body.content, body.source_ids
        ):
            yield line

    return StreamingResponse(event_gen(), media_type="application/x-ndjson")


@router.post("/search", response_model=list[SearchHit])
async def search(body: SearchRequest, session: DBSession, current_user: CurrentUser):
    return await KnowledgeService(session).search(
        current_user, body.space_id, body.query, body.source_ids, body.top_k
    )
