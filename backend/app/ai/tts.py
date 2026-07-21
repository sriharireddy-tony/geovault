"""Sarvam AI Text-to-Speech integration (bulbul:v3)."""

import base64
import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "hi-IN": "Hindi",
    "en-IN": "English (India)",
    "bn-IN": "Bengali",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "mr-IN": "Marathi",
    "gu-IN": "Gujarati",
    "pa-IN": "Punjabi",
    "od-IN": "Odia",
}

SPEAKERS = [
    "shubh", "aditya", "ritu", "priya", "neha", "rahul", "pooja",
    "rohan", "simran", "kavya", "amit", "dev", "ishita", "shreya",
]


async def text_to_speech(
    text: str,
    language: str = "en-IN",
    speaker: str = "shubh",
) -> bytes:
    """Convert text to audio bytes using Sarvam AI TTS.

    Returns raw WAV audio bytes.
    Raises httpx.HTTPStatusError on API failure.
    """
    settings = get_settings()
    if not settings.SARVAM_API_KEY:
        raise ValueError("SARVAM_API_KEY not configured")

    payload = {
        "text": text[:2500],
        "target_language_code": language,
        "speaker": speaker,
        "model": "bulbul:v3",
        "output_audio_codec": "wav",
        "speech_sample_rate": "24000",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            settings.SARVAM_TTS_URL,
            headers={
                "api-subscription-key": settings.SARVAM_API_KEY,
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    audio_b64 = data["audios"][0]
    audio_bytes = base64.b64decode(audio_b64)
    logger.info("TTS generated %d bytes for %d chars (%s)", len(audio_bytes), len(text), language)
    return audio_bytes
