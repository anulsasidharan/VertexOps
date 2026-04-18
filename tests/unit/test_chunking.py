"""Unit tests for chunking strategies and registry."""

import uuid

import pytest

from backend.chunking.base import ChunkResult
from backend.chunking.registry import ChunkingConfig, get_chunker
from backend.chunking.service import ChunkingService
from backend.chunking.strategies.code import CodeChunker
from backend.chunking.strategies.fixed import FixedSizeChunker
from backend.chunking.strategies.markdown import MarkdownChunker
from backend.chunking.strategies.recursive import RecursiveChunker


# ---------------------------------------------------------------------------
# FixedSizeChunker
# ---------------------------------------------------------------------------


def test_fixed_basic_split():
    c = FixedSizeChunker(chunk_size=10, chunk_overlap=2)
    chunks = c.chunk("0123456789ABCDE")
    assert len(chunks) >= 2
    assert chunks[0].text == "0123456789"
    assert chunks[0].chunk_index == 0


def test_fixed_overlap_restarts_correctly():
    c = FixedSizeChunker(chunk_size=10, chunk_overlap=3)
    chunks = c.chunk("0123456789ABCDEFGHIJ")
    assert chunks[1].start_char == 7


def test_fixed_empty_text_returns_empty():
    assert FixedSizeChunker().chunk("") == []
    assert FixedSizeChunker().chunk("   ") == []


def test_fixed_short_text_single_chunk():
    c = FixedSizeChunker(chunk_size=100, chunk_overlap=10)
    chunks = c.chunk("Hello world")
    assert len(chunks) == 1
    assert chunks[0].text == "Hello world"


def test_fixed_chunk_index_sequential():
    c = FixedSizeChunker(chunk_size=5, chunk_overlap=0)
    chunks = c.chunk("ABCDEABCDEABCDE")
    for i, ch in enumerate(chunks):
        assert ch.chunk_index == i


def test_fixed_token_count_populated():
    c = FixedSizeChunker(chunk_size=20, chunk_overlap=0)
    chunks = c.chunk("Hello world test data")
    assert all(ch.token_count is not None and ch.token_count > 0 for ch in chunks)


def test_fixed_start_end_chars_correct():
    text = "ABCDEFGHIJ"
    c = FixedSizeChunker(chunk_size=5, chunk_overlap=0)
    chunks = c.chunk(text)
    assert chunks[0].start_char == 0
    assert chunks[0].end_char == 5
    assert chunks[1].start_char == 5
    assert chunks[1].end_char == 10


def test_fixed_overlap_invalid_raises():
    with pytest.raises(ValueError):
        FixedSizeChunker(chunk_size=10, chunk_overlap=10)


# ---------------------------------------------------------------------------
# RecursiveChunker
# ---------------------------------------------------------------------------


def test_recursive_splits_paragraphs_first():
    text = "Para one.\n\nPara two.\n\nPara three."
    c = RecursiveChunker(chunk_size=50, chunk_overlap=0)
    chunks = c.chunk(text)
    assert len(chunks) >= 1
    combined = " ".join(ch.text for ch in chunks)
    assert "Para one" in combined
    assert "Para three" in combined


def test_recursive_merges_short_pieces():
    text = "a\n\nb\n\nc"
    c = RecursiveChunker(chunk_size=100, chunk_overlap=0)
    chunks = c.chunk(text)
    # All three pieces should be merged into one or two
    assert len(chunks) <= 2


def test_recursive_empty_returns_empty():
    assert RecursiveChunker().chunk("") == []


def test_recursive_long_text_splits():
    text = "word " * 200  # 1000 chars
    c = RecursiveChunker(chunk_size=100, chunk_overlap=10)
    chunks = c.chunk(text)
    assert len(chunks) > 1
    for ch in chunks:
        assert len(ch.text) <= 110  # size + small tolerance


def test_recursive_chunk_index_sequential():
    text = "\n\n".join([f"Paragraph {i}" for i in range(10)])
    c = RecursiveChunker(chunk_size=50, chunk_overlap=0)
    chunks = c.chunk(text)
    for i, ch in enumerate(chunks):
        assert ch.chunk_index == i


def test_recursive_custom_separators():
    text = "A|B|C|D|E"
    c = RecursiveChunker(chunk_size=5, chunk_overlap=0, separators=["|"])
    chunks = c.chunk(text)
    assert len(chunks) >= 2


# ---------------------------------------------------------------------------
# MarkdownChunker
# ---------------------------------------------------------------------------


def test_markdown_splits_at_heading():
    md = "# Introduction\n\nThis is the intro.\n\n## Methods\n\nThis is methods."
    c = MarkdownChunker(chunk_size=200, chunk_overlap=0)
    chunks = c.chunk(md)
    assert any(ch.section_path == "Introduction" for ch in chunks)
    assert any(ch.section_path == "Methods" for ch in chunks)


def test_markdown_no_headings_falls_back_to_single_chunk():
    text = "Just plain text without any headers."
    c = MarkdownChunker(chunk_size=200, chunk_overlap=0)
    chunks = c.chunk(text)
    assert len(chunks) == 1


def test_markdown_large_section_is_split():
    section_content = "word " * 200  # ~1000 chars
    md = f"# BigSection\n\n{section_content}"
    c = MarkdownChunker(chunk_size=100, chunk_overlap=0)
    chunks = c.chunk(md)
    assert len(chunks) > 1
    for ch in chunks:
        assert ch.section_path == "BigSection"


def test_markdown_empty_returns_empty():
    assert MarkdownChunker().chunk("") == []
    assert MarkdownChunker().chunk("   ") == []


def test_markdown_chunk_index_sequential():
    md = "\n\n".join([f"## Section {i}\n\nContent {i}." for i in range(5)])
    c = MarkdownChunker(chunk_size=200, chunk_overlap=0)
    chunks = c.chunk(md)
    for i, ch in enumerate(chunks):
        assert ch.chunk_index == i


# ---------------------------------------------------------------------------
# CodeChunker
# ---------------------------------------------------------------------------


def test_code_splits_at_double_newlines():
    code = "def foo():\n    return 1\n\n\ndef bar():\n    return 2"
    c = CodeChunker(chunk_size=200, chunk_overlap=0)
    chunks = c.chunk(code)
    assert len(chunks) >= 1
    combined = "\n".join(ch.text for ch in chunks)
    assert "foo" in combined
    assert "bar" in combined


def test_code_merges_small_blocks():
    code = "x = 1\n\ny = 2\n\nz = 3"
    c = CodeChunker(chunk_size=200, chunk_overlap=0)
    chunks = c.chunk(code)
    assert len(chunks) == 1


def test_code_splits_oversized_block():
    # One big block with no double newlines
    code = "x = " + "a" * 1000
    c = CodeChunker(chunk_size=100, chunk_overlap=0)
    chunks = c.chunk(code)
    assert len(chunks) > 1


def test_code_empty_returns_empty():
    assert CodeChunker().chunk("") == []


def test_code_chunk_index_sequential():
    blocks = "\n\n\n".join([f"def f{i}():\n    pass" for i in range(5)])
    c = CodeChunker(chunk_size=50, chunk_overlap=0)
    chunks = c.chunk(blocks)
    for i, ch in enumerate(chunks):
        assert ch.chunk_index == i


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_registry_returns_fixed():
    config = ChunkingConfig(strategy="fixed")
    chunker = get_chunker(config)
    assert isinstance(chunker, FixedSizeChunker)


def test_registry_returns_recursive():
    config = ChunkingConfig(strategy="recursive")
    chunker = get_chunker(config)
    assert isinstance(chunker, RecursiveChunker)


def test_registry_returns_markdown():
    config = ChunkingConfig(strategy="markdown")
    chunker = get_chunker(config)
    assert isinstance(chunker, MarkdownChunker)


def test_registry_returns_code():
    config = ChunkingConfig(strategy="code")
    chunker = get_chunker(config)
    assert isinstance(chunker, CodeChunker)


def test_registry_unknown_raises():
    with pytest.raises(ValueError, match="Unknown"):
        config = ChunkingConfig(strategy="unknown")  # type: ignore[arg-type]
        get_chunker(config)


def test_registry_passes_chunk_size():
    config = ChunkingConfig(strategy="fixed", chunk_size=256, chunk_overlap=32)
    chunker = get_chunker(config)
    assert chunker.chunk_size == 256  # type: ignore[attr-defined]


def test_registry_passes_separators():
    config = ChunkingConfig(strategy="recursive", separators=["|", ","])
    chunker = get_chunker(config)
    assert chunker.separators == ["|", ","]  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# ChunkingService
# ---------------------------------------------------------------------------


def test_service_returns_chunk_models():
    svc = ChunkingService()
    doc_id = uuid.uuid4()
    config = ChunkingConfig(strategy="fixed", chunk_size=20, chunk_overlap=0)
    chunks = svc.chunk_document(doc_id, "Hello world. This is test content.", config)
    assert len(chunks) >= 1
    assert all(hasattr(c, "document_id") for c in chunks)
    assert all(c.document_id == doc_id for c in chunks)


def test_service_empty_text_returns_empty():
    svc = ChunkingService()
    result = svc.chunk_document(uuid.uuid4(), "", ChunkingConfig())
    assert result == []


def test_service_preserves_chunk_index_order():
    svc = ChunkingService()
    text = "word " * 100
    config = ChunkingConfig(strategy="fixed", chunk_size=50, chunk_overlap=0)
    chunks = svc.chunk_document(uuid.uuid4(), text, config)
    for i, ch in enumerate(chunks):
        assert ch.chunk_index == i


def test_service_filters_whitespace_chunks():
    svc = ChunkingService()
    config = ChunkingConfig(strategy="fixed", chunk_size=5, chunk_overlap=0)
    chunks = svc.chunk_document(uuid.uuid4(), "     ", config)
    assert chunks == []


def test_service_section_path_preserved_for_markdown():
    svc = ChunkingService()
    md = "# MySection\n\nContent here."
    config = ChunkingConfig(strategy="markdown", chunk_size=200, chunk_overlap=0)
    chunks = svc.chunk_document(uuid.uuid4(), md, config)
    assert any(ch.section_path == "MySection" for ch in chunks)
