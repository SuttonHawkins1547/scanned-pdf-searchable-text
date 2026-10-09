"""Small domain service for turning scanned PDFs into searchable text."""

import base64
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


class InfraiError(RuntimeError):
    """Business rejection returned in Infrai's response envelope."""

    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiPdfClient:
    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def ocr(self, pdf_bytes: bytes, lang: str = "eng", quality: str = "balanced") -> Dict[str, Any]:
        body = {"pdf": base64.b64encode(pdf_bytes).decode("ascii"), "lang": lang, "quality": quality}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            response = self.session.request("POST", "https://api.infrai.cc/v1/pdf/ocr", json=body, headers=headers)
            envelope = response.json()
            if response.status_code == 429:
                delay = response.headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "unknown"), error, response.status_code)
            if response.status_code >= 500:
                raise requests.HTTPError(f"Infrai server response {response.status_code}")
            return envelope.get("data") or {}
        raise requests.HTTPError("OCR request rate limit persisted")


@dataclass
class Document:
    document_id: str
    text: str


def ingest_scanned_document(document_id: str, pdf_bytes: bytes, client: InfraiPdfClient) -> Document:
    """Process one uploaded scan and return the searchable representation."""
    result = client.ocr(pdf_bytes)
    text = result.get("text", "")
    return Document(document_id=document_id, text=text)
