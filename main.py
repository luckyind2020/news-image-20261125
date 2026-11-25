#!/usr/bin/env python3
"""The World in One Page — 25 November 2026.

A deterministic program that draws a newspaper front page summing up the
world news of Wednesday 25 November 2026 and writes it to /output/entry.png.

Pure Python standard library only: no network, no fonts on disk, no random
input. The picture is built from a small embedded 5x7 bitmap font and simple
vector shapes, then encoded as a PNG by hand (zlib + struct). Running the
program twice writes the same bytes.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024
OUT_PATH = "/output/entry.png"

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (18, 20, 28)
NAVY = (16, 34, 64)
NAVY_LIGHT = (28, 52, 92)
RED = (178, 34, 34)
RED_SOFT = (226, 84, 66)
GOLD = (201, 162, 39)
TEAL = (14, 110, 110)
SLATE = (84, 88, 102)
LINE = (180, 174, 158)
WHITE = (255, 255, 255)
SKY = (178, 205, 226)
SEA = (34, 84, 128)
SEA_DARK = (22, 60, 96)
SMOKE = (120, 122, 128)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, '#' = on. Uppercase + digits + punctuation.
_GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    """A plain RGB pixel buffer with tiny vector helpers."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def _offset(self, x, y):
        return (y * self.width + x) * 3

    def put(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            off = self._offset(x, y)
            self.pixels[off:off + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            off = self._offset(x0, yy)
            self.pixels[off:off + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            self.put(x0 + dx * i // steps, y0 + dy * i // steps, color)

    def disc(self, cx, cy, radius, color):
        for yy in range(cy - radius, cy + radius + 1):
            for xx in range(cx - radius, cx + radius + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= radius * radius:
                    self.put(xx, yy, color)

    def triangle(self, points, color):
        (ax, ay), (bx, by), (cx, cy) = points
        min_x = max(0, min(ax, bx, cx))
        max_x = min(self.width - 1, max(ax, bx, cx))
        min_y = max(0, min(ay, by, cy))
        max_y = min(self.height - 1, max(ay, by, cy))
        denom = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if denom == 0:
            return
        for yy in range(min_y, max_y + 1):
            for xx in range(min_x, max_x + 1):
                w0 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / denom
                w1 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / denom
                w2 = 1 - w0 - w1
                if w0 >= 0 and w1 >= 0 and w2 >= 0:
                    self.put(xx, yy, color)

    def glyph(self, x, y, char, scale, color):
        rows = _GLYPHS.get(char.upper(), _GLYPHS["?"])
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell == "#":
                    self.rect(x + c * scale, y + r * scale, scale, scale, color)

    def text(self, x, y, message, scale, color):
        cursor = x
        for char in message:
            self.glyph(cursor, y, char, scale, color)
            cursor += 6 * scale
        return cursor

    def text_width(self, message, scale):
        return len(message) * 6 * scale

    def wrap(self, message, max_width, scale):
        """Greedy word wrap; returns a list of lines fitting max_width."""
        limit = max(1, max_width // (6 * scale))
        words = message.split(" ")
        lines = []
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if len(trial) <= limit:
                current = trial
            else:
                if current:
                    lines.append(current)
                while len(word) > limit:
                    lines.append(word[:limit])
                    word = word[limit:]
                current = word
        if current:
            lines.append(current)
        return lines

    def paragraph(self, x, y, message, max_width, scale, color, leading=None):
        step = (leading if leading is not None else 10 * scale)
        lines = self.wrap(message, max_width, scale)
        for i, line in enumerate(lines):
            self.text(x, y + i * step, line, scale, color)
        return y + len(lines) * step


# ---------------------------------------------------------------- PNG encode
def _chunk(kind, payload):
    out = struct.pack(">I", len(payload)) + kind + payload
    out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    header = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    body = _chunk(b"IHDR", header)
    body += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    body += _chunk(b"IEND", b"")
    return b"\x89PNG\r\n\x1a\n" + body


# ---------------------------------------------------------------- the stories
# Headlines verified against Reuters / BBC / AP reporting of 25 Nov 2026.
LEAD = {
    "kicker": "UKRAINE WAR",
    "headline": "KYIV CONFIRMS DRONE STRIKE ON RUSSIAN SHIP IN GULF OF FINLAND",
    "standfirst": (
        "Zelenskiy takes responsibility for the weekend attack as Norway, "
        "a staunch ally, urges caution. Ukraine also says it sank a Russian "
        "warship off Libya as the war at sea spreads."
    ),
}

CARDS = [
    {
        "kicker": "MIDDLE EAST",
        "color": RED_SOFT,
        "headline": "HOUTHIS HIT RIYADH TOWER, 11 HURT",
        "body": (
            "A drone strike on the capital's tallest tower wounds eleven, "
            "the second in a week."
        ),
    },
    {
        "kicker": "TECH TRIAL",
        "color": TEAL,
        "headline": "HUAWEI CONVICTED IN US TRIAL",
        "body": (
            "Huawei is found guilty of stealing trade secrets in a US "
            "criminal trial."
        ),
    },
    {
        "kicker": "WASHINGTON",
        "color": NAVY_LIGHT,
        "headline": "CIA AND SPY CHIEF HIT BY CYBER BREACH",
        "body": (
            "Unclassified information is compromised in a breach at the CIA "
            "and the spy chief's office."
        ),
    },
]

STRIP = [
    ("NATO", "Early-warning jets to deploy in Poland after missiles land"),
    ("NEPAL", "5.6 quake shakes Koshi Province near the China border"),
    ("SEOUL", "Education minister quits over exam-cheating scandal"),
    ("SPORT", "England level T20 series with eight-wicket win in Australia"),
]


# ---------------------------------------------------------------- drawing
def draw_sea_scene(canvas, x, y, w, h):
    """A small illustration: sky, sea, a cargo ship and a drone."""
    canvas.rect(x, y, w, h, SKY)
    horizon = y + int(h * 0.52)
    canvas.rect(x, horizon, w, h - (horizon - y), SEA)
    # sun
    canvas.disc(x + w - 70, y + 58, 26, GOLD)
    # distant clouds
    for cx, cy, cw in ((x + 30, y + 34, 90), (x + 150, y + 22, 70)):
        canvas.rect(cx, cy, cw, 14, WHITE)
        canvas.rect(cx + 12, cy - 8, cw - 36, 10, WHITE)
    # waves
    for row in range(4):
        wy = horizon + 16 + row * 18
        for wx in range(x + 8, x + w - 8, 44):
            canvas.line(wx, wy, wx + 22, wy - 6, SEA_DARK)
            canvas.line(wx + 22, wy - 6, wx + 44, wy, SEA_DARK)
    # cargo ship: hull, containers, funnel, smoke
    hull_y = horizon + 34
    canvas.triangle(
        [(x + 40, hull_y), (x + w - 46, hull_y), (x + 78, hull_y + 34)],
        (24, 26, 32),
    )
    canvas.triangle(
        [(x + w - 46, hull_y), (x + w - 86, hull_y + 34), (x + 78, hull_y + 34)],
        (24, 26, 32),
    )
    canvas.rect(x + 96, hull_y - 30, 46, 30, RED_SOFT)
    canvas.rect(x + 150, hull_y - 30, 46, 30, GOLD)
    canvas.rect(x + 204, hull_y - 30, 46, 30, TEAL)
    canvas.rect(x + w - 96, hull_y - 52, 16, 52, (40, 40, 48))
    for i, (sx, sy, sr) in enumerate(((x + w - 88, hull_y - 66, 9),
                                      (x + w - 76, hull_y - 80, 7),
                                      (x + w - 62, hull_y - 92, 5))):
        canvas.disc(sx, sy, sr, SMOKE)
    # drone above the ship
    dx, dy = x + 92, y + 62
    canvas.disc(dx, dy, 7, INK)
    canvas.hline(dx - 22, dy - 4, 44, INK)
    canvas.disc(dx - 22, dy - 4, 4, INK)
    canvas.disc(dx + 22, dy - 4, 4, INK)
    canvas.line(dx, dy + 6, dx + 26, dy + 40, INK)
    canvas.line(dx + 26, dy + 40, dx + 40, dy + 34, RED)


def draw_kicker_chip(canvas, x, y, label, color):
    pad = 10
    width = canvas.text_width(label, 2) + pad * 2
    canvas.rect(x, y, width, 30, color)
    canvas.text(x + pad, y + 7, label, 2, WHITE)
    return width


def draw_card(canvas, x, y, w, h, card):
    canvas.rect(x, y, w, h, WHITE)
    canvas.hline(x, y, w, card["color"], thick=2)
    canvas.hline(x, y + h - 2, w, LINE, thick=2)
    canvas.vline(x, y, h, LINE, thick=2)
    canvas.vline(x + w - 2, y, h, LINE, thick=2)
    inner = x + 18
    draw_kicker_chip(canvas, inner, y + 18, card["kicker"], card["color"])
    canvas.paragraph(inner, y + 62, card["headline"], w - 36, 3, INK, leading=30)
    canvas.paragraph(inner, y + 160, card["body"], w - 36, 2, SLATE, leading=19)


def draw_front_page():
    page = Canvas(WIDTH, HEIGHT, PAPER)

    # masthead
    page.rect(0, 0, WIDTH, 148, NAVY)
    page.rect(0, 148, WIDTH, 6, GOLD)
    title = "THE WORLD TODAY"
    title_w = page.text_width(title, 7)
    page.text((WIDTH - title_w) // 2, 34, title, 7, WHITE)
    date_line = "WEDNESDAY 25 NOVEMBER 2026  -  THE DAY IN ONE PICTURE"
    date_w = page.text_width(date_line, 2)
    page.text((WIDTH - date_w) // 2, 108, date_line, 2, GOLD)

    # lead story
    lead_y = 176
    lead_h = 300
    page.rect(24, lead_y, WIDTH - 48, lead_h, WHITE)
    page.hline(24, lead_y, WIDTH - 48, RED, thick=3)
    draw_kicker_chip(page, 48, lead_y + 20, LEAD["kicker"], RED)
    page.paragraph(48, lead_y + 66, LEAD["headline"], 560, 4, INK, leading=40)
    page.paragraph(48, lead_y + 204, LEAD["standfirst"], 560, 2, SLATE, leading=19)
    draw_sea_scene(page, 640, lead_y + 20, 336, 260)

    # three cards
    cards_y = 500
    cards_h = 252
    gap = 20
    card_w = (WIDTH - 48 - gap * 2) // 3
    for i, card in enumerate(CARDS):
        draw_card(page, 24 + i * (card_w + gap), cards_y, card_w, cards_h, card)

    # also-today strip
    strip_y = 776
    page.rect(24, strip_y, WIDTH - 48, 200, NAVY)
    page.text(48, strip_y + 18, "ALSO TODAY", 3, GOLD)
    page.hline(48, strip_y + 52, WIDTH - 96, NAVY_LIGHT, thick=2)
    row_y = strip_y + 70
    for label, item in STRIP:
        page.text(48, row_y, label + "  -", 2, GOLD)
        label_w = page.text_width(label + "  -", 2)
        page.paragraph(48 + label_w + 12, row_y, item, WIDTH - 48 - label_w - 60, 2,
                       WHITE, leading=20)
        row_y += 32

    # footer
    page.text(24, 992, "SUMMARY OF THE WORLD NEWS OF 25 NOVEMBER 2026", 2, SLATE)
    page.text(1024 - 24 - page.text_width("PAGE 1 OF 1", 2), 992, "PAGE 1 OF 1", 2, SLATE)
    return page


def main():
    page = draw_front_page()
    data = encode_png(page)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as handle:
        handle.write(data)
    print("wrote %s (%d bytes)" % (OUT_PATH, len(data)))


if __name__ == "__main__":
    main()
