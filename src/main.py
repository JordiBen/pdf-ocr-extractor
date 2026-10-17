"""Apify entrypoint: PDF & image to text / Markdown with OCR (incl. Hebrew & Arabic) and table extraction."""
from __future__ import annotations

import asyncio
import os

import httpx
from apify import Actor

from .extract import (SUPPORTED_LANGS, DocumentError, ExtractOptions, available_languages, download, iter_pages,
                      to_markdown)

EVENT_TEXT = 'text-page'
EVENT_OCR = 'ocr-page'
_SENTINEL = object()


def parse_input(inp: dict) -> tuple[list[str], ExtractOptions, str]:
    urls = []
    for s in inp.get('fileUrls') or []:
        u = (s.get('url') if isinstance(s, dict) else s) or ''
        u = u.strip()
        if u and u not in urls:
            urls.append(u)
    if not urls:
        raise ValueError('Provide at least one file URL in "fileUrls".')
    langs = tuple(dict.fromkeys(inp.get('languages') or ['eng']))
    bad = [l for l in langs if l not in SUPPORTED_LANGS]
    if bad:
        raise ValueError(f'Unsupported OCR language(s): {bad}. Supported: {SUPPORTED_LANGS}')
    mode = inp.get('mode', 'auto')
    if mode not in ('auto', 'ocr', 'text'):
        raise ValueError('mode must be auto, ocr or text')
    fmt = inp.get('outputFormat', 'markdown')
    if fmt not in ('markdown', 'text'):
        raise ValueError('outputFormat must be markdown or text')
    opts = ExtractOptions(languages=langs, mode=mode, extract_tables=bool(inp.get('extractTables', True)),
                          max_pages=int(min(max(inp.get('maxPagesPerFile', 200), 1), 2000)),
                          dpi=int(min(max(inp.get('ocrDpi', 300), 100), 400)))
    return urls, opts, fmt


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}
        try:
            urls, opts, fmt = parse_input(inp)
        except ValueError as e:
            await Actor.fail(status_message=str(e))
            return
        if os.environ.get('ALLOW_PRIVATE_NETWORK_FOR_LOCAL_DEV') == '1' and not Actor.is_at_home():
            opts.allow_private = True
        missing = set(opts.languages) - available_languages()
        if missing:
            await Actor.fail(status_message=f'OCR language data not installed: {sorted(missing)}')
            return

        budget_hit = False
        include_pages = bool(inp.get('includePageDetails', True))
        async with httpx.AsyncClient(timeout=60, headers={'User-Agent': 'Mozilla/5.0 (compatible; PdfOcrExtractor/1.0)'}) as client:
            for n, url in enumerate(urls, 1):
                if budget_hit:
                    break
                await Actor.set_status_message(f'File {n}/{len(urls)}: downloading')
                record: dict = {'url': url}
                try:
                    data = await download(client, url, opts)
                    record['bytes'] = len(data)
                    pages = []
                    it = await asyncio.to_thread(iter_pages, data, opts)
                    while True:
                        page = await asyncio.to_thread(next, it, _SENTINEL)  # CPU work off the event loop
                        if page is _SENTINEL:
                            break
                        event = EVENT_OCR if page['method'] == 'ocr' else EVENT_TEXT if page['method'] == 'text' else None
                        if event:
                            res = await Actor.charge(event)
                            if res.charged_count == 0 and res.event_charge_limit_reached:
                                budget_hit = True
                                break
                        pages.append(page)
                        if len(pages) % 5 == 0:
                            await Actor.set_status_message(f'File {n}/{len(urls)}: {len(pages)} pages')
                        if event and res.event_charge_limit_reached:
                            budget_hit = True
                            break
                    record.update({
                        'pageCount': len(pages),
                        'ocrPages': sum(1 for p in pages if p['method'] == 'ocr'),
                        'textLayerPages': sum(1 for p in pages if p['method'] == 'text'),
                        'tableCount': sum(len(p['tables']) for p in pages),
                        'languages': list(opts.languages),
                        'content': to_markdown(pages) if fmt == 'markdown' else
                                   '\n\n'.join(p['text'] for p in pages if p['text']),
                        'format': fmt,
                        'truncated': budget_hit or len(pages) >= opts.max_pages,
                    })
                    if include_pages:
                        record['pages'] = pages
                except DocumentError as e:
                    record['error'] = str(e)
                except Exception as e:  # noqa: BLE001
                    record['error'] = f'{type(e).__name__}: {e}'[:300]
                await Actor.push_data(record)
        msg = f'Done: processed {len(urls)} file(s)' + (' (stopped: max charge reached)' if budget_hit else '')
        await Actor.set_status_message(msg, is_terminal=True)
