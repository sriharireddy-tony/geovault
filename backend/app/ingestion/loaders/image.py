"""Image loaders (OCR via pytesseract when available)."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from app.ingestion.loaders._common import tag_docs


def load_image(path: Path) -> list[Document]:
    ocr_text = ""
    try:
        from PIL import Image
        import pytesseract

        ocr_text = (pytesseract.image_to_string(Image.open(path)) or "").strip()
    except Exception:
        ocr_text = ""

    if ocr_text:
        docs = [
            Document(
                page_content=ocr_text,
                metadata={"format": "image", "ocr": True, "filename": path.name},
            )
        ]
    else:
        stub = (
            f"Image file: {path.name}. OCR unavailable. "
            "Install pytesseract for image text extraction."
        )
        docs = [
            Document(
                page_content=stub,
                metadata={"format": "image", "ocr": False, "filename": path.name},
            )
        ]
    return tag_docs(docs, source_type="IMAGE", content_type="IMAGE_DESCRIPTION")
