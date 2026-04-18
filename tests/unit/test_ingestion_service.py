"""Unit tests for ingestion loaders, validator, hashing, and ParseService."""

import hashlib
import io
from pathlib import Path
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.ingestion.hashing import compute_content_hash
from backend.ingestion.loaders.base import ParsedDocument
from backend.ingestion.loaders.csv import CsvLoader
from backend.ingestion.loaders.html import HtmlLoader
from backend.ingestion.loaders.markdown import MarkdownLoader
from backend.ingestion.loaders.registry import get_loader
from backend.ingestion.loaders.txt import TxtLoader
from backend.ingestion.services import ParseService
from backend.ingestion.validator import (
    MAX_FILE_SIZE_BYTES,
    SUPPORTED_EXTENSIONS,
    validate_file,
)
from backend.core.exceptions import DomainValidationError


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def test_compute_content_hash_returns_sha256():
    content = b"hello world"
    expected = hashlib.sha256(content).hexdigest()
    assert compute_content_hash(content) == expected


def test_compute_content_hash_is_64_hex_chars():
    assert len(compute_content_hash(b"data")) == 64


def test_compute_content_hash_distinct_for_different_content():
    assert compute_content_hash(b"aaa") != compute_content_hash(b"bbb")


def test_compute_content_hash_deterministic():
    assert compute_content_hash(b"x") == compute_content_hash(b"x")


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def test_validate_file_accepts_supported_extension():
    validate_file("report.pdf", size_bytes=1024)


def test_validate_file_accepts_all_supported_extensions():
    for ext in SUPPORTED_EXTENSIONS:
        validate_file(f"file{ext}", size_bytes=100)


def test_validate_file_rejects_unknown_extension():
    with pytest.raises(DomainValidationError, match="Unsupported"):
        validate_file("malware.exe", size_bytes=100)


def test_validate_file_accepts_known_mime_when_ext_unknown():
    validate_file("data.bin", size_bytes=100, content_type="application/pdf")


def test_validate_file_rejects_oversized_file():
    with pytest.raises(DomainValidationError, match="exceeds"):
        validate_file("big.pdf", size_bytes=MAX_FILE_SIZE_BYTES + 1)


def test_validate_file_accepts_exact_max_size():
    validate_file("ok.pdf", size_bytes=MAX_FILE_SIZE_BYTES)


def test_validate_file_rejects_zero_known_type():
    # Zero bytes is fine as long as type is valid
    validate_file("empty.txt", size_bytes=0)


def test_validate_file_rejects_unknown_with_unknown_mime():
    with pytest.raises(DomainValidationError):
        validate_file("file.xyz", size_bytes=100, content_type="application/octet-stream")


# ---------------------------------------------------------------------------
# TxtLoader
# ---------------------------------------------------------------------------


def test_txt_loader_basic():
    loader = TxtLoader()
    doc = loader.load(b"Hello World\nSecond line", "doc.txt")
    assert doc.format == "txt"
    assert "Hello World" in doc.text
    assert doc.title == "Hello World"


def test_txt_loader_title_is_first_nonempty_line():
    loader = TxtLoader()
    doc = loader.load(b"\n\n  First Real Line\nMore", "doc.txt")
    assert doc.title == "First Real Line"


def test_txt_loader_empty_content():
    loader = TxtLoader()
    doc = loader.load(b"", "empty.txt")
    assert doc.text == ""
    assert doc.title is None


def test_txt_loader_latin1_fallback():
    loader = TxtLoader()
    content = "café".encode("latin-1")
    doc = loader.load(content, "latin.txt")
    assert "caf" in doc.text


def test_txt_loader_char_count():
    loader = TxtLoader()
    text = b"Hello"
    doc = loader.load(text, "f.txt")
    assert doc.char_count == 5


# ---------------------------------------------------------------------------
# MarkdownLoader
# ---------------------------------------------------------------------------


def test_markdown_loader_extracts_h1_title():
    loader = MarkdownLoader()
    doc = loader.load(b"# My Report\n\nSome content.", "report.md")
    assert doc.format == "markdown"
    assert doc.title == "My Report"


def test_markdown_loader_extracts_h2_title():
    loader = MarkdownLoader()
    doc = loader.load(b"## Section Title\n\nContent.", "doc.md")
    assert doc.title == "Section Title"


def test_markdown_loader_no_heading():
    loader = MarkdownLoader()
    doc = loader.load(b"Just plain text.", "plain.md")
    assert doc.title is None


def test_markdown_loader_full_text_preserved():
    loader = MarkdownLoader()
    content = b"# Title\n\nParagraph text."
    doc = loader.load(content, "f.md")
    assert "Paragraph text." in doc.text


# ---------------------------------------------------------------------------
# HtmlLoader
# ---------------------------------------------------------------------------


def test_html_loader_strips_tags():
    loader = HtmlLoader()
    doc = loader.load(b"<html><body><p>Hello World</p></body></html>", "page.html")
    assert doc.format == "html"
    assert "Hello World" in doc.text
    assert "<p>" not in doc.text


def test_html_loader_extracts_title_tag():
    loader = HtmlLoader()
    html = b"<html><head><title>My Page</title></head><body>Content</body></html>"
    doc = loader.load(html, "page.html")
    assert doc.title == "My Page"


def test_html_loader_skips_script_content():
    loader = HtmlLoader()
    html = b"<html><body><script>alert('x')</script><p>Real</p></body></html>"
    doc = loader.load(html, "page.html")
    assert "alert" not in doc.text
    assert "Real" in doc.text


def test_html_loader_skips_style_content():
    loader = HtmlLoader()
    html = b"<html><head><style>body{color:red}</style></head><body>Text</body></html>"
    doc = loader.load(html, "page.html")
    assert "color" not in doc.text


def test_html_loader_empty():
    loader = HtmlLoader()
    doc = loader.load(b"<html></html>", "empty.html")
    assert doc.text == ""


# ---------------------------------------------------------------------------
# CsvLoader
# ---------------------------------------------------------------------------


def test_csv_loader_basic():
    loader = CsvLoader()
    doc = loader.load(b"name,age\nAlice,30\nBob,25", "data.csv")
    assert doc.format == "csv"
    assert "Alice" in doc.text
    assert "Bob" in doc.text


def test_csv_loader_title_from_header():
    loader = CsvLoader()
    doc = loader.load(b"first_name,last_name,email\nJohn,Doe,j@d.com", "users.csv")
    assert "first_name" in doc.title or "last_name" in doc.title


def test_csv_loader_empty():
    loader = CsvLoader()
    doc = loader.load(b"", "empty.csv")
    assert doc.text == ""


def test_csv_loader_single_column():
    loader = CsvLoader()
    doc = loader.load(b"word\nhello\nworld", "words.csv")
    assert "hello" in doc.text
    assert "world" in doc.text


# ---------------------------------------------------------------------------
# PdfLoader (mocked)
# ---------------------------------------------------------------------------


def test_pdf_loader_extracts_text():
    from backend.ingestion.loaders.pdf import PdfLoader

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page one text"

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_reader.metadata = None

    with patch("backend.ingestion.loaders.pdf._require_pypdf") as mock_req:
        mock_pypdf = MagicMock()
        mock_pypdf.PdfReader.return_value = mock_reader
        mock_req.return_value = mock_pypdf

        loader = PdfLoader()
        doc = loader.load(b"%PDF fake", "report.pdf")

    assert doc.format == "pdf"
    assert "Page one text" in doc.text
    assert doc.page_count == 1


def test_pdf_loader_extracts_title_from_metadata():
    from backend.ingestion.loaders.pdf import PdfLoader

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Content"

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_reader.metadata = {"/Title": "My PDF Title"}

    with patch("backend.ingestion.loaders.pdf._require_pypdf") as mock_req:
        mock_pypdf = MagicMock()
        mock_pypdf.PdfReader.return_value = mock_reader
        mock_req.return_value = mock_pypdf

        loader = PdfLoader()
        doc = loader.load(b"%PDF fake", "doc.pdf")

    assert doc.title == "My PDF Title"


def test_pdf_loader_missing_sdk_raises():
    from backend.ingestion.loaders import pdf as pdf_module

    original = pdf_module._PYPDF_AVAILABLE
    try:
        with patch.dict("sys.modules", {"pypdf": None}):
            pdf_module._PYPDF_AVAILABLE = None
            with pytest.raises(ImportError, match="pypdf"):
                pdf_module._require_pypdf()
    finally:
        pdf_module._PYPDF_AVAILABLE = original


# ---------------------------------------------------------------------------
# DocxLoader (mocked)
# ---------------------------------------------------------------------------


def test_docx_loader_extracts_paragraphs():
    from backend.ingestion.loaders.docx import DocxLoader

    para1 = MagicMock()
    para1.text = "Introduction"
    para2 = MagicMock()
    para2.text = "First paragraph body."

    mock_doc = MagicMock()
    mock_doc.paragraphs = [para1, para2]
    mock_doc.core_properties.title = ""

    with patch("backend.ingestion.loaders.docx._require_docx") as mock_req:
        mock_docx = MagicMock()
        mock_docx.Document.return_value = mock_doc
        mock_req.return_value = mock_docx

        loader = DocxLoader()
        doc = loader.load(b"PK fake", "report.docx")

    assert doc.format == "docx"
    assert "Introduction" in doc.text
    assert "First paragraph body." in doc.text


def test_docx_loader_uses_core_property_title():
    from backend.ingestion.loaders.docx import DocxLoader

    para = MagicMock()
    para.text = "Some text"

    mock_doc = MagicMock()
    mock_doc.paragraphs = [para]
    mock_doc.core_properties.title = "Core Title"

    with patch("backend.ingestion.loaders.docx._require_docx") as mock_req:
        mock_docx = MagicMock()
        mock_docx.Document.return_value = mock_doc
        mock_req.return_value = mock_docx

        loader = DocxLoader()
        doc = loader.load(b"PK fake", "doc.docx")

    assert doc.title == "Core Title"


def test_docx_loader_missing_sdk_raises():
    from backend.ingestion.loaders import docx as docx_module

    original = docx_module._DOCX_AVAILABLE
    try:
        with patch.dict("sys.modules", {"docx": None}):
            docx_module._DOCX_AVAILABLE = None
            with pytest.raises(ImportError, match="python-docx"):
                docx_module._require_docx()
    finally:
        docx_module._DOCX_AVAILABLE = original


# ---------------------------------------------------------------------------
# Loader registry
# ---------------------------------------------------------------------------


def test_registry_txt_by_extension():
    loader = get_loader("readme.txt")
    assert isinstance(loader, TxtLoader)


def test_registry_md_by_extension():
    loader = get_loader("notes.md")
    assert isinstance(loader, MarkdownLoader)


def test_registry_markdown_extension():
    loader = get_loader("notes.markdown")
    assert isinstance(loader, MarkdownLoader)


def test_registry_html_by_extension():
    loader = get_loader("page.html")
    assert isinstance(loader, HtmlLoader)


def test_registry_htm_by_extension():
    loader = get_loader("page.htm")
    assert isinstance(loader, HtmlLoader)


def test_registry_csv_by_extension():
    loader = get_loader("data.csv")
    assert isinstance(loader, CsvLoader)


def test_registry_pdf_by_mime_fallback():
    from backend.ingestion.loaders.pdf import PdfLoader

    loader = get_loader("upload.bin", content_type="application/pdf")
    assert isinstance(loader, PdfLoader)


def test_registry_docx_by_mime_fallback():
    from backend.ingestion.loaders.docx import DocxLoader

    loader = get_loader(
        "upload.bin",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert isinstance(loader, DocxLoader)


def test_registry_unknown_raises_value_error():
    with pytest.raises(ValueError, match="No loader available"):
        get_loader("malware.exe")


def test_registry_unknown_with_unknown_mime_raises():
    with pytest.raises(ValueError):
        get_loader("data.xyz", content_type="application/octet-stream")


def test_registry_extension_takes_precedence_over_mime():
    # .txt extension → TxtLoader regardless of MIME
    loader = get_loader("file.txt", content_type="application/pdf")
    assert isinstance(loader, TxtLoader)


# ---------------------------------------------------------------------------
# ParseService
# ---------------------------------------------------------------------------


def test_parse_service_parse_txt():
    svc = ParseService()
    doc = svc.parse(b"Hello text", "doc.txt")
    assert isinstance(doc, ParsedDocument)
    assert doc.format == "txt"
    assert "Hello text" in doc.text


def test_parse_service_parse_markdown():
    svc = ParseService()
    doc = svc.parse(b"# Title\n\nContent", "doc.md")
    assert doc.format == "markdown"
    assert doc.title == "Title"


def test_parse_service_parse_html():
    svc = ParseService()
    doc = svc.parse(b"<p>Test</p>", "page.html")
    assert doc.format == "html"


def test_parse_service_parse_csv():
    svc = ParseService()
    doc = svc.parse(b"col1,col2\n1,2", "data.csv")
    assert doc.format == "csv"


def test_parse_service_hash_returns_sha256():
    svc = ParseService()
    content = b"hello"
    assert svc.hash(content) == hashlib.sha256(content).hexdigest()


def test_parse_service_unknown_type_raises():
    svc = ParseService()
    with pytest.raises(ValueError, match="No loader available"):
        svc.parse(b"data", "file.exe")


@pytest.mark.asyncio
async def test_parse_service_find_duplicate_returns_match():
    import uuid

    svc = ParseService()
    ws_id = uuid.uuid4()
    hash_val = "abc123"

    mock_doc = MagicMock()
    mock_doc.workspace_id = ws_id

    mock_repo = MagicMock()
    mock_repo.get_by_content_hash = AsyncMock(return_value=mock_doc)

    with patch(
        "backend.repositories.document_repository.DocumentRepository",
        return_value=mock_repo,
    ):
        result = await svc.find_duplicate(MagicMock(), ws_id, hash_val)

    assert result is mock_doc


@pytest.mark.asyncio
async def test_parse_service_find_duplicate_returns_none_for_different_workspace():
    import uuid

    svc = ParseService()
    ws_id = uuid.uuid4()
    other_ws = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc.workspace_id = other_ws  # different workspace

    mock_repo = MagicMock()
    mock_repo.get_by_content_hash = AsyncMock(return_value=mock_doc)

    with patch(
        "backend.repositories.document_repository.DocumentRepository",
        return_value=mock_repo,
    ):
        result = await svc.find_duplicate(MagicMock(), ws_id, "abc123")

    assert result is None


@pytest.mark.asyncio
async def test_parse_service_find_duplicate_returns_none_when_not_found():
    import uuid

    svc = ParseService()

    mock_repo = MagicMock()
    mock_repo.get_by_content_hash = AsyncMock(return_value=None)

    with patch(
        "backend.repositories.document_repository.DocumentRepository",
        return_value=mock_repo,
    ):
        result = await svc.find_duplicate(MagicMock(), uuid.uuid4(), "nohash")

    assert result is None
