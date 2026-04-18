"""Documents API — register, upload, list, retrieve, and delete documents."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_current_user
from backend.api.dependencies.auth import AuthContext
from backend.core.db import get_db
from backend.core.exceptions import ForbiddenError
from backend.ingestion.schemas import (
    CompleteUploadRequest,
    DocumentListResponse,
    DocumentRegisterRequest,
    DocumentResponse,
    PrepareUploadRequest,
    PrepareUploadResponse,
)
from backend.ingestion.services import DocumentService

router = APIRouter()


def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    return DocumentService(db)


def _workspace_id(auth: AuthContext) -> UUID:
    if auth.workspace_id is None:
        raise ForbiddenError("This endpoint requires a workspace-scoped token.")
    return auth.workspace_id


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def register_document(
    req: DocumentRegisterRequest,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    svc: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    doc = await svc.register(_workspace_id(auth), req)
    return DocumentResponse.model_validate(doc)


@router.post(
    "/upload-url",
    response_model=PrepareUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def prepare_upload(
    req: PrepareUploadRequest,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    svc: DocumentService = Depends(get_document_service),
) -> PrepareUploadResponse:
    doc, spec = await svc.prepare_upload(_workspace_id(auth), req)
    return PrepareUploadResponse(
        document_id=doc.id,
        upload_url=spec.upload_url,
        storage_key=spec.storage_key,
        storage_uri=spec.storage_uri,
        method=spec.method,
        headers=spec.headers,
        expires_in=spec.expires_in,
    )


@router.post("/{document_id}/complete", response_model=DocumentResponse)
async def complete_upload(
    document_id: UUID,
    req: CompleteUploadRequest,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    svc: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    doc = await svc.complete_upload(_workspace_id(auth), document_id, req)
    return DocumentResponse.model_validate(doc)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    auth: Annotated[AuthContext, Depends(get_current_user)],
    svc: DocumentService = Depends(get_document_service),
    status_filter: Annotated[Optional[str], Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DocumentListResponse:
    items, total = await svc.list(_workspace_id(auth), status_filter, limit, offset)
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    svc: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    doc = await svc.get(_workspace_id(auth), document_id)
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    auth: Annotated[AuthContext, Depends(get_current_user)],
    svc: DocumentService = Depends(get_document_service),
) -> Response:
    await svc.delete(_workspace_id(auth), document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
