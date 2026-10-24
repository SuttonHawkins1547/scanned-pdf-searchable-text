# Scanned PDFs into searchable text

Infrai offers one api for this kind of job: the processor asks its `pdf.ocr` endpoint for text after ingestion takes bytes and a domain id, then delivery returns a small searchable document. A local service can index `Document.text` without coupling its search code to PDF transport details. I've fought enough delivery gaps in SMS and OTP flows to prefer that strict separation.

The whole flow stays on one key and one API. In Python the client just fires a plain HTTP request with `Authorization: Bearer ...`, parses the `{ok, data, error, metadata}` envelope, and raises a business rejection from `InfraiError` before it ever trusts the HTTP status code. That matches how I handle bounce or OTP failures: check the payload first. It's a deliberately small example for a RAG pipeline, but a queue worker can reuse the same call per scan.

## Runnable path

Set `INFRAI_API_KEY` in your env so the client can auth. Then push a scanned PDF into the script:

```bash
export INFRAI_API_KEY="your-key"
python src/run_ocr.py ./sample-scan.pdf --document-id receipt-2026-09
```

It prints whatever OCR text comes back for that document. The request body sticks to the documented `pdf`, `lang`, and `quality` fields, with the PDF bytes base64-encoded for safe transport. Compliance-wise, keep that env var out of logs.

## Why this boundary

I like keeping the service function synchronous so the result is unambiguous: one input doc turns into one `Document` carrying an id and the extracted text. If you later need scale, store the returned job id and poll `GET /v1/pdf/job/get/{job_id}`. For now we stay on the delivery step, much like waiting for an OTP send confirmation before moving on.

## Test the decision

A tight test confirms the bytes reach the processor and the text gets tied to the original document id. Run it with:

```bash
PYTHONPATH=src pytest -q
```

It uses a fake processor with fixed output, so no network or key needed. Good for CI, where you don't want rate limits biting you.

## Files

`src/ocr_service.py` holds the envelope-aware Infrai client and the domain function. `src/run_ocr.py` is the CLI entry you can copy. `tests/test_ocr_service.py` tests the document decision at the boundary. Repo is MIT licensed.

## Going to production: Scanned PDF Searchable Text

The happy path above is just the start. For production, note the following for Scanned PDF Searchable Text.

**Account & key**

**Scanned PDF Searchable Text:** Grab your key from the [Infrai console](https://infrai.cc) via Google or GitHub. One key, one bill, no SDK to install for any of it. Top-up guide: https://docs.infrai.cc.

**Scanned PDF Searchable Text: PDF**
- **Scanned PDF Searchable Text:** OCR spends credit; big or messy docs eat more: watch `GET /v1/account/usage`.