"""The World Tonight -- Monday 23 November 2026.

Pure standard-library entry: draws a one-page newspaper front page summing
up the day's world news and writes it to /output/entry.png as a PNG.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
The grader runs it as `python3 -P -s main.py` with no network, so everything
is drawn here from data in this file: a small 5x7 bitmap font defined below,
a tiny raster canvas, and a hand-rolled PNG encoder (zlib + struct only).
No sibling imports, no file reads, no timestamps: two runs are byte-identical.
"""

import os
import struct
import zlib

# --------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
# Drawn from scratch for this entry.
# --------------------------------------------------------------------------
_G = {}


def _glyph(ch, rows):
    _G[ch] = rows


_glyph("A", (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"))
_glyph("B", ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."))
_glyph("C", (".####", "#....", "#....", "#....", "#....", "#....", ".####"))
_glyph("D", ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."))
_glyph("E", ("#####", "#....", "#....", "####.", "#....", "#....", "#####"))
_glyph("F", ("#####", "#....", "#....", "####.", "#....", "#....", "#...."))
_glyph("G", (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."))
_glyph("H", ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"))
_glyph("I", ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"))
_glyph("J", ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."))
_glyph("K", ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"))
_glyph("L", ("#....", "#....", "#....", "#....", "#....", "#....", "#####"))
_glyph("M", ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"))
_glyph("N", ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"))
_glyph("O", (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."))
_glyph("P", ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."))
_glyph("Q", (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"))
_glyph("R", ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"))
_glyph("S", (".####", "#....", "#....", ".###.", "....#", "....#", "####."))
_glyph("T", ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."))
_glyph("U", ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."))
_glyph("V", ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."))
_glyph("W", ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"))
_glyph("X", ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"))
_glyph("Y", ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."))
_glyph("Z", ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"))
_glyph("0", (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."))
_glyph("1", ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."))
_glyph("2", (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"))
_glyph("3", ("####.", "....#", "....#", ".###.", "....#", "....#", "####."))
_glyph("4", ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."))
_glyph("5", ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."))
_glyph("6", (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."))
_glyph("7", ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."))
_glyph("8", (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."))
_glyph("9", (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."))

_glyph("a", (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"))
_glyph("b", ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."))
_glyph("c", (".....", ".....", ".####", "#....", "#....", "#....", ".####"))
_glyph("d", ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"))
_glyph("e", (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."))
_glyph("f", ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."))
_glyph("g", (".....", ".####", "#...#", "#...#", ".####", "....#", "...#.", "..##."))
_glyph("h", ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"))
_glyph("i", ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."))
_glyph("j", ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."))
_glyph("k", ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."))
_glyph("l", (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."))
_glyph("m", (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"))
_glyph("n", (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"))
_glyph("o", (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."))
_glyph("p", (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."))
_glyph("q", (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"))
_glyph("r", (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."))
_glyph("s", (".....", ".....", ".####", "#....", ".###.", "....#", "####."))
_glyph("t", (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."))
_glyph("u", (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"))
_glyph("v", (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."))
_glyph("w", (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."))
_glyph("x", (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"))
_glyph("y", (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#..", ".#..."))
_glyph("z", (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"))
_glyph(" ", (".....", ".....", ".....", ".....", ".....", ".....", "....."))
_glyph(".", (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."))
_glyph(",", (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."))
_glyph(":", (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."))
_glyph(";", (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."))
_glyph("!", ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."))
_glyph("?", (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."))
_glyph("'", ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."))
_glyph('"', (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."))
_glyph("(", ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."))
_glyph(")", (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."))
_glyph("-", (".....", ".....", ".....", ".###.", ".....", ".....", "....."))
_glyph("/", ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."))
_glyph("&", (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"))
_glyph("%", ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"))
_glyph("+", (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."))
_glyph("=", (".....", ".....", "#####", ".....", "#####", ".....", "....."))
_glyph("*", (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."))
_glyph("[", (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."))
_glyph("]", (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."))


# --------------------------------------------------------------------------
# Raster canvas (RGB bytearray) and PNG encoder.
# --------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = c

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:(yy * self.w + x1) * 3] = c * (x1 - x0)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else -1
            if dx >= 0:
                self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r + t:
                    self.set(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # Scanline fill of a triangle.
        ys = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys

        def edge_x(y, p, q):
            if q[1] == p[1]:
                return p[0]
            return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])

        for y in range(ay, cy + 1):
            if y < by:
                xa = edge_x(y, (ax, ay), (bx, by))
            else:
                xa = edge_x(y, (bx, by), (cx, cy))
            xb = edge_x(y, (ax, ay), (cx, cy))
            if xa > xb:
                xa, xb = xb, xa
            self.rect(int(xa), y, int(xb) - int(xa) + 1, 1, c)


def _png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + _png_chunk(b"IEND", b""))


# --------------------------------------------------------------------------
# Text: measure, draw, wrap.
# --------------------------------------------------------------------------
def text_w(s, scale, spacing=1):
    return len(s) * (5 + spacing) * scale - spacing * scale


def draw_text(cv, x, y, s, scale, color, spacing=1):
    cx = x
    adv = (5 + spacing) * scale
    for ch in s:
        glyph = _G.get(ch)
        if glyph is None:
            glyph = _G["?"]
        for r, row in enumerate(glyph):
            for col, cell in enumerate(row):
                if cell == "#":
                    cv.rect(cx + col * scale, y + r * scale, scale, scale, color)
        cx += adv
    return cx


def draw_text_centered(cv, cx, y, s, scale, color, spacing=1):
    draw_text(cv, cx - text_w(s, scale, spacing) // 2, y, s, scale, color, spacing)


def wrap_text(s, scale, max_w, spacing=1):
    """Greedy word wrap; returns list of lines."""
    adv = (5 + spacing) * scale
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if len(trial) * adv - spacing * scale <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# Palette and layout.
# --------------------------------------------------------------------------
W = H = 1024
PAPER = (246, 241, 229)
PANEL = (255, 253, 246)
INK = (26, 26, 26)
MUTED = (96, 89, 74)
RED = (179, 38, 30)
NAVY = (22, 40, 63)
NAVY2 = (38, 68, 104)
SEA = (24, 74, 88)
PALE = (214, 224, 235)
GOLD = (201, 154, 44)
TEAL = (38, 110, 110)
ORANGE = (214, 96, 32)
BORDER = (205, 196, 172)
RULE = (60, 54, 44)


def draw_bold(cv, x, y, s, scale, color):
    draw_text(cv, x, y, s, scale, color)
    draw_text(cv, x + 1, y, s, scale, color)


def draw_icon(cv, name, x, y, c):
    """A 30x30 pictogram, top-left (x, y)."""
    if name == "globe":
        cv.ring(x + 15, y + 15, 12, c, 2)
        cv.line(x + 3, y + 15, x + 27, y + 15, c)
        cv.line(x + 15, y + 3, x + 15, y + 27, c)
        cv.line(x + 8, y + 8, x + 22, y + 22, c)
    elif name == "missile":
        cv.line(x + 6, y + 24, x + 22, y + 8, c)
        cv.line(x + 8, y + 26, x + 24, y + 10, c)
        cv.triangle(x + 22, y + 8, x + 28, y + 2, x + 26, y + 12, c)
        cv.triangle(x + 6, y + 24, x + 2, y + 28, x + 12, y + 26, c)
        cv.disc(x + 26, y + 4, 2, c)
    elif name == "building":
        cv.rect(x + 7, y + 10, 16, 18, c)
        cv.triangle(x + 7, y + 10, x + 23, y + 10, x + 15, y + 4, c)
        for wy in (14, 19, 24):
            for wx in (11, 17):
                cv.rect(wx, wy, 2, 2, PANEL)
        cv.disc(x + 24, y + 6, 2, c)
        cv.disc(x + 27, y + 3, 2, c)
    elif name == "warn":
        cv.triangle(x + 15, y + 3, x + 28, y + 27, x + 2, y + 27, c)
        cv.rect(x + 14, y + 11, 2, 9, PANEL)
        cv.rect(x + 14, y + 22, 2, 2, PANEL)
    elif name == "flame":
        cv.triangle(x + 15, y + 2, x + 26, y + 24, x + 4, y + 24, c)
        cv.triangle(x + 15, y + 12, x + 21, y + 24, x + 9, y + 24, GOLD)
        cv.rect(x + 4, y + 24, 22, 3, c)
    elif name == "planet":
        cv.disc(x + 15, y + 15, 9, c)
        cv.disc(x + 12, y + 12, 2, PANEL)
        cv.disc(x + 18, y + 18, 2, PANEL)
        for t in range(0, 360, 6):
            import math
            ex = int(x + 15 + 14 * math.cos(math.radians(t)))
            ey = int(y + 15 + 5 * math.sin(math.radians(t)))
            cv.set(ex, ey, c)
        cv.rect(x + 26, y + 6, 3, 3, c)


def draw_burst(cv, cx, cy, r, c):
    """An explosion starburst: 8 spikes."""
    import math
    for k in range(8):
        ang = math.radians(k * 45)
        x2 = int(cx + r * math.cos(ang))
        y2 = int(cy + r * math.sin(ang))
        cv.line(cx, cy, x2, y2, c)
        cv.line(cx, cy, int(cx + r * 0.6 * math.cos(ang + 0.4)),
                int(cy + r * 0.6 * math.sin(ang + 0.4)), c)
    cv.disc(cx, cy, r // 3, c)


STORIES = [
    ("globe", "CLIMATE - ANTALYA", ("Climate talks", "collapse, no deal"),
     "Nearly 200 nations left COP31 with no agreement. The EU rejected "
     "a text that never named fossil fuels.", TEAL),
    ("missile", "POLAND - NATO", ("Fallen objects were", "Russian missiles"),
     "Three objects that fell in Poland on Friday were Russian cruise "
     "missiles, Warsaw confirmed. NATO will meet.", RED),
    ("building", "UKRAINE - KYIV REGION", ("Drone hits flats", "north of Kyiv"),
     "A Russian drone struck a five-storey block in Dymer. Two were "
     "killed and 11 are missing, among them two children.", NAVY),
    ("warn", "SOUTH SUDAN", ("24 civilians killed", "in fresh violence"),
     "An attack by SPLA-IO forces left 24 civilians dead, officials "
     "said, in the latest bloodshed in the young nation.", GOLD),
    ("flame", "INDONESIA - BANTEN", ("Factory fire leaves", "dozens missing"),
     "Rescuers pulled bodies from a candy factory blaze in Cikande. "
     "Dozens of workers are still unaccounted for.", ORANGE),
    ("planet", "SPACE - MERCURY", ("BepiColombo reaches", "Mercury orbit"),
     "After eight years in space, the probe entered orbit around "
     "Mercury, only the second mission ever to do so.", TEAL),
]

ALSO = [
    ("MEXICO", "Troops captured FBI most-wanted cartel boss 'El Chapo "
     "Isidro' in Sinaloa; 11 were killed."),
    ("MARKETS", "Asian shares on alert after US stocks plunged on Friday; "
     "Taiwan and South Korea hold emergency talks."),
    ("SPORT", "Marc Marquez won a record-tying eighth MotoGP title at the "
     "Portuguese Grand Prix."),
    ("JAPAN", "Shuri Castle's main hall restored seven years after fire; "
     "it opens to the public on Monday."),
]


def render():
    cv = Canvas(W, H, PAPER)

    # --- masthead ------------------------------------------------------
    draw_text_centered(cv, 512, 22, "THE WORLD TONIGHT", 6, INK)
    cv.rect(24, 74, 976, 4, RED)
    draw_text_centered(cv, 512, 86, "MONDAY 23 NOVEMBER 2026", 2, RED, spacing=2)
    cv.rect(24, 108, 976, 2, RULE)

    # --- lead story: Strait of Hormuz ----------------------------------
    cv.rect(24, 116, 976, 272, NAVY)
    draw_text(cv, 44, 132, "STRAIT OF HORMUZ - WAR AT SEA", 2, GOLD)
    draw_bold(cv, 44, 158, "Tankers ablaze as", 3, (255, 255, 255))
    draw_bold(cv, 44, 182, "the Gulf war widens", 3, (255, 255, 255))
    lead = ("Three oil tankers were struck in and near the Strait of "
            "Hormuz on Friday and Saturday, and two more caught fire on "
            "Sunday after hitting naval mines. Iran says the ships "
            "entered a restricted zone. The war has now reached Saudi "
            "Arabia and Bahrain.")
    y = 224
    for line in wrap_text(lead, 2, 540):
        draw_text(cv, 44, y, line, 2, PALE)
        y += 17
    # illustration: tankers under a pale moon, one burning, mines below
    cv.rect(620, 132, 364, 168, NAVY2)
    cv.disc(944, 158, 16, (232, 228, 210))
    cv.rect(620, 300, 364, 72, SEA)
    # tanker 1
    cv.rect(640, 314, 120, 20, (12, 20, 32))
    cv.rect(700, 300, 28, 14, (226, 222, 210))
    cv.rect(732, 294, 10, 6, RED)
    # tanker 2, burning at the funnel
    cv.rect(790, 314, 110, 20, (12, 20, 32))
    cv.rect(848, 300, 26, 14, (226, 222, 210))
    cv.rect(874, 294, 10, 6, RED)
    draw_burst(cv, 879, 276, 20, (232, 140, 40))
    draw_burst(cv, 879, 276, 12, (240, 200, 60))
    cv.disc(879, 246, 8, (120, 120, 120))
    cv.disc(879, 224, 9, (140, 140, 140))
    cv.disc(879, 202, 7, (120, 120, 120))
    # tanker 3
    cv.rect(920, 318, 60, 16, (12, 20, 32))
    # mines in the water
    for mx, my in ((672, 344), (868, 352)):
        cv.disc(mx, my, 5, (12, 20, 32))
        cv.line(mx - 8, my, mx + 8, my, (12, 20, 32))
        cv.line(mx, my - 8, mx, my + 8, (12, 20, 32))
    # wave marks
    for wx in (660, 760, 860, 940):
        cv.line(wx, 336, wx + 22, 336, (120, 180, 190))
        cv.line(wx + 8, 356, wx + 30, 356, (120, 180, 190))

    # --- six story panels ----------------------------------------------
    xs = [24, 353, 682]
    widths = [317, 317, 318]
    ys = [400, 616]
    for idx, (icon, kicker, head, body, accent) in enumerate(STORIES):
        x = xs[idx % 3]
        y = ys[idx // 3]
        w = widths[idx % 3]
        cv.rect(x, y, w, 204, PANEL)
        cv.rect(x, y, w, 5, accent)
        # border: draw the four edges over the panel fill
        cv.rect(x, y, w, 1, BORDER)
        cv.rect(x, y + 203, w, 1, BORDER)
        cv.rect(x, y, 1, 204, BORDER)
        cv.rect(x + w - 1, y, 1, 204, BORDER)
        draw_icon(cv, icon, x + 14, y + 16, accent)
        draw_text(cv, x + 52, y + 24, kicker, 2, RED)
        draw_bold(cv, x + 14, y + 56, head[0], 2, INK)
        draw_bold(cv, x + 14, y + 74, head[1], 2, INK)
        cv.rect(x + 14, y + 98, w - 28, 1, BORDER)
        by = y + 108
        for line in wrap_text(body, 2, w - 28)[:5]:
            draw_text(cv, x + 14, by, line, 2, (58, 54, 44))
            by += 16

    # --- also today ------------------------------------------------------
    cv.rect(24, 832, 976, 140, PANEL)
    cv.rect(24, 832, 976, 1, BORDER)
    cv.rect(24, 971, 976, 1, BORDER)
    cv.rect(24, 832, 1, 140, BORDER)
    cv.rect(999, 832, 1, 140, BORDER)
    draw_text(cv, 40, 844, "ALSO TODAY", 2, RED)
    for i, (tag, text) in enumerate(ALSO):
        cx = 40 + (i % 2) * 488
        cy = 868 + (i // 2) * 54
        # first line carries the tag, rest are plain
        lines = wrap_text(tag + " - " + text, 2, 462)
        ly = cy
        for li, line in enumerate(lines[:3]):
            if li == 0:
                draw_bold(cv, cx, ly, tag + " -", 2, INK)
                draw_text(cv, cx + text_w(tag + " - ", 2), ly, line[len(tag) + 3:],
                          2, (58, 54, 44))
            else:
                draw_text(cv, cx, ly, line, 2, (58, 54, 44))
            ly += 16

    # --- footer ----------------------------------------------------------
    draw_text_centered(cv, 512, 984,
                       "Sources: AP - Reuters - AFP - BBC - Al Jazeera - Dawn",
                       2, MUTED)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(encode_png(render()))
    print("wrote", path)


if __name__ == "__main__":
    main()
