"""Shared look for every kneeboard template.

The generators import this so the sheets stay consistent. Everything is
grayscale and prints cleanly on a black-and-white laser printer.

Font: B612, the typeface Airbus and ENAC designed for cockpit displays
(SIL Open Font License, see fonts/OFL.txt). It is wide and open, so labels
stay readable at 6pt on a bouncing kneeboard.
"""
import os
import re
import xml.etree.ElementTree as ET
from contextlib import contextmanager

from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT, FONT_BOLD = "B612", "B612-Bold"
pdfmetrics.registerFont(TTFont(FONT, os.path.join(HERE, "fonts", "B612-Regular.ttf")))
pdfmetrics.registerFont(TTFont(FONT_BOLD, os.path.join(HERE, "fonts", "B612-Bold.ttf")))

# Sheet geometry shared by all templates
W, H = 11 * inch, 8.5 * inch
PANEL_W = W / 2
M = 0.3 * inch            # margin on every panel edge, fold side included
GAP = 0.1 * inch          # between blocks
HEADER_H = 0.45 * inch    # airport / letter / time band at the top of a block
LINE_PITCH = 0.22 * inch  # handwriting guide spacing
LINE_TOP = 0.28 * inch    # first guide, below the top of its cell

# Type sizes, pt
LABEL_SIZE = 5.8
HINT_SIZE = 5.2

# Ink
GRID = 0.6                # inner cell dividers
LABEL = 0.15              # field labels
HINT = 0.45               # units / hints
BAND = 0.9                # header row fill
SHADE = 0.95              # lighter fill for rows that alternate with white ones
RULE = 0.55               # writing guide dots
RADIUS = 5                # block corner radius, pt

def cell(c, x, y, w, h, text, hint=None, band=False):
    """A labelled field. band=True gives it the light header fill."""
    if band:
        c.setFillGray(BAND); c.rect(x, y, w, h, stroke=0, fill=1)
    c.setStrokeGray(GRID); c.setLineWidth(0.5); c.rect(x, y, w, h)
    c.setFillGray(LABEL); c.setFont(FONT_BOLD, LABEL_SIZE)
    c.drawString(x + 3.5, y + h - 8, text)
    if hint:
        c.setFillGray(HINT); c.setFont(FONT, HINT_SIZE)
        c.drawRightString(x + w - 3.5, y + h - 8, hint)
    c.setFillGray(0)

def letter_cell(c, x, y, w, h, letter, label, hint=None, tab=0.3 * inch):
    """Field with a black tab holding a big mnemonic letter (CRAFT etc.)."""
    c.setFillGray(0.1); c.rect(x, y + 0.75, tab, h - 1.5, stroke=0, fill=1)  # white seam between tabs
    c.setFillGray(1); c.setFont(FONT_BOLD, 13)
    c.drawCentredString(x + tab / 2, y + h / 2 - 4.5, letter)
    cell(c, x + tab, y, w - tab, h, label, hint)

def checkbox(c, x, y, size=6):
    c.setStrokeGray(0.3); c.setLineWidth(0.6)
    c.roundRect(x, y, size, size, 1.2)

def dotted(c, x1, y, x2, inset=5):
    """One dotted guide, the same ink as write_lines."""
    c.saveState()
    c.setStrokeGray(RULE); c.setLineWidth(0.6); c.setLineCap(1); c.setDash(0.1, 2.4)
    c.line(x1 + inset, y, x2 - inset, y)
    c.restoreState()

def write_lines(c, x, y, w, top, pitch=LINE_PITCH):
    """Dotted handwriting guides from top down to just above y."""
    ly = top
    while ly > y + 0.08 * inch:
        dotted(c, x, ly, x + w); ly -= pitch

def hatch(c, x, y, w, h, step=4):
    """Light diagonal hatching: a cell that is not filled in."""
    c.saveState()
    p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)
    c.setFillGray(SHADE); c.rect(x, y, w, h, stroke=0, fill=1)
    c.setStrokeGray(0.65); c.setLineWidth(0.4)
    k = -h
    while k < w:
        c.line(x + k, y, x + k + h, y + h); k += step
    c.restoreState()

@contextmanager
def block_frame(c, x, y, w, h):
    """Clip block contents to a rounded frame, then draw the frame on top."""
    c.saveState()
    p = c.beginPath(); p.roundRect(x, y, w, h, RADIUS)
    c.clipPath(p, stroke=0, fill=0)
    yield
    c.restoreState()
    c.setStrokeGray(0); c.setLineWidth(1.3); c.roundRect(x, y, w, h, RADIUS)

def panel(c, px, blocks, block, name):
    """Stack `blocks` copies of `block` in one half-letter panel."""
    bw = PANEL_W - 2 * M
    bh = (H - 2 * M - GAP * (blocks - 1)) / blocks
    for i in range(blocks):
        block(c, px + M, H - M - (i + 1) * bh - i * GAP, bw, bh)
    panel_marks(c, px, name)

def panel_marks(c, px, name):
    """Panel tag and wordmark in the bottom margin, out of the kneeboard clip."""
    c.setFillGray(HINT); c.setFont(FONT, 5.5)
    c.drawCentredString(px + PANEL_W / 2, 0.11 * inch, name)
    c.setFillGray(0)
    wordmark(c, px + PANEL_W - M, 0.08 * inch)

def build_sheet(out, title, front, back=None):
    """Write a duplex letter-fold PDF. front and back are (left, right) pairs
    of panel functions f(c, px); back defaults to a copy of front."""
    c = canvas.Canvas(out, pagesize=(W, H), initialFontName=FONT, invariant=1)
    c.setTitle(title); c.setAuthor("decitrig"); c.setCreator("decitrig kneeboard")
    for left, right in (front, back or front):
        left(c, 0); right(c, PANEL_W); fold_line(c)
        c.showPage()
    c.save()

def fold_line(c):
    c.saveState()
    c.setStrokeGray(0.7); c.setLineWidth(0.5); c.setDash(3, 3)
    c.line(PANEL_W, 0.25 * inch, PANEL_W, H - 0.25 * inch)
    c.setFillGray(0.6); c.setFont(FONT, 5)
    for ty in (0.1 * inch, H - 0.17 * inch):
        c.drawCentredString(PANEL_W, ty, "FOLD")
    c.restoreState()

# decitrig wordmark, from github.com/decitrig/decimarks (small, for-light).
# Drawn as vector paths in gray so it stays crisp and prints like the rest.
MARK_SVG = os.path.join(HERE, "marks", "decitrig-wordmark-small-for-light.svg")
MARK_W = 0.5 * inch       # printed width of the mark
MARK_INK, MARK_ACCENT = HINT, 0.65

def _svg_path(c, d):
    """reportlab path from SVG path data (the M L Q H V Z subset the mark uses)."""
    p = c.beginPath()
    toks = re.findall(r"[A-Za-z]|-?\d*\.?\d+", d)
    i, cmd, x, y = 0, None, 0.0, 0.0
    def num():
        nonlocal i
        i += 1
        return float(toks[i - 1])
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
        rel = cmd.islower(); C = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if C == "M":
            x, y = ox + num(), oy + num(); p.moveTo(x, y)
            cmd = "l" if rel else "L"
        elif C == "L":
            x, y = ox + num(), oy + num(); p.lineTo(x, y)
        elif C == "H":
            x = ox + num(); p.lineTo(x, y)
        elif C == "V":
            y = oy + num(); p.lineTo(x, y)
        elif C == "Q":
            qx, qy, ex, ey = ox + num(), oy + num(), ox + num(), oy + num()
            p.curveTo(x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y),
                      ex + 2 / 3 * (qx - ex), ey + 2 / 3 * (qy - ey), ex, ey)
            x, y = ex, ey
        elif C == "Z":
            p.close()
        else:
            raise ValueError("unsupported SVG path command " + cmd)
    return p

_mark = None

def _mark_root():
    """The parsed mark SVG, read once per run."""
    global _mark
    if _mark is None:
        _mark = ET.parse(MARK_SVG).getroot()
    return _mark

def wordmark(c, right, bottom, width=MARK_W):
    """Draw the decitrig wordmark with its bottom-right corner at (right, bottom)."""
    root = _mark_root()
    vx, vy, vw, vh = map(float, root.get("viewBox").split())
    k = width / vw
    c.saveState()
    # SVG y runs down: flip, scale and move the viewBox into place
    c.transform(k, 0, 0, -k, right - width - vx * k, bottom + (vy + vh) * k)
    c.setLineCap(1); c.setLineJoin(1)
    parents = {ch: g.get("transform") for g in root.iter() for ch in g if g.get("transform")}
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in ("path", "circle"):
            continue
        gray = MARK_INK
        if "c4691a" in (el.get("fill", "") + el.get("stroke", "")).lower():
            gray = MARK_ACCENT
        stroke = el.get("stroke") not in (None, "none")
        fill = el.get("fill", "#000") != "none"
        c.setStrokeGray(gray); c.setFillGray(gray)
        c.setLineWidth(float(el.get("stroke-width", 1)))
        if tag == "path":
            if not el.get("d"):
                continue
            c.drawPath(_svg_path(c, el.get("d")), stroke=stroke, fill=fill)
        else:
            cx, cy = 0.0, 0.0
            parent_t = parents.get(el)
            if parent_t:
                cx, cy = map(float, re.findall(r"-?[\d.]+", parent_t))
            c.circle(cx + float(el.get("cx", 0)), cy + float(el.get("cy", 0)),
                     float(el.get("r")), stroke=stroke, fill=fill)
    c.restoreState()
