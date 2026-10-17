"""Generate deterministic test documents (run by the tests; also handy for manual runs)."""
import io
import pathlib

from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent / 'fixtures'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def text_pdf_with_table(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', size=12)
    pdf.multi_cell(0, 8, 'Quarterly Report 2026\nRevenue grew strongly in the third quarter across all regions.')
    pdf.ln(4)
    with pdf.table() as t:
        for row in [('Region', 'Q2', 'Q3'), ('North', '120', '150'), ('South', '90', '110')]:
            r = t.row()
            for c in row:
                r.cell(c)
    pdf.add_page()
    pdf.multi_cell(0, 8, 'Second page with plain digital text for the extractor test suite.')
    pdf.output(str(path))


def hebrew_text_pdf(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('dejavu', fname=FONT)
    pdf.set_font('dejavu', size=14)
    pdf.set_text_shaping(True)
    pdf.multi_cell(0, 10, 'שלום עולם, זהו מסמך בדיקה בעברית עם מילים רבות')
    pdf.output(str(path))


def render_lines(lines, size=(1700, 600), font_size=56, rtl=False):
    img = Image.new('RGB', size, 'white')
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, font_size)
    y = 60
    for line in lines:
        if rtl:
            from PIL import features
            kw = {'direction': 'rtl'} if features.check('raqm') else {}
            if not kw:  # no libraqm: do bidi reordering ourselves
                from bidi.algorithm import get_display
                line = get_display(line)
            w = d.textlength(line, font=f, **kw)
            d.text((size[0] - 80 - w, y), line, font=f, fill='black', **kw)
        else:
            d.text((80, y), line, font=f, fill='black')
        y += font_size + 40
    return img


def build():
    HERE.mkdir(exist_ok=True)
    text_pdf_with_table(HERE / 'digital_table.pdf')
    hebrew_text_pdf(HERE / 'hebrew_text.pdf')
    render_lines(['Invoice number 4821', 'Total amount due 1250 USD']).save(HERE / 'english.png')
    render_lines(['שלום עולם', 'חשבונית מספר 4821'], rtl=True).save(HERE / 'hebrew.png')
    scan = render_lines(['Scanned contract page', 'Signed by both parties'], size=(1700, 2200))
    scan.save(HERE / 'scanned.pdf', 'PDF', resolution=200)
    (HERE / 'not_a_doc.txt').write_bytes(b'hello, I am plain text')
    return HERE


if __name__ == '__main__':
    print(build())
