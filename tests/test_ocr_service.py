from ocr_service import Document, ingest_scanned_document


class FakeClient:
    def __init__(self):
        self.received = None

    def ocr(self, pdf_bytes):
        self.received = pdf_bytes
        return {"text": "Invoice 42\nTotal 18.50"}


def test_ingestion_returns_searchable_document_text():
    client = FakeClient()
    result = ingest_scanned_document("invoice-42", b"pdf bytes", client)
    assert result == Document("invoice-42", "Invoice 42\nTotal 18.50")
    assert client.received == b"pdf bytes"
