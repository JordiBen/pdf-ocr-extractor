# PDF & Image OCR to Text/Markdown (Hebrew, Arabic + 11 languages)

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-1f6feb?logo=apify)](https://apify.com/manageable_gully/pdf-ocr-extractor) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Run it in the cloud with no setup:** [PDF & Image OCR to Text/Markdown (Hebrew, Arabic) on the Apify Store](https://apify.com/manageable_gully/pdf-ocr-extractor).  
> Pay only per result, export to JSON/CSV/Excel, schedule runs and call it from the API.
<!-- Note: the Apify Store page goes live once the Actor is published. -->
<!-- AFFILIATE_LINK_PLACEHOLDER: replace the Apify links above with the affiliate link when available -->

Turn PDFs and images into clean **Markdown or plain text**, with tables. Digital PDF pages are read straight from the text layer (fast, exact, cheap). Only **scanned pages go through OCR** (Tesseract 5). It handles **right-to-left Hebrew and Arabic** properly, including PDFs whose Hebrew text layer is stored backwards.

## Why this one
- **Hybrid extraction:** text layer first, OCR fallback page by page. You pay the OCR price only for scanned pages.
- **RTL done right:** Hebrew and Arabic come out in readable (logical) order, and reversed "visual order" Hebrew text layers are detected and fixed.
- **Tables:** tables in digital PDFs are returned as rows and as Markdown tables, ready for LLM/RAG pipelines.
- **13 OCR languages:** English, Hebrew, Arabic, Russian, German, French, Spanish, Italian, Portuguese, Dutch, Polish, Turkish, Ukrainian. Combine them, e.g. `["heb","eng"]`.
- Formats: PDF, PNG, JPEG, TIFF (multi-page), GIF, BMP, WebP. Up to 50 MB per file.

## Input
```json
{
  "fileUrls": [{"url": "https://example.com/contract.pdf"}],
  "languages": ["eng", "heb"], "mode": "auto", "outputFormat": "markdown", "extractTables": true
}
```
- `mode`: `auto` (recommended), `ocr` (force OCR on every page) or `text` (never OCR).
- `maxPagesPerFile` (default 200), `ocrDpi` (default 300), `includePageDetails` (default true).
- Have local files? Upload them to an Apify key-value store and pass the record URLs.

## Output (one item per file)
```json
{
  "url": "https://example.com/contract.pdf", "pageCount": 12, "ocrPages": 3, "textLayerPages": 9, "tableCount": 2,
  "content": "<!-- page 1 (text) -->\n\nQuarterly Report 2026 ...\n\n| Region | Q2 | Q3 |\n|---|---|---|\n| North | 120 | 150 |",
  "pages": [{"page": 1, "method": "text", "text": "...", "tables": [[["Region","Q2","Q3"],["North","120","150"]]], "ocrConfidence": null}]
}
```

## Pricing
Pay per event:
- **$0.001 per text-layer page** (digital PDFs)
- **$0.006 per OCR page** (scans and images)

For example, a 10-page digital PDF costs $0.01, and a 10-page scan costs $0.06. Failed downloads and unsupported files are not charged. Set "max cost per run" to cap spend; processing stops at the limit and the file is marked `truncated`.

## Good to know
- Processing happens inside the run. Files are not kept beyond the run's default storage retention.
- OCR accuracy depends on scan quality. `ocrConfidence` (0–100) per page helps you spot pages to re-check.
- Handwriting recognition is not supported.

*This Actor was built and is maintained with AI assistance. Report issues on the Issues tab; they are monitored daily.*

## Run from source
This repository is the full source of the [PDF & Image OCR to Text/Markdown (Hebrew, Arabic)](https://apify.com/manageable_gully/pdf-ocr-extractor) Actor.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest
# run locally with the Apify CLI (https://docs.apify.com/cli):
apify run --input '{...}'
```

Deploy your own copy with `apify push`. The easiest way to use it is the hosted version on the [Apify Store](https://apify.com/manageable_gully/pdf-ocr-extractor).

<!-- AFFILIATE_LINK_PLACEHOLDER: "New to Apify? Sign up here" link goes here -->

## License
MIT, see [LICENSE](LICENSE).
