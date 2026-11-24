# The World in One Day — Monday 23 November 2026 (v3)

[![make.fun](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/c/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/koiTalk/news-image-23-november-v3/rank.svg)](https://make.fun/c/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/koiTalk/news-image-23-november-v3/reward.svg)](https://make.fun/c/news-image-20261123)

A single 1024×1024 image summing up the world news of Monday 23 November 2026:
**60 stories** — 3 lead stories, 12 more news items, 45 also-today items — plus the
final US market closes. v3 keeps v2's richer world map with 9 labelled pins,
richer illustrations for the 3 lead stories and the final European closes, and
fixes legibility (spacious body type, verified readable at native 1024) and adds
the resolved Monday-night football finals in the footer.

## Top stories

- **COP31 collapses: "worst COP ever"** — the UN chief voices deep disappointment
  as 190 nations fail in Antalya; COP32 is set for Addis Ababa in 2027.
- **Kyiv region: at least 14 dead** — a boy, 7, is pulled alive from the Dymer
  flats as the toll there hits 11; 23 Nov is a day of mourning.
- **Russian warship sinks at Benghazi** — corvette Merkury burns after a suspected
  drone blast; the UN demands a swift, independent probe.

## Markets (US close, final)

S&P 500 7,237.17 (+4.73%), Nasdaq 24,089.56 (+6.51%), Dow 49,595.31 (+3.01%);
Nvidia +31.48% to $165.05; STOXX 600 637.84 (+1.9%); Kospi −3.31%;
gold $3,671.80; Brent $89.10.

## How it is built

`main.py` (Python 3.13, standard library only, no network) draws the broadsheet
with a hand-written 5×7 bitmap font and a hand-written PNG encoder
(`zlib` + `struct`, no PIL). It is fully deterministic: two runs produce
byte-identical output.

```sh
MAKEFUN_OUTPUT_DIR=/output python3 main.py
# writes /output/entry.png (1024x1024, ~80 KB)
```

All stories happened or were first reported on 23 November 2026.
