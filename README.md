# The World Tonight — Monday 23 November 2026

A make.fun entry for the `news-image-20261123` bounty: one program that
draws a one-page newspaper front page summing up the world's news of
Monday 23 November 2026 and writes it to `/output/entry.png`.

## Stories covered

- **Strait of Hormuz (lead)** — tankers struck and mined; the war at sea
  reaches Saudi Arabia and Bahrain.
- **COP31, Antalya** — climate talks collapse with no deal; the EU rejected
  a final text that never named fossil fuels.
- **Poland** — three objects that fell on Friday were Russian cruise
  missiles, Warsaw confirmed; NATO to meet.
- **Ukraine** — a Russian drone hit a five-storey block in Dymer, north of
  Kyiv; two killed, 11 missing.
- **South Sudan** — 24 civilians killed in fresh violence.
- **Mercury** — BepiColombo enters orbit, only the second mission ever.
- **Also today** — Mexico captures cartel boss "El Chapo Isidro", Asian
  markets on alert, Marquez's eighth MotoGP title, Shuri Castle restored.

## How it works

`main.py` is pure Python standard library. It defines its own 5x7 bitmap
font, a tiny raster canvas, and a hand-rolled PNG encoder (zlib + struct),
then draws the whole page — masthead, lead story with a night scene of
tankers in the Strait, six story panels and an "Also today" strip — with
no network, no file reads and no timestamps, so two runs are byte-identical.

Run it with:

```
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Licence

MIT — see `LICENSE`.
