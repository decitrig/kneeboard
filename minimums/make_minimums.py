"""Personal minimums reference card.

Same landscape letter fold format as the other sheets. Every panel carries
the same card, front and back, so the sheet reads the same whichever way it
is folded and can be cut into four half-letter cards.

The card: my own day VFR minimums (weather, fuel, operations) over the
legal VFR weather minimums of 14 CFR 91.155 for day flight.

Fonts, line weights and shading come from ../style.py.
"""
import os
import sys

from reportlab.lib.units import inch

sys.dont_write_bytecode = True  # keep the repo root free of __pycache__
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import style  # noqa: E402
from style import (H, M, GAP, PANEL_W, GRID, LABEL, HINT, BAND, SHADE,  # noqa: E402
                   FONT, FONT_BOLD, LABEL_SIZE, block_frame, panel_marks)

TITLE = "PERSONAL MINIMUMS"
SUBTITLE = "DAY VFR ONLY · NO NIGHT FLYING UNTIL INSTRUMENT RATED"

MINIMUMS = [
    ("WEATHER", [
        ("Ceiling/vis: local", "≥ 3,000 ft AGL / ≥ 5 sm"),
        ("Ceiling/vis: XC", "≥ 6,000 ft AGL / ≥ 7 sm along route"),
        ("Surface wind", "≤ 20 kt steady; gust spread ≤ 8 kt"),
        ("Crosswind", "≤ 10 kt component"),
        ("Thunderstorms", "Stay ≥ 20 nm; no Conv. SIGMET on route"),
        ("SIGMET / AIRMET", "SIGMET on route = no-go; Tango: check alt & area"),
        ("Icing / wind shear", "FZRA, FZDZ or LLWS reported/forecast = no-go"),
    ]),
    ("FUEL", [
        ("Reserve at landing", "≥ 60 min"),
    ]),
    ("OPERATIONS", [
        ("Daylight", "Up ≥ 30 min after sunrise; down ≥ 30 min before sunset"),
        ("Recency", "3 takeoffs & landings in last 60 days, else fly with CFI first"),
        ("Runway", "Book takeoff & landing distance ≤ 50% of runway"),
    ]),
]

# 91.155 day VFR: class, altitude, visibility, then above / below / horizontal
# from clouds, or a single "Clear of clouds".
VFR_TITLE = "VFR WEATHER MINIMUMS · DAY (LEGAL FLOOR)"
VFR_COLS = [("CLASS", 0.42), ("ALTITUDE", 1.5), ("VIS", 0.48),
            ("ABOVE", 0.62), ("BELOW", 0.62), ("SIDE", 0.62)]
VFR = [
    ("B", "All", "3 sm", "Clear of clouds"),
    ("C", "All", "3 sm", "1,000 ft", "500 ft", "2,000 ft"),
    ("D", "All", "3 sm", "1,000 ft", "500 ft", "2,000 ft"),
    ("E", "Below 10,000 ft MSL", "3 sm", "1,000 ft", "500 ft", "2,000 ft"),
    ("E", "10,000 ft MSL and up", "5 sm", "1,000 ft", "1,000 ft", "1 sm"),
    ("G", "1,200 ft AGL and below", "1 sm", "Clear of clouds"),
    ("G", "Over 1,200 AGL, < 10,000 MSL", "1 sm", "1,000 ft", "500 ft", "2,000 ft"),
    ("G", "Over 1,200 AGL, ≥ 10,000 MSL", "5 sm", "1,000 ft", "1,000 ft", "1 sm"),
]
FOOTNOTE = "Legal minimums per 91.155. Set Oct 2026."

TEXT = 9.0                # body text, pt
LEAD = 10.6               # line spacing for wrapped text, pt
PAD = 6.0                 # above and below the text in a row, pt
BAR = 0.25 * inch         # section title band
COLHEAD = 0.21 * inch     # column header row
FACTOR_W = 1.5 * inch    # first column of the minimums table

# B612 has no ≥ or ≤: draw them from its > and < with a bar underneath.
REL = {"≥": ">", "≤": "<"}

def text_width(c, s, font, size):
    return sum(c.stringWidth(REL.get(ch, ch), font, size) for ch in s)

def draw_text(c, x, y, s, font, size):
    """drawString that also handles ≥ and ≤."""
    c.setFont(font, size)
    run = ""
    for ch in s + "\0":
        if ch in REL or ch == "\0":
            c.drawString(x, y, run); x += c.stringWidth(run, font, size); run = ""
            if ch == "\0":
                break
            g = REL[ch]; gw = c.stringWidth(g, font, size)
            c.drawString(x, y + size * 0.14, g)
            c.saveState(); c.setStrokeColor(c._fillColorObj)
            c.setLineWidth(size * 0.07)
            c.line(x + gw * 0.2, y - size * 0.03, x + gw * 0.8, y - size * 0.03)
            c.restoreState()
            x += gw
        else:
            run += ch

def wrap(c, s, font, size, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        test = (cur + " " + word).strip()
        if cur and text_width(c, test, font, size) > maxw:
            lines.append(cur); cur = word
        else:
            cur = test
    return lines + [cur]

def row_h(n):
    return 2 * PAD + TEXT * 0.72 + (n - 1) * LEAD

def rule(c, x1, y, x2):
    c.setStrokeGray(GRID); c.setLineWidth(0.5); c.line(x1, y, x2, y)

def band(c, x, y, w, h, text, size=LABEL_SIZE + 1.4):
    c.setFillGray(BAND); c.rect(x, y, w, h, stroke=0, fill=1)
    c.setFillGray(LABEL); draw_text(c, x + 4.5, y + h / 2 - size * 0.36, text, FONT_BOLD, size)
    c.setFillGray(0)

def col_heads(c, x, y, w, heads):
    """Small gray column labels on white, with a rule under them."""
    c.setFillGray(HINT)
    for hx, text in heads:
        draw_text(c, hx, y + COLHEAD / 2 - 2, text, FONT_BOLD, LABEL_SIZE)
    c.setFillGray(0)
    rule(c, x, y, x + w)

def minimums_height(c, w):
    vw = w - FACTOR_W - 9
    h = COLHEAD
    for _, rows in MINIMUMS:
        h += BAR + sum(row_h(len(wrap(c, v, FONT, TEXT, vw))) for _, v in rows)
    return h

def minimums_block(c, x, top, w, h):
    y = top - h
    vx, vw = x + FACTOR_W, w - FACTOR_W - 9
    with block_frame(c, x, y, w, h):
        yy = top - COLHEAD
        col_heads(c, x, yy, w, [(x + 4.5, "FACTOR"), (vx + 4.5, "MY MINIMUM")])
        for section, rows in MINIMUMS:
            yy -= BAR
            band(c, x, yy, w, BAR, section)
            for i, (factor, value) in enumerate(rows):
                lines = wrap(c, value, FONT, TEXT, vw)
                rh = row_h(len(lines))
                yy -= rh
                if i % 2:
                    c.setFillGray(SHADE); c.rect(x, yy, w, rh, stroke=0, fill=1)
                    c.setFillGray(0)
                if i:
                    rule(c, x, yy + rh, x + w)
                c.setStrokeGray(GRID); c.setLineWidth(0.5); c.line(vx, yy, vx, yy + rh)
                ty = yy + rh - PAD - TEXT * 0.72
                draw_text(c, x + 4.5, ty, factor, FONT_BOLD, TEXT)
                for line in lines:
                    draw_text(c, vx + 4.5, ty, line, FONT, TEXT); ty -= LEAD

def vfr_cols(x, w):
    unit = w / sum(cw for _, cw in VFR_COLS)
    xs = [x]
    for _, cw in VFR_COLS:
        xs.append(xs[-1] + cw * unit)
    return xs

def vfr_height(c, w):
    xs = vfr_cols(0, w)
    aw = xs[2] - xs[1] - 7
    return BAR + COLHEAD + sum(row_h(len(wrap(c, r[1], FONT, TEXT, aw))) for r in VFR)

def vfr_block(c, x, top, w, h):
    y = top - h
    xs = vfr_cols(x, w)
    with block_frame(c, x, y, w, h):
        yy = top - BAR
        band(c, x, yy, w, BAR, VFR_TITLE)
        yy -= COLHEAD
        col_heads(c, x, yy, w, [(cx + 4.5, name) for cx, (name, _) in zip(xs, VFR_COLS)])
        for i, r in enumerate(VFR):
            lines = wrap(c, r[1], FONT, TEXT, xs[2] - xs[1] - 7)
            rh = row_h(len(lines))
            yy -= rh
            if i % 2:
                c.setFillGray(SHADE); c.rect(x, yy, w, rh, stroke=0, fill=1)
                c.setFillGray(0)
            if i:
                rule(c, x, yy + rh, x + w)
            ty = yy + rh - PAD - TEXT * 0.72
            draw_text(c, xs[0] + 4.5, ty, r[0], FONT_BOLD, TEXT)
            for k, line in enumerate(lines):
                draw_text(c, xs[1] + 4.5, ty - k * LEAD, line, FONT, TEXT)
            draw_text(c, xs[2] + 4.5, ty, r[2], FONT_BOLD, TEXT)
            for cx, val in zip(xs[3:], r[3:]):
                draw_text(c, cx + 4.5, ty, val, FONT, TEXT)

def panel(c, px):
    x, w = px + M, PANEL_W - 2 * M
    top = H - M
    # Title and the day-VFR-only rule above the blocks
    c.setFillGray(0); c.setFont(FONT_BOLD, 15)
    c.drawString(x + 1, top - 13, TITLE)
    top -= 20
    sh = 0.26 * inch
    c.setStrokeGray(0); c.setLineWidth(1.3); c.roundRect(x, top - sh, w, sh, style.RADIUS)
    size = 7.6
    c.setFont(FONT_BOLD, size)
    c.drawCentredString(x + w / 2, top - sh / 2 - size * 0.36, SUBTITLE)
    top -= sh + GAP
    mh = minimums_height(c, w)
    minimums_block(c, x, top, w, mh)
    top -= mh + GAP
    vh = vfr_height(c, w)
    vfr_block(c, x, top, w, vh)
    top -= vh
    c.setFillGray(HINT); c.setFont(FONT, 6.8)
    c.drawString(x + 1, top - 10, FOOTNOTE)
    c.setFillGray(0)
    assert top - 10 > M, "card overruns the panel by %.1f pt" % (M - top + 10)
    panel_marks(c, px, "PERSONAL MINIMUMS")

def build(out):
    style.build_sheet(out, "Personal Minimums (C172 kneeboard, letter fold)", (panel, panel))

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minimums_letter_fold.pdf")
    build(out); print(out)
