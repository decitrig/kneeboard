"""CRAFT copy template for flight following / clearance readbacks.

Same format as the ATIS template: landscape letter sheet (11x8.5in), folded
in half into two half-letter kneeboard panels. 3 CRAFT blocks per panel,
2 panels per side, 2 sides (print duplex) = 12 blocks. Margins are
symmetric about the fold so duplex flip edge doesn't matter.
"""
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas

W, H = 11 * inch, 8.5 * inch
PANEL_W = W / 2
M = 0.3 * inch            # margin on every panel edge, fold side included
GAP = 0.1 * inch          # between blocks
BLOCKS = 3                # per panel (CRAFT needs more writing room than ATIS)
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

def letter_cell(c, x, y, w, h, letter, label, hint=None):
    """Row with a big CRAFT letter tab on the left, label + hint in the field."""
    tw = 0.3 * inch
    c.setFillGray(0.9); c.setStrokeGray(GRID); c.setLineWidth(0.6)
    c.rect(x, y, tw, h, fill=1)
    c.setFillGray(0.15); c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(x + tw / 2, y + h / 2 - 4.5, letter)
    cell(c, x + tw, y, w - tw, h, label, hint)

def block(c, x, y, w, h):
    top = y + h
    # Header: airport / facility | ATIS letter | time
    hh = 0.4 * inch
    aw, lw = w * 0.42, 0.7 * inch
    cell(c, x, top - hh, aw, hh, "AIRPORT / FACILITY")
    cell(c, x + aw, top - hh, lw, hh, "ATIS")
    cell(c, x + aw + lw, top - hh, w - aw - lw, hh, "TIME", "Z")
    # CRAFT rows. A and F/T share rows to leave room for notes.
    rh = 0.36 * inch
    yy = top - hh
    half = w / 2
    yy -= rh
    letter_cell(c, x, yy, w, rh, "C", "CLEARANCE LIMIT / DESTINATION")
    yy -= rh
    letter_cell(c, x, yy, w, rh, "R", "ROUTE / HEADING", "RV = radar vectors")
    yy -= rh
    letter_cell(c, x, yy, w, rh, "A", "ALTITUDE", "maint VFR at/blw  ·  exp ___ in ___ min")
    yy -= rh
    letter_cell(c, x, yy, half, rh, "F", "DEPARTURE FREQ")
    letter_cell(c, x + half, yy, half, rh, "T", "SQUAWK")
    # Notes fill the rest (restrictions, traffic, readback corrections)
    cell(c, x, y, w, yy - y, "NOTES / RESTRICTIONS", "read back")
    bs = 6  # read-back checkbox
    c.setStrokeGray(0.4); c.setLineWidth(0.6)
    c.rect(x + w - 3 - c.stringWidth("read back", "Helvetica", 6) - bs - 2, yy - 8.5, bs, bs)
    c.setStrokeGray(0.8); c.setLineWidth(0.4)
    ly = yy - 0.26 * inch
    while ly > y + 0.08 * inch:
        c.line(x + 4, ly, x + w - 4, ly); ly -= 0.2 * inch
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
    c.setTitle("CRAFT Template (C172 kneeboard, letter fold)")
    for _ in range(SIDES):
        panel(c, 0); panel(c, PANEL_W); fold_line(c)
        c.showPage()
    c.save()

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "craft_letter_fold.pdf")
    build(out); print(out)
