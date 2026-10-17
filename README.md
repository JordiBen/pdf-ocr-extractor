# OCR PDF Extractor: PDF to Text, Image to Text & PDF to Markdown (Hebrew, Arabic + 11 languages)

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-1f6feb?logo=apify)](https://apify.com/manageable_gully/pdf-ocr-extractor) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Run it in the cloud with no setup:** [OCR PDF Extractor: Image to Text, PDF to Markdown & Tables on the Apify Store](https://apify.com/manageable_gully/pdf-ocr-extractor).  
> Pay only per result, export to JSON/CSV/Excel, schedule runs and call it from the API.
<!-- AFFILIATE_LINK_PLACEHOLDER: replace the Apify links above with the affiliate link when available -->

Turn PDFs and images into clean **Markdown or plain text**, with tables. Digital PDF pages are read straight from the text layer (fast, exact, cheap). Only **scanned pages go through OCR** (Tesseract 5). It handles **right-to-left Hebrew and Arabic** properly, including PDFs whose Hebrew text layer is stored backwards.

## What you can use it for
- **RAG and LLM pipelines:** turn PDFs into clean Markdown with tables, ready for chunking and embeddings.
- **Document processing:** extract text from scanned contracts, invoices and letters (image to text OCR) into JSON.
- **Hebrew and Arabic documents:** get readable right-to-left text, including PDFs whose Hebrew text layer is stored backwards.
- **Data entry automation:** pull tables out of digital PDF reports as rows you can load into a spreadsheet.
- **Archives:** batch-convert hundreds of PDFs or TIFF scans into searchable text.

## How to use it
1. Add PDF or image URLs under **File URLs** (or upload files to an Apify key-value store and paste the record URLs).
2. Pick the OCR **languages**, e.g. `eng` + `heb`.
3. Keep **mode** on `auto`: the text layer is used where it exists and OCR only where it doesn't.
4. Click **Start** and download Markdown, text or JSON.

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

## Good to know
- Processing happens inside the run. Files are not kept beyond the run's default storage retention.
- OCR accuracy depends on scan quality. `ocrConfidence` (0–100) per page helps you spot pages to re-check.
- Handwriting recognition is not supported.

## Pricing
Pay per event, no monthly rent:
- **$0.001 per text-layer page** (digital PDFs)
- **$0.006 per OCR page** (scans and images)
- $0.002 per run start

| Example | Cost |
|---|---|
| A 10-page digital PDF | $0.012 |
| A 10-page scanned PDF | $0.062 |
| 1,000 digital pages | $1.00 |
| 1,000 scanned pages | $6.00 |

Failed downloads and unsupported files are not charged.

You can set a **maximum cost per run** in the run options; the Actor stops cleanly when it is reached. New to Apify? The free plan includes $5 of platform credit every month, so you can try this Actor at no cost.

## API, integrations and AI agents (MCP)
Run it from your own code with the [Apify API](https://docs.apify.com/api/v2) and get the results in one call:
```bash
curl -X POST "https://api.apify.com/v2/acts/manageable_gully~pdf-ocr-extractor/run-sync-get-dataset-items?token=<YOUR_APIFY_TOKEN>" \
  -H "Content-Type: application/json" -d @input.json
```
```python
from apify_client import ApifyClient
run = ApifyClient("<YOUR_APIFY_TOKEN>").actor("manageable_gully/pdf-ocr-extractor").call(run_input={...})
```
- **No-code:** use the Apify app in **n8n, Make or Zapier** ("Run Actor", then "Get dataset items"), or send results to Google Sheets, Slack or a webhook.
- **AI agents (MCP):** add `https://mcp.apify.com?tools=manageable_gully/pdf-ocr-extractor` to Claude, Cursor, VS Code or any MCP client and the agent can call this Actor as a tool.
- **Schedules:** run it hourly, daily or weekly from Apify Console.

## FAQ
**Does it read handwriting?** No. Tesseract OCR handles printed text. Handwriting is not supported.

**Can I convert a PDF to Markdown for ChatGPT or Claude?** Yes. Set `outputFormat` to `markdown`. Headings, paragraphs and tables are preserved, and each page is marked so you can cite page numbers.

**What image formats are supported?** PNG, JPEG, TIFF (including multi-page), GIF, BMP and WebP, plus PDF. Up to 50 MB per file.

**Can AI agents use it?** Yes. It is available as a tool through the Apify MCP server (`https://mcp.apify.com?tools=manageable_gully/pdf-ocr-extractor`) and the Apify API, and it returns structured JSON that agents can read directly.

## More tools from WebIntel Tools
- [Web Page to Markdown](https://apify.com/manageable_gully/page-to-markdown): clean Markdown and RAG chunks from any URL, for LLMs
- [Website Screenshot & URL to PDF](https://apify.com/manageable_gully/url-to-pdf-screenshot): full-page screenshots and PDFs of URLs or your own HTML
- [RSS Feed Reader & Monitor](https://apify.com/manageable_gully/rss-feed-reader): read and monitor RSS, Atom and JSON feeds, only new items

See [all WebIntel Tools Actors](https://apify.com/manageable_gully).

*Made by WebIntel Tools. This Actor was built and is maintained with AI assistance. Report issues on the Issues tab; they are monitored daily.*

## Run from source
This repository is the full source of the [OCR PDF Extractor: Image to Text, PDF to Markdown & Tables](https://apify.com/manageable_gully/pdf-ocr-extractor) Actor.

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
