"""VFR navlog template.

Same landscape letter fold format as the other sheets. Front: one navlog
across both panels, 11 legs on the left under the route header and 12 more
on the right. Back: departure and destination / alternate frequencies and
notes on the left, enroute frequencies on the right.

Each leg is a white row of headings (TC through CH) followed by the shaded
checkpoint it arrives at. ETE, GS, distance and fuel span both rows: the
estimate on top, the actual below.

Fonts, line weights and shading come from ../style.py.
"""
import os
import sys

from reportlab.lib.units import inch

sys.dont_write_bytecode = True  # keep the repo root free of __pycache__
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import style  # noqa: E402
from style import (H, M, GAP, PANEL_W, GRID, HINT, SHADE, FONT, FONT_BOLD,  # noqa: E402
                   cell, block_frame, dotted, hatch, write_lines, panel_marks)

LEGS = (11, 12)           # left panel, right panel
IND = 0.2 * inch          # leg-number gutter; checkpoint rows run across it
H1, H2 = 20, 13           # header rows: leg columns, checkpoint columns (pt)
ROW = 21                  # one leg row or one checkpoint row (pt)
TITLE_H = 0.22 * inch     # section title band on the back
FIELD_H = 0.36 * inch     # labelled field on the back

# Leg columns: (label, hint, relative width). The last four span both rows.
COLS = [("TC", "true", 39), ("WCA", "R+ L−", 36), ("TH", "true", 39),
        ("VAR", "W+ E−", 35), ("MH", "mag", 36), ("DEV", "card", 35),
        ("CH", "compass", 49), ("ETE", "est / act", 60), ("GS", "est / act", 50),
        ("DIST", "leg / rem", 46), ("FUEL", "leg / rem", 49)]
KEY = ("CH", "ETE")       # the numbers flown: set a size up

def centred(c, font, size, text, cx, y, maxw):
    """Centred text, shrunk if it would not fit maxw."""
    while c.stringWidth(text, font, size) > maxw and size > 4:
        size -= 0.2
    c.setFont(font, size); c.drawCentredString(cx, y, text)

def rule(c, x1, y1, x2, y2, heavy=False):
    if heavy:
        c.setStrokeGray(0); c.setLineWidth(0.9)
    else:
        c.setStrokeGray(GRID); c.setLineWidth(0.5)
    c.line(x1, y1, x2, y2)

def leg_table(c, x, top, w, legs, first):
    """Header, departure checkpoint, then `legs` leg + checkpoint pairs."""
    h = H1 + H2 + ROW + legs * 2 * ROW
    y = top - h
    unit = (w - IND) / sum(cw for _, _, cw in COLS)
    xs = [x + IND]
    for _, _, cw in COLS:
        xs.append(xs[-1] + cw * unit)
    xs[-1] = x + w
    cp = xs[7]                       # checkpoint rows end where ETE starts
    y1, y2 = top - H1, top - H1 - H2
    with block_frame(c, x, y, w, h):
        # Fills first, lines on top
        c.setFillGray(SHADE)
        c.rect(x, y2, cp - x, H2, stroke=0, fill=1)           # checkpoint heads
        c.rect(x, y2 - ROW, cp - x, ROW, stroke=0, fill=1)     # departure
        c.rect(xs[9], y2 - ROW, x + w - xs[9], ROW, stroke=0, fill=1)
        hatch(c, xs[7], y2 - ROW, xs[9] - xs[7], ROW)          # no ETE / GS yet
        for i in range(legs):
            lt = y2 - ROW - i * 2 * ROW
            c.setFillGray(SHADE)
            c.rect(x, lt - 2 * ROW, x + w - x, ROW, stroke=0, fill=1)

        # Header: leg columns on top, checkpoint columns below,
        # ETE / GS / DIST / FUEL spanning both
        for i, (label, hint, _) in enumerate(COLS):
            cx, cw = (xs[i] + xs[i + 1]) / 2, xs[i + 1] - xs[i] - 3
            base = top - 9 if i < 7 else top - 13
            c.setFillGray(0)
            centred(c, FONT_BOLD, 8 if label in KEY else 6.3, label, cx, base, cw)
            c.setFillGray(HINT)
            centred(c, FONT, 5, hint, cx, base - 7.5 if label in KEY else base - 7, cw)
            if i:
                rule(c, xs[i], y1 if i < 7 else y, xs[i], top)
        c.setFillGray(HINT); centred(c, FONT, 4.6, "LEG", x + IND / 2, top - 12, IND - 2)
        rule(c, xs[0], y1, xs[0], top)
        rule(c, x, y1, cp, y1)
        c.setFillGray(0.15); c.setFont(FONT_BOLD, 5.8)
        for label, x0 in (("CHECKPOINT", x), ("NAVAID", xs[3]), ("ALT", xs[6])):
            c.drawString(x0 + 3.5, y2 + 4, label)
        for xx in (xs[3], xs[6], cp):
            rule(c, xx, y2, xx, y1)
        rule(c, x, y2, x + w, y2, heavy=True)

        # Departure checkpoint
        yd = y2 - ROW
        for xx in (xs[3], xs[6], xs[10]):
            rule(c, xx, yd, xx, y2)

        # Legs
        for i in range(legs):
            lt = yd - i * 2 * ROW            # top of this leg
            mid, lb = lt - ROW, lt - 2 * ROW
            rule(c, x, lt, x + w, lt, heavy=True)
            for xx in xs[:8]:
                rule(c, xx, mid, xx, lt)
            for xx in (xs[3], xs[6]):
                rule(c, xx, lb, xx, mid)
            dotted(c, x, mid, cp, inset=0)
            dotted(c, cp, mid, x + w, inset=0)
            c.setFillGray(HINT); c.setFont(FONT, 5.5)
            c.drawCentredString(x + IND / 2, mid + 7.5, str(first + i))
    c.setFillGray(0)
    return h

def route_block(c, x, top, w, h):
    """Aircraft and planning numbers above the left-hand legs."""
    rows = [[("AIRCRAFT", None, 1.2), ("DATE", None, 1), ("FROM", None, 1), ("TO", None, 1)],
            [("CRUISE RPM / MP", None, 1.5), ("TAS", "kt", 1), ("GPH", None, 1),
             ("FUEL ON BOARD", "gal", 1.2), ("ENDURANCE", None, 1.2)]]
    rh = h / len(rows)
    with block_frame(c, x, top - h, w, h):
        for r, row in enumerate(rows):
            unit = w / sum(f[2] for f in row)
            cx = x
            for label, hint, span in row:
                cell(c, cx, top - (r + 1) * rh, span * unit, rh, label, hint)
                cx += span * unit

def front_left(c, px):
    x, w = px + M, PANEL_W - 2 * M
    table_h = H1 + H2 + ROW + LEGS[0] * 2 * ROW
    rb = H - 2 * M - table_h - GAP
    route_block(c, x, H - M, w, rb)
    leg_table(c, x, H - M - rb - GAP, w, LEGS[0], 1)
    panel_marks(c, px, "NAVLOG")

def front_right(c, px):
    leg_table(c, px + M, H - M, PANEL_W - 2 * M, LEGS[1], LEGS[0] + 1)
    panel_marks(c, px, "NAVLOG")

def section(c, x, top, w, title, fields):
    """Title band over a two-column grid of labelled fields."""
    rows = (len(fields) + 1) // 2
    h = TITLE_H + rows * FIELD_H
    with block_frame(c, x, top - h, w, h):
        cell(c, x, top - TITLE_H, w, TITLE_H, title, band=True)
        for i, label in enumerate(fields):
            cell(c, x + (i % 2) * w / 2, top - TITLE_H - (i // 2 + 1) * FIELD_H,
                 w / 2, FIELD_H, label)
    return h

def back_left(c, px):
    x, w, top = px + M, PANEL_W - 2 * M, H - M
    top -= section(c, x, top, w, "DEPARTURE",
                   ["AIRPORT", "ELEV / RUNWAY", "ATIS / AWOS", "CLEARANCE",
                    "GROUND", "TOWER / CTAF", "DEPARTURE FREQ", "SQUAWK"]) + GAP
    top -= section(c, x, top, w, "DESTINATION / ALTERNATE",
                   ["AIRPORT", "ELEV / RUNWAY", "ATIS / AWOS", "TOWER / CTAF",
                    "GROUND", "APPROACH / CENTER", "ALTERNATE", "ALTERNATE FREQ"]) + GAP
    y = M
    with block_frame(c, x, y, w, top - y):
        cell(c, x, top - TITLE_H, w, TITLE_H, "NOTES", band=True)
        write_lines(c, x, y, w, top - TITLE_H - style.LINE_PITCH)
    panel_marks(c, px, "NAVLOG")

def back_right(c, px):
    x, w, top = px + M, PANEL_W - 2 * M, H - M
    widths = (0.30 * w, 0.17 * w, 0.53 * w)
    avail = H - 2 * M - TITLE_H
    n = round(avail / (0.4 * inch))
    rh = avail / n
    with block_frame(c, x, M, w, H - 2 * M):
        cx = x
        for label, cw in zip(("ENROUTE FACILITY", "FREQ", "NOTES"), widths):
            cell(c, cx, top - TITLE_H, cw, TITLE_H, label, band=True)
            for r in range(n):
                cell(c, cx, top - TITLE_H - (r + 1) * rh, cw, rh, "")
            cx += cw
    panel_marks(c, px, "NAVLOG")

def build(out):
    style.build_sheet(out, "VFR Navlog (C172 kneeboard, letter fold)",
                      (front_left, front_right), (back_left, back_right))

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "navlog_letter_fold.pdf")
    build(out); print(out)
