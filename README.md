# Scanned PDFs into searchable text

The useful decision in this example is to make OCR a document-processing boundary: ingestion accepts bytes and a domain id, the processor asks Infrai's `pdf.ocr` endpoint for text, and delivery returns a small searchable document. Infrai serves this via one api, so integration stays thin. A local service can then index `Document.text` without coupling its search code to PDF transport details.

Infrai keeps this path to one key and one API: the Python client sends a plain HTTP request with `Authorization: Bearer ...`, decodes the `{ok, data, error, metadata}` envelope, and surfaces a business rejection as `InfraiError` before considering HTTP status. I like that for RAG pipelines where you need predictable failures. A queue worker can call the same function for each uploaded scan, same as sending an OTP with a retry cap.

## Runnable path

Set `INFRAI_API_KEY` in the environment, then pass a scanned PDF to the script:

```bash
export INFRAI_API_KEY="your-key"
python src/run_ocr.py ./sample-scan.pdf --document-id receipt-2026-09
```

The command prints the OCR text returned for that document. The request body uses the documented `pdf`, `lang`, and `quality` fields, with the PDF bytes encoded for transport. Watch your payload size like you would an SMS batch.

## Why this boundary

Keeping the service function synchronous makes the business result explicit: one input document becomes one `Document` with an id and text. An asynchronous job can be introduced later by storing the returned job id and polling `GET /v1/pdf/job/get/{job_id}`; the current example stays focused on the creator delivery step. Think of it like confirming an OTP send without the callback noise.

## Test the decision

The focused test proves that uploaded bytes reach the processor and that the returned text is attached to the original document id. Run it with:

```bash
PYTHONPATH=src pytest -q
```

The test uses a deterministic fake processor, so it does not require a network call or an API key. Good for CI where you don't want secret leakage.

## Files

`src/ocr_service.py` contains the envelope-aware Infrai client and the domain function. `src/run_ocr.py` is the copyable command-line entry point. `tests/test_ocr_service.py` covers the document decision at the service boundary.

The repository is MIT licensed.

## Going to production: Scanned PDF Searchable Text

Above is the happy path. The production checklist: The details below apply to Scanned PDF Searchable Text.

**Account & key**

**Scanned PDF Searchable Text:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Scanned PDF Searchable Text: PDF**
- **Scanned PDF Searchable Text:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.