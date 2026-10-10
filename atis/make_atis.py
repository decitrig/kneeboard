"""ATIS copy template.

Landscape letter sheet (11x8.5in), folded in half into two half-letter
kneeboard panels. 4 ATIS blocks per panel, 2 panels per side, 2 sides
(print duplex) = 16 blocks. Margins are symmetric about the fold, so the
back lines up whether the printer flips on the long or short edge.

Fonts, line weights and shading come from ../style.py.
"""
import os
import sys

from reportlab.lib.units import inch

sys.dont_write_bytecode = True  # keep the repo root free of __pycache__
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import style  # noqa: E402
from style import HEADER_H, LINE_TOP, cell, block_frame, write_lines  # noqa: E402

BLOCKS = 4                # per panel

def block(c, x, y, w, h):
    top = y + h
    with block_frame(c, x, y, w, h):
        # Header: airport | info letter | time
        hh = HEADER_H
        aw, lw = w * 0.42, 0.7 * inch
        cell(c, x, top - hh, aw, hh, "AIRPORT", band=True)
        cell(c, x + aw, top - hh, lw, hh, "INFO", band=True)
        cell(c, x + aw + lw, top - hh, w - aw - lw, hh, "TIME", "Z", band=True)
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
        write_lines(c, x, y, w, yy - LINE_TOP)

def panel(c, px):
    style.panel(c, px, BLOCKS, block, "ATIS")

def build(out):
    style.build_sheet(out, "ATIS Template (C172 kneeboard, letter fold)", (panel, panel))

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atis_letter_fold.pdf")
    build(out); print(out)
