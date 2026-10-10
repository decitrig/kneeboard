"""CRAFT copy template for flight following / clearance readbacks.

Same format as the ATIS template: landscape letter sheet (11x8.5in), folded
in half into two half-letter kneeboard panels. 3 CRAFT blocks per panel,
2 panels per side, 2 sides (print duplex) = 12 blocks. Margins are
symmetric about the fold so duplex flip edge doesn't matter.

Fonts, line weights and shading come from ../style.py.
"""
import os
import sys

from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas

sys.dont_write_bytecode = True  # keep the repo root free of __pycache__
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import style  # noqa: E402
from style import (W, H, PANEL_W, cell, letter_cell, checkbox,  # noqa: E402
                   block_frame, write_lines, fold_line)

BLOCKS = 3                # per panel (CRAFT needs more writing room than ATIS)
SIDES = 2

def block(c, x, y, w, h):
    top = y + h
    with block_frame(c, x, y, w, h):
        # Header: airport / facility | ATIS letter | time
        hh = 0.4 * inch
        aw, lw = w * 0.42, 0.7 * inch
        cell(c, x, top - hh, aw, hh, "AIRPORT / FACILITY", band=True)
        cell(c, x + aw, top - hh, lw, hh, "ATIS", band=True)
        cell(c, x + aw + lw, top - hh, w - aw - lw, hh, "TIME", "Z", band=True)
        # CRAFT rows. A and F/T share rows to leave room for notes.
        rh = 0.36 * inch
        yy = top - hh
        half = w / 2
        yy -= rh
        letter_cell(c, x, yy, w, rh, "C", "CLEARANCE LIMIT / DESTINATION")
        yy -= rh
        letter_cell(c, x, yy, w, rh, "R", "ROUTE / HEADING", "RV = radar vectors")
        yy -= rh
        letter_cell(c, x, yy, w, rh, "A", "ALTITUDE", "maint VFR at/blw · exp ___ in ___ min")
        yy -= rh
        letter_cell(c, x, yy, half, rh, "F", "DEPARTURE FREQ")
        letter_cell(c, x + half, yy, half, rh, "T", "SQUAWK")
        # Notes fill the rest (restrictions, traffic, readback corrections)
        cell(c, x, y, w, yy - y, "NOTES / RESTRICTIONS", "read back")
        bs = 6
        checkbox(c, x + w - 3.5 - c.stringWidth("read back", style.FONT, 5.2) - bs - 2.5, yy - 8.6, bs)
        write_lines(c, x, y, w, yy - 0.26 * inch, 0.2 * inch)

def panel(c, px):
    style.panel(c, px, BLOCKS, block, "CRAFT")

def build(out):
    c = canvas.Canvas(out, pagesize=(W, H))
    c.setTitle("CRAFT Template (C172 kneeboard, letter fold)")
    for _ in range(SIDES):
        panel(c, 0); panel(c, PANEL_W); fold_line(c)
        c.showPage()
    c.save()

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "craft_letter_fold.pdf")
    build(out); print(out)
