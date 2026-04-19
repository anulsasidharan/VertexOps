"""Pydantic schemas for the Documents API."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentRegisterRequest(BaseModel):
    title: Optional[str] = None
    source_uri: Optional[str] = None
    format: Optional[str] = None
    language: Optional[str] = None
    doc_metadata: Optional[dict[str, Any]] = None


class PrepareUploadRequest(BaseModel):
    filename: str
    content_type: str = "application/octet-stream"
    title: Optional[str] = None
    format: Optional[str] = None
    language: Optional[str] = None
    expires_in: int = Field(default=3600, ge=60, le=86400)


class CompleteUploadRequest(BaseModel):
    content_hash: Optional[str] = None


class DocumentResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: Optional[str]
    source_uri: Optional[str]
    format: Optional[str]
    language: Optional[str]
    content_hash: Optional[str]
    ingest_status: str
    doc_metadata: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    limit: int
    offset: int


class PrepareUploadResponse(BaseModel):
    document_id: UUID
    upload_url: str
    storage_key: str
    storage_uri: str
    method: str
    headers: dict[str, str]
    expires_in: int
