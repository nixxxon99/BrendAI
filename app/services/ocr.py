# app/services/ocr.py
from __future__ import annotations
import io, os
from typing import Optional, List
from PIL import Image

def _try_google_vision(image_bytes: bytes) -> Optional[str]:
    try:
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.text_detection(image=image)
        if response and response.text_annotations:
            return response.text_annotations[0].description or ""
        return None
    except Exception:
        return None

def _try_tesseract(image_bytes: bytes) -> Optional[str]:
    try:
        import pytesseract
        img = Image.open(io.BytesIO(image_bytes))
        txt = pytesseract.image_to_string(img, lang="eng+rus")
        return txt or None
    except Exception:
        return None

def extract_text(image_bytes: bytes) -> str:
    # 1) Google Vision if credentials are valid
    txt = _try_google_vision(image_bytes)
    if txt:
        return txt.strip()

    # 2) Fallback to Tesseract if available
    txt = _try_tesseract(image_bytes)
    if txt:
        return txt.strip()

    # 3) Nothing worked
    return ""
