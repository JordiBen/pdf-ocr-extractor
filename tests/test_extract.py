import asyncio
import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest

from src.extract import (DocumentError, ExtractOptions, detect_kind, download, fix_visual_rtl_line, iter_pages,
                         looks_visual_order, table_to_markdown, to_markdown)
from src.main import parse_input
from tests.make_fixtures import build

FX = build()


def pages(name, **kw):
    return list(iter_pages((FX / name).read_bytes(), ExtractOptions(**kw)))


def test_detect_kind():
    assert detect_kind((FX / 'digital_table.pdf').read_bytes()) == 'pdf'
    assert detect_kind((FX / 'english.png').read_bytes()) == 'image'
    with pytest.raises(DocumentError):
        detect_kind((FX / 'not_a_doc.txt').read_bytes())


def test_digital_pdf_text_and_table():
    ps = pages('digital_table.pdf')
    assert [p['method'] for p in ps] == ['text', 'text']
    assert 'Quarterly Report 2026' in ps[0]['text']
    flat = [c for t in ps[0]['tables'] for row in t for c in row]
    assert {'Region', 'North', '150'} <= set(flat)
    md = to_markdown(ps)
    assert '| Region | Q2 | Q3 |' in md and '<!-- page 2 (text) -->' in md


def test_scanned_pdf_falls_back_to_ocr():
    ps = pages('scanned.pdf', dpi=200)
    assert ps[0]['method'] == 'ocr' and ps[0]['ocrConfidence'] > 60
    assert 'Scanned contract page' in ps[0]['text'] and 'Signed by both parties' in ps[0]['text']


def test_mode_text_never_ocrs():
    ps = pages('scanned.pdf', mode='text')
    assert ps[0]['method'] == 'text' and ps[0]['text'] == ''


def test_mode_ocr_forces_ocr_on_digital():
    ps = pages('digital_table.pdf', mode='ocr', max_pages=1, dpi=200)
    assert len(ps) == 1 and ps[0]['method'] == 'ocr' and 'Quarterly' in ps[0]['text']


def test_english_image_ocr():
    ps = pages('english.png')
    assert ps[0]['method'] == 'ocr'
    assert 'Invoice number 4821' in ps[0]['text'] and '1250' in ps[0]['text']


def test_hebrew_image_ocr_logical_order():
    ps = pages('hebrew.png', languages=('heb',))
    t = ps[0]['text']
    assert 'שלום עולם' in t, t          # logical (readable) order, not reversed
    assert '4821' in t and 'חשבונית' in t


def test_hebrew_pdf_text_layer_reads_in_logical_order():
    t = pages('hebrew_text.pdf')[0]['text']
    assert 'שלום עולם' in t, t
    assert not looks_visual_order(t)


def test_rtl_helpers():
    visual = 'םלוע םולש'  # how some PDFs store "שלום עולם"
    assert fix_visual_rtl_line(visual) == 'שלום עולם'
    assert fix_visual_rtl_line('1234 רפסמ') == 'מספר 1234'
    assert fix_visual_rtl_line('plain english') == 'plain english'
    assert looks_visual_order('םלוע םולש ןמז ץרא') and not looks_visual_order('שלום עולם זמן ארץ')


def test_table_markdown_escapes():
    md = table_to_markdown([['a|b', None], ['x\ny', '2', 'extra']])
    assert md.splitlines()[0] == '| a\\|b |  |  |' and md.splitlines()[2] == '| x y | 2 | extra |'


def test_max_pages():
    assert len(pages('digital_table.pdf', max_pages=1)) == 1


@pytest.fixture(scope='module')
def server():
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(FX))
    handler.log_message = lambda *a: None
    srv = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f'http://127.0.0.1:{srv.server_address[1]}'
    srv.shutdown()


def test_download_size_limit_and_ssrf(server):
    async def go(url, **kw):
        async with httpx.AsyncClient() as c:
            return await download(c, url, ExtractOptions(**kw))
    data = asyncio.run(go(server + '/english.png', allow_private=True))
    assert data[:4] == b'\x89PNG'
    with pytest.raises(DocumentError, match='too large'):
        asyncio.run(go(server + '/english.png', allow_private=True, max_bytes=100))
    with pytest.raises(Exception, match='non-public'):
        asyncio.run(go(server + '/english.png'))
    with pytest.raises(DocumentError, match='404'):
        asyncio.run(go(server + '/nope.pdf', allow_private=True))


def test_parse_input():
    urls, opts, fmt = parse_input({'fileUrls': [{'url': 'https://x/a.pdf'}, {'url': 'https://x/a.pdf'}], 'languages': ['heb', 'eng']})
    assert urls == ['https://x/a.pdf'] and opts.languages == ('heb', 'eng') and fmt == 'markdown'
    with pytest.raises(ValueError):
        parse_input({'fileUrls': [{'url': 'https://x'}], 'languages': ['xx']})
    with pytest.raises(ValueError):
        parse_input({'fileUrls': []})
