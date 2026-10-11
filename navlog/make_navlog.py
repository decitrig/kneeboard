"""VFR navlog template.

Same landscape letter fold format as the other sheets. Front: one navlog
across both panels, 11 legs on the left under the route header and 12 more
on the right. Back: departure and destination / alternate frequencies and
notes on the left; enroute frequencies over weight & balance on the right.

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
                   cell, field, block_frame, shape_frame, dotted, hatch, write_lines,
                   panel_marks)

LEGS = (11, 12)           # left panel, right panel
IND = 0.2 * inch          # checkpoint rows overhang the legs by this much
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
    yd = y2 - ROW
    # Outline: checkpoint rows (and their header) overhang the leg rows on
    # the left, so the route reads down the overhanging tabs.
    pts = [(xs[0], top), (x + w, top), (x + w, y), (x, y)]
    for k in range(legs):
        pts += [(x, y + (2 * k + 1) * ROW), (xs[0], y + (2 * k + 1) * ROW),
                (xs[0], y + (2 * k + 2) * ROW), (x, y + (2 * k + 2) * ROW)]
    pts += [(x, y1), (xs[0], y1)]
    with shape_frame(c, pts):
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
        rule(c, x, y1, cp, y1)
        c.setFillGray(0.15); c.setFont(FONT_BOLD, 5.8)
        for label, x0 in (("CHECKPOINT", x), ("NAVAID", xs[3]), ("ALT", xs[6])):
            c.drawString(x0 + 3.5, y2 + 4, label)
        for xx in (xs[3], xs[6], cp):
            rule(c, xx, y2, xx, y1)
        rule(c, x, y2, x + w, y2, heavy=True)

        # Departure checkpoint
        for xx in (xs[3], xs[6], xs[10]):
            rule(c, xx, yd, xx, y2)

        # Legs
        for i in range(legs):
            lt = yd - i * 2 * ROW            # top of this leg
            mid, lb = lt - ROW, lt - 2 * ROW
            rule(c, x, lt, x + w, lt, heavy=True)
            for xx in xs[1:8]:
                rule(c, xx, mid, xx, lt)
            for xx in (xs[3], xs[6]):
                rule(c, xx, lb, xx, mid)
            dotted(c, xs[0], mid, cp, inset=0)
            dotted(c, cp, mid, x + w, inset=0)

        # Form fields (fillable sheet only)
        start = "dep" if first == 1 else "cont"
        cp_fields(c, start, (x, xs[3], xs[6], cp), yd)
        for j, col in ((9, "DIST"), (10, "FUEL")):
            box(c, f"{start}_{col.lower()}_rem", xs[j], xs[j + 1], yd)
        for i in range(legs):
            n, lt = first + i, yd - i * 2 * ROW
            for j, (label, _, _) in enumerate(COLS):
                if j < 7:
                    box(c, f"leg{n}_{label.lower()}", xs[j], xs[j + 1], lt - ROW)
                else:
                    tail = ("leg", "rem") if j > 8 else ("est", "act")
                    box(c, f"leg{n}_{label.lower()}_{tail[0]}", xs[j], xs[j + 1], lt - ROW)
                    box(c, f"leg{n}_{label.lower()}_{tail[1]}", xs[j], xs[j + 1], lt - 2 * ROW)
            cp_fields(c, f"leg{n}", (x, xs[3], xs[6], cp), lt - 2 * ROW)
    # Leg numbers sit in the notch beside each leg row
    c.setFillGray(HINT); c.setFont(FONT, 5.5)
    for i in range(legs):
        c.drawCentredString(x + IND / 2, yd - i * 2 * ROW - ROW + 7.5, str(first + i))
    centred(c, FONT, 4.6, "LEG", x + IND / 2, top - 12, IND - 2)
    c.setFillGray(0)
    return h

def box(c, name, x1, x2, y):
    """Field filling one leg-table row between x1 and x2."""
    field(c, name, x1 + 1.5, y + 1, x2 - x1 - 3, ROW - 2)

def cp_fields(c, prefix, xs, y):
    """Checkpoint, navaid and altitude fields in a checkpoint row."""
    for k, label in enumerate(("checkpoint", "navaid", "alt")):
        box(c, f"{prefix}_{label}", xs[k] + (3 if k == 0 else 0), xs[k + 1], y)

def slug(*parts):
    """Form field name from printed labels."""
    words = "".join(ch if ch.isalnum() else " " for ch in " ".join(parts)).lower()
    return "_".join(words.split())

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
                cell(c, cx, top - (r + 1) * rh, span * unit, rh, label, hint,
                     name=slug(label))
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
                 w / 2, FIELD_H, label, name=slug(title.split()[0], label))
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
        field(c, "notes", x + 3, y + 3, w - 6, top - TITLE_H - y - 6, multiline=True)
    panel_marks(c, px, "NAVLOG")

def enroute_block(c, x, top, w, h):
    widths = (0.30 * w, 0.17 * w, 0.53 * w)
    avail = h - TITLE_H
    n = round(avail / (0.4 * inch))
    rh = avail / n
    with block_frame(c, x, top - h, w, h):
        cx = x
        for label, cw in zip(("ENROUTE FACILITY", "FREQ", "NOTES"), widths):
            cell(c, cx, top - TITLE_H, cw, TITLE_H, label, band=True)
            for r in range(n):
                cell(c, cx, top - TITLE_H - (r + 1) * rh, cw, rh, "",
                     name=slug("enroute", str(r + 1), label.split()[-1]))
            cx += cw

# Weight & balance stations: (label, hint, total row). Arms are left blank
# because they differ between C172 models; the arm of a total is its CG.
WB_ROWS = [("BASIC EMPTY WEIGHT", None, False),
           ("FRONT SEATS", None, False),
           ("REAR SEATS", None, False),
           ("BAGGAGE AREA 1", None, False),
           ("BAGGAGE AREA 2", None, False),
           ("USABLE FUEL", "gal × 6", False),
           ("TAKEOFF", None, True),
           ("FUEL BURN", "− gal × 6", False),
           ("LANDING", None, True)]
WB_COLS = (("STATION", None, 0.40), ("WEIGHT", "lb", 0.20),
           ("ARM", "in", 0.17), ("MOMENT", "÷ 1000", 0.23))
WB_HEAD = 0.2 * inch      # column header row
WB_LIMITS = 0.36 * inch   # limits row at the bottom

def wb_block(c, x, top, w, h):
    """Weight, arm and moment per station; totals carry the CG."""
    xs = [x]
    for _, _, f in WB_COLS:
        xs.append(xs[-1] + f * w)
    xs[-1] = x + w
    rh = (h - TITLE_H - WB_HEAD - WB_LIMITS) / len(WB_ROWS)
    y = top - h
    with block_frame(c, x, y, w, h):
        cell(c, x, top - TITLE_H, w, TITLE_H, "WEIGHT & BALANCE", band=True)
        hy = top - TITLE_H - WB_HEAD
        for i, (label, hint, _) in enumerate(WB_COLS):
            cell(c, xs[i], hy, xs[i + 1] - xs[i], WB_HEAD, label, hint)
        for r, (label, hint, total) in enumerate(WB_ROWS):
            ry = hy - (r + 1) * rh
            if total:
                c.setFillGray(SHADE); c.rect(x, ry, w, rh, stroke=0, fill=1)
            for i in range(len(WB_COLS)):
                cw = xs[i + 1] - xs[i]
                name = slug("wb", label, WB_COLS[i][0])
                if i == 0:
                    cell(c, xs[i], ry, cw, rh, label, hint)
                elif i == 2 and total:
                    cell(c, xs[i], ry, cw, rh, "CG", "in", name=slug("wb", label, "CG"))
                else:
                    cell(c, xs[i], ry, cw, rh, "", name=name)
            if total:
                rule(c, x, ry + rh, x + w, ry + rh, heavy=True)
        ly = y + WB_LIMITS
        rule(c, x, ly, x + w, ly, heavy=True)
        cell(c, x, y, 0.4 * w, WB_LIMITS, "MAX GROSS", "lb", name="wb_max_gross")
        cell(c, x + 0.4 * w, y, 0.6 * w, WB_LIMITS, "CG LIMITS", "fwd – aft",
             name="wb_cg_limits")

def back_right(c, px):
    """Enroute frequencies on top, weight & balance below."""
    x, w, top = px + M, PANEL_W - 2 * M, H - M
    half = (H - 2 * M - GAP) / 2
    enroute_block(c, x, top, w, half)
    wb_block(c, x, M + half, w, half)
    panel_marks(c, px, "NAVLOG")

def build(out, fillable=False):
    title = "VFR Navlog (C172 kneeboard, letter fold%s)" % (", fillable" if fillable else "")
    style.build_sheet(out, title, (front_left, front_right), (back_left, back_right),
                      fillable=fillable)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for name, fillable in (("navlog_letter_fold.pdf", False),
                           ("navlog_letter_fold_fillable.pdf", True)):
        out = os.path.join(here, name)
        build(out, fillable); print(out)
