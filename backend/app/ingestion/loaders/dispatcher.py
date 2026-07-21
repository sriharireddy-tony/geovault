"""Dispatch knowledge source types to the matching LangChain loader."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from app.ingestion.loaders import audio, image, office, pdf, tabular, text


def load_documents(
    *,
    source_type: str,
    path: Path | None = None,
    raw_text: str | None = None,
) -> list[Document]:
    stype = (source_type or "").upper()

    if stype == "TEXT":
        return text.load_inline_text(raw_text)

    if path is None or not path.is_file():
        raise FileNotFoundError(f"File not found for source type {stype}")

    if stype in {"TXT", "MARKDOWN"}:
        return text.load_text_file(path, source_type=stype)
    if stype == "PDF":
        return pdf.load_pdf(path)
    if stype == "DOCX":
        return office.load_docx(path)
    if stype == "CSV":
        return tabular.load_csv(path)
    if stype == "XLSX":
        return tabular.load_xlsx(path)
    if stype == "IMAGE":
        return image.load_image(path)
    if stype == "AUDIO":
        return audio.load_audio(path)

    raise ValueError(f"Unsupported source type for LangChain loaders: {stype}")
