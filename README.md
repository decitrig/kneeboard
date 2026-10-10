# kneeboard

Printable kneeboard templates for private pilot flying (C172).

Every template is a landscape US letter sheet folded in half into two
half-letter kneeboard panels and printed double-sided. Margins are symmetric
about the fold, so the back lines up whichever edge the printer flips on.

| Template | PDF | What's on it |
|---|---|---|
| ATIS | [atis/atis_letter_fold.pdf](atis/atis_letter_fold.pdf) | 4 ATIS blocks per panel, 16 total |
| CRAFT | [craft/craft_letter_fold.pdf](craft/craft_letter_fold.pdf) | 3 CRAFT clearance / flight following blocks per panel, 12 total |
| ATIS + CRAFT | [atis_craft/atis_craft_letter_fold.pdf](atis_craft/atis_craft_letter_fold.pdf) | ATIS panel left, CRAFT panel right, both sides: 8 ATIS + 6 CRAFT |

## Regenerating

Each PDF is drawn by the Python script beside it using
[reportlab](https://pypi.org/project/reportlab/).

```sh
pip install reportlab
python3 atis/make_atis.py
python3 craft/make_craft.py
python3 atis_craft/make_atis_craft.py
```

Each script writes its PDF into its own folder. The combined sheet imports
the panel designs from `atis/` and `craft/`, so rerun it after changing
either of those.
