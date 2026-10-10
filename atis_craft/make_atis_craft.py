"""Combined ATIS + CRAFT template.

Same landscape letter fold format as the standalone sheets: ATIS panel
(4 blocks) on the left half, CRAFT panel (3 blocks) on the right half, on
both sides of a duplex print = 8 ATIS + 6 CRAFT blocks.

Block designs are imported from ../atis/make_atis.py and
../craft/make_craft.py, so a rerun picks up any changes made there.
"""
import os
import sys

sys.dont_write_bytecode = True  # keep the other templates' folders clean
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for d in ("", "atis", "craft"):
    sys.path.insert(0, os.path.join(ROOT, d))
import style  # noqa: E402
import make_atis  # noqa: E402
import make_craft  # noqa: E402

def build(out):
    style.build_sheet(out, "ATIS + CRAFT Template (C172 kneeboard, letter fold)",
                      make_atis.panel, make_craft.panel)

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atis_craft_letter_fold.pdf")
    build(out); print(out)
