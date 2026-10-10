"""CRAFT copy template for flight following / clearance readbacks.

Same format as the ATIS template: landscape letter sheet (11x8.5in), folded
in half into two half-letter kneeboard panels. 3 CRAFT blocks per panel,
2 panels per side, 2 sides (print duplex) = 12 blocks. Margins are
symmetric about the fold so duplex flip edge doesn't matter.

Fonts, line weights and shading come from ../style.py.
"""
import os
import sys

from reportlab.lib.units import inch

sys.dont_write_bytecode = True  # keep the repo root free of __pycache__
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import style  # noqa: E402
from style import (HEADER_H, LINE_TOP, HINT_SIZE, FONT, cell,  # noqa: E402
                   letter_cell, checkbox, block_frame, write_lines)

BLOCKS = 3                # per panel (CRAFT needs more writing room than ATIS)

def block(c, x, y, w, h):
    top = y + h
    with block_frame(c, x, y, w, h):
        # Header: airport / facility | ATIS letter | time
        hh = HEADER_H
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
        checkbox(c, x + w - 3.5 - c.stringWidth("read back", FONT, HINT_SIZE) - bs - 2.5, yy - 8.6, bs)
        write_lines(c, x, y, w, yy - LINE_TOP)

def panel(c, px):
    style.panel(c, px, BLOCKS, block, "CRAFT")

def build(out):
    style.build_sheet(out, "CRAFT Template (C172 kneeboard, letter fold)", (panel, panel))

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "craft_letter_fold.pdf")
    build(out); print(out)
