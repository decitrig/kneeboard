"""Combined ATIS + CRAFT template.

Same landscape letter fold format as the standalone sheets: ATIS panel
(4 blocks) on the left half, CRAFT panel (3 blocks) on the right half, on
both sides of a duplex print = 8 ATIS + 6 CRAFT blocks.

Block designs are imported from ../atis/make_atis.py and
../craft/make_craft.py, so a rerun picks up any changes made there.
"""
import importlib.util
import sys
import os

from reportlab.pdfgen import canvas

sys.dont_write_bytecode = True  # keep the other templates' folders clean

HERE = os.path.dirname(os.path.abspath(__file__))

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

atis = load("make_atis", "../atis/make_atis.py")
craft = load("make_craft", "../craft/make_craft.py")

W, H, PANEL_W = atis.W, atis.H, atis.PANEL_W
SIDES = 2

def build(out):
    c = canvas.Canvas(out, pagesize=(W, H))
    c.setTitle("ATIS + CRAFT Template (C172 kneeboard, letter fold)")
    for _ in range(SIDES):
        atis.panel(c, 0); craft.panel(c, PANEL_W); atis.fold_line(c)
        c.showPage()
    c.save()

if __name__ == "__main__":
    out = os.path.join(HERE, "atis_craft_letter_fold.pdf")
    build(out); print(out)
