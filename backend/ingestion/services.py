"""Ingestion services — document CRUD and file parsing/deduplication."""

import uuid
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import ForbiddenError, NotFoundError
from backend.ingestion.hashing import compute_content_hash
from backend.ingestion.loaders import ParsedDocument, get_loader
from backend.ingestion.schemas import (
    CompleteUploadRequest,
    DocumentRegisterRequest,
    PrepareUploadRequest,
)
from backend.ingestion.storage.base import UploadSpec, document_storage_key
from backend.ingestion.storage.service import get_storage_backend
from backend.models.document import Document
from backend.repositories.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = DocumentRepository(session)
        self._storage = get_storage_backend()

    async def register(
        self,
        workspace_id: uuid.UUID,
        req: DocumentRegisterRequest,
    ) -> Document:
        doc = Document(
            workspace_id=workspace_id,
            title=req.title,
            source_uri=req.source_uri,
            format=req.format,
            language=req.language,
            ingest_status="pending",
            doc_metadata=req.doc_metadata,
        )
        return await self._repo.add(doc)

    async def prepare_upload(
        self,
        workspace_id: uuid.UUID,
        req: PrepareUploadRequest,
    ) -> Tuple[Document, UploadSpec]:
        doc_id = uuid.uuid4()
        storage_key = document_storage_key(workspace_id, doc_id, req.filename)
        spec = await self._storage.prepare_upload(
            storage_key, req.content_type, expires_in=req.expires_in
        )
        doc = Document(
            id=doc_id,
            workspace_id=workspace_id,
            title=req.title or req.filename,
            format=req.format,
            language=req.language,
            ingest_status="pending",
            doc_metadata={"storage_key": storage_key, "filename": req.filename},
        )
        doc = await self._repo.add(doc)
        return doc, spec

    async def complete_upload(
        self,
        workspace_id: uuid.UUID,
        document_id: uuid.UUID,
        req: CompleteUploadRequest,
    ) -> Document:
        doc = await self._get_owned(workspace_id, document_id)
        doc.ingest_status = "uploaded"
        if req.content_hash:
            doc.content_hash = req.content_hash
        await self._repo.session.flush()
        await self._repo.session.refresh(doc)
        return doc

    async def get(self, workspace_id: uuid.UUID, document_id: uuid.UUID) -> Document:
        return await self._get_owned(workspace_id, document_id)

    async def list(
        self,
        workspace_id: uuid.UUID,
        status: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[Document], int]:
        if status:
            total = await self._repo.count_by_workspace_and_status(workspace_id, status)
            items = await self._repo.list_by_workspace_and_status_paginated(
                workspace_id, status, offset, limit
            )
        else:
            total = await self._repo.count_by_workspace(workspace_id)
            items = await self._repo.list_by_workspace_paginated(workspace_id, offset, limit)
        return items, total

    async def delete(self, workspace_id: uuid.UUID, document_id: uuid.UUID) -> None:
        doc = await self._get_owned(workspace_id, document_id)
        storage_key = (doc.doc_metadata or {}).get("storage_key")
        await self._repo.delete(doc)
        if storage_key:
            try:
                await self._storage.delete(storage_key)
            except Exception:
                pass  # best-effort; DB record is already gone

    async def _get_owned(
        self, workspace_id: uuid.UUID, document_id: uuid.UUID
    ) -> Document:
        doc = await self._repo.get(document_id)
        if doc is None:
            raise NotFoundError(f"Document {document_id} not found.")
        if doc.workspace_id != workspace_id:
            raise ForbiddenError("Document does not belong to this workspace.")
        return doc


# ---------------------------------------------------------------------------
# ParseService — file parsing, metadata extraction, and deduplication
# ---------------------------------------------------------------------------


class ParseService:
    """Parse raw file bytes and support content-hash deduplication."""

    def parse(
        self,
        content: bytes,
        filename: str,
        content_type: Optional[str] = None,
    ) -> ParsedDocument:
        """Return a ParsedDocument by dispatching to the appropriate loader.

        Raises ValueError when no loader supports the file type.
        """
        loader = get_loader(filename, content_type)
        return loader.load(content, filename)

    def hash(self, content: bytes) -> str:
        """Return the SHA-256 hex digest of *content*."""
        return compute_content_hash(content)

    async def find_duplicate(
        self,
        session: AsyncSession,
        workspace_id: uuid.UUID,
        content_hash: str,
    ) -> Optional["Document"]:
        """Return an existing Document in *workspace_id* with *content_hash*, or None."""
        from backend.repositories.document_repository import DocumentRepository

        repo = DocumentRepository(session)
        doc = await repo.get_by_content_hash(content_hash)
        if doc is not None and doc.workspace_id == workspace_id:
            return doc
        return None
