from app.utils.storage import MEDIA_ROOT

KNOWLEDGE_DIR = MEDIA_ROOT / "knowledge"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


def save_knowledge_file(data: bytes, original_name: str, source_id: str) -> str:
    from pathlib import Path
    ext = Path(original_name).suffix.lower() or ".bin"
    filename = f"{source_id}{ext}"
    path = KNOWLEDGE_DIR / filename
    path.write_bytes(data)
    return f"/media/knowledge/{filename}"


def resolve_storage_path(storage_key: str):
    from pathlib import Path
    rel = storage_key.lstrip("/").replace("\\", "/")
    # storage_key like /media/knowledge/uuid.pdf → media/knowledge/uuid.pdf
    candidate = Path(rel)
    if candidate.is_file():
        return candidate
    # fallback under MEDIA_ROOT parent
    alt = Path("media") / Path(rel).name if "knowledge" not in rel else Path(rel)
    if alt.is_file():
        return alt
    return candidate
