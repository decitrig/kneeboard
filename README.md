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
| VFR navlog | [navlog/navlog_letter_fold.pdf](navlog/navlog_letter_fold.pdf) | Front: two navlogs (23 legs), side by side. Back: departure / destination / alternate frequencies, enroute frequencies, notes |

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

### Navlog

The navlog is drawn as HTML instead of reportlab. The page is
[navlog/navlog_letter_fold.html](navlog/navlog_letter_fold.html): sheet 1 is
the front, sheet 2 is the back, each a landscape US letter page. The PDF is
printed from it with headless Edge or Chrome (it loads the Barlow and Barlow
Condensed fonts from Google Fonts, so it needs a network connection):

```sh
msedge --headless=new --no-pdf-header-footer --virtual-time-budget=15000 \
  --print-to-pdf=navlog/navlog_letter_fold.pdf \
  "file:///$PWD/navlog/navlog_letter_fold.html"
```

Each half-letter panel on the front is a complete navlog. The left panel has
the route header (aircraft, date, from, to, cruise power, TAS, GPH, fuel) and
11 legs; the right panel continues the route with 12 more.
