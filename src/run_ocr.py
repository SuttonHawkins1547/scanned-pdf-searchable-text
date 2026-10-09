import argparse
from pathlib import Path

from ocr_service import InfraiPdfClient, ingest_scanned_document


def main() -> None:
    parser = argparse.ArgumentParser(description="OCR a scanned PDF into searchable text")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--document-id", default="scan-001")
    args = parser.parse_args()
    document = ingest_scanned_document(args.document_id, args.pdf.read_bytes(), InfraiPdfClient())
    print(document.text)


if __name__ == "__main__":
    main()
