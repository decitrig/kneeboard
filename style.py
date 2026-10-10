"""Shared look for every kneeboard template.

The generators import this so the sheets stay consistent. Everything is
grayscale and prints cleanly on a black-and-white laser printer.

Font: B612, the typeface Airbus and ENAC designed for cockpit displays
(SIL Open Font License, see fonts/OFL.txt). It is wide and open, so labels
stay readable at 6pt on a bouncing kneeboard.
"""
import os
from contextlib import contextmanager

from reportlab.lib.pagesizes import inch
from reportlab.pdfbase import pdfmetrics
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

# Ink
GRID = 0.6                # inner cell dividers
LABEL = 0.15              # field labels
HINT = 0.45               # units / hints
BAND = 0.9                # header row fill
RULE = 0.55               # writing guide dots
RADIUS = 5                # block corner radius, pt

def cell(c, x, y, w, h, text, hint=None, band=False):
    """A labelled field. band=True gives it the light header fill."""
    if band:
        c.setFillGray(BAND); c.rect(x, y, w, h, stroke=0, fill=1)
    c.setStrokeGray(GRID); c.setLineWidth(0.5); c.rect(x, y, w, h)
    c.setFillGray(LABEL); c.setFont(FONT_BOLD, 5.8)
    c.drawString(x + 3.5, y + h - 8, text)
    if hint:
        c.setFillGray(HINT); c.setFont(FONT, 5.2)
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

def write_lines(c, x, y, w, top, pitch):
    """Dotted handwriting guides from top down to just above y."""
    c.saveState()
    c.setStrokeGray(RULE); c.setLineWidth(0.6); c.setLineCap(1); c.setDash(0.1, 2.4)
    ly = top
    while ly > y + 0.08 * inch:
        c.line(x + 5, ly, x + w - 5, ly); ly -= pitch
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
    # Small panel tag in the bottom margin, out of the kneeboard clip
    c.setFillGray(HINT); c.setFont(FONT, 5.5)
    c.drawCentredString(px + PANEL_W / 2, 0.11 * inch, name)
    c.setFillGray(0)

def fold_line(c):
    c.saveState()
    c.setStrokeGray(0.7); c.setLineWidth(0.5); c.setDash(3, 3)
    c.line(PANEL_W, 0.25 * inch, PANEL_W, H - 0.25 * inch)
    c.setFillGray(0.6); c.setFont(FONT, 5)
    for ty in (0.1 * inch, H - 0.17 * inch):
        c.drawCentredString(PANEL_W, ty, "FOLD")
    c.restoreState()
