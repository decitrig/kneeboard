"""ATIS copy template.

Landscape letter sheet (11x8.5in), folded in half into two half-letter
kneeboard panels. 4 ATIS blocks per panel, 2 panels per side, 2 sides
(print duplex) = 16 blocks. Margins are symmetric about the fold, so the
back lines up whether the printer flips on the long or short edge.
"""
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas

W, H = 11 * inch, 8.5 * inch
PANEL_W = W / 2
M = 0.3 * inch            # margin on every panel edge, fold side included
GAP = 0.1 * inch          # between blocks
BLOCKS = 4                # per panel
SIDES = 2
GRID = 0.55

def cell(c, x, y, w, h, text, hint=None):
    c.setStrokeGray(GRID); c.setLineWidth(0.6); c.rect(x, y, w, h)
    c.setFillGray(0.25); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(x + 3, y + h - 7.5, text)
    if hint:
        c.setFillGray(0.6); c.setFont("Helvetica", 6)
        c.drawRightString(x + w - 3, y + h - 7.5, hint)
    c.setFillGray(0)

def block(c, x, y, w, h):
    top = y + h
    # Header: airport | info letter | time
    hh = 0.45 * inch
    aw, lw = w * 0.42, 0.7 * inch
    cell(c, x, top - hh, aw, hh, "AIRPORT")
    cell(c, x + aw, top - hh, lw, hh, "INFO")
    cell(c, x + aw + lw, top - hh, w - aw - lw, hh, "TIME", "Z")
    # Weather: 2 rows x 3 columns
    # Each cell: (label, hint, relative width)
    rows = [[("WIND", "°/kt  G", 1), ("VISIBILITY", "SM", 1), ("SKY / CEILING", None, 2)],
            [("TEMP / DEW", "°C", 1), ("ALTIMETER", "inHg", 1), ("RWY / APPROACH", None, 1)]]
    rh = 0.38 * inch
    yy = top - hh
    for row in rows:
        yy -= rh
        unit = w / sum(r[2] for r in row)
        cx = x
        for label, hint, span in row:
            cell(c, cx, yy, span * unit, rh, label, hint)
            cx += span * unit
    # Remarks fill the rest
    cell(c, x, y, w, yy - y, "NOTAMS / REMARKS")
    c.setStrokeGray(0.8); c.setLineWidth(0.4)
    ly = yy - 0.28 * inch
    while ly > y + 0.08 * inch:
        c.line(x + 4, ly, x + w - 4, ly); ly -= 0.22 * inch
    c.setStrokeGray(0); c.setLineWidth(1.4); c.rect(x, y, w, h)

def panel(c, px):
    bw = PANEL_W - 2 * M
    bh = (H - 2 * M - GAP * (BLOCKS - 1)) / BLOCKS
    for i in range(BLOCKS):
        block(c, px + M, H - M - (i + 1) * bh - i * GAP, bw, bh)

def fold_line(c):
    c.setStrokeGray(0.75); c.setLineWidth(0.5); c.setDash(4, 4)
    c.line(PANEL_W, 0.1 * inch, PANEL_W, H - 0.1 * inch)
    c.setDash()

def build(out):
    c = canvas.Canvas(out, pagesize=(W, H))
    c.setTitle("ATIS Template (C172 kneeboard, letter fold)")
    for _ in range(SIDES):
        panel(c, 0); panel(c, PANEL_W); fold_line(c)
        c.showPage()
    c.save()

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atis_letter_fold.pdf")
    build(out); print(out)
