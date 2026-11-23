#!/usr/bin/env python3
"""Draw the 22 November 2026 world-news front page (1024x1024 PNG).

Six verified stories, one broadsheet: a navy masthead naming the day,
then a 2x3 grid of cards. Each card has a small drawn icon, a region and
field kicker, a two-line headline and a three-line sub that explains the
event on its own. Run: python3 draw-image.py  ->  entry.png
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 240, 226)
NAVY = (24, 38, 66)
INK = (28, 39, 51)
SUB = (74, 74, 69)
BORDER = (216, 207, 186)
CARD = (255, 255, 255)
KICKER_SUB = (169, 188, 221)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
REG = FONT_DIR + "DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(path, text, start, max_width, minimum=18):
    """Largest size at or below start whose text fits max_width."""
    size = start
    while size > minimum:
        f = font(path, size)
        if f.getbbox(text)[2] <= max_width:
            return f
        size -= 1
    return font(path, minimum)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap into lines that fit max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(draw, centre_x, y, text, fnt, fill, tracking=6):
    """Draw text centred with extra space between letters."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = centre_x - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


# ---------------------------------------------------------------- icons
def icon_globe(d, x, y, s, c):
    d.ellipse([x, y, x + s, y + s], outline=c, width=5)
    d.ellipse([x + s * 0.28, y, x + s * 0.72, y + s], outline=c, width=4)
    d.line([x, y + s * 0.5, x + s, y + s * 0.5], fill=c, width=4)
    d.arc([x, y + s * 0.18, x + s, y + s * 0.82], 200, 340, fill=c, width=4)
    d.arc([x, y + s * 0.18, x + s, y + s * 0.82], 20, 160, fill=c, width=4)


def icon_ship(d, x, y, s, c):
    d.polygon([(x, y + s * 0.58), (x + s, y + s * 0.58),
               (x + s * 0.84, y + s * 0.84), (x + s * 0.16, y + s * 0.84)], fill=c)
    d.rectangle([x + s * 0.42, y + s * 0.42, x + s * 0.58, y + s * 0.58], fill=c)
    d.line([x + s * 0.5, y + s * 0.06, x + s * 0.5, y + s * 0.58], fill=c, width=5)
    d.polygon([(x + s * 0.5, y + s * 0.1), (x + s * 0.84, y + s * 0.36),
               (x + s * 0.5, y + s * 0.36)], fill=c)
    d.line([x, y + s * 0.94, x + s, y + s * 0.94], fill=c, width=4)
    d.arc([x + s * 0.08, y + s * 0.88, x + s * 0.4, y + s], 0, 180, fill=c, width=4)
    d.arc([x + s * 0.6, y + s * 0.88, x + s * 0.92, y + s], 0, 180, fill=c, width=4)


def icon_block(d, x, y, s, c):
    d.rectangle([x + s * 0.12, y + s * 0.08, x + s * 0.62, y + s * 0.88], fill=c)
    d.polygon([(x + s * 0.62, y + s * 0.08), (x + s * 0.88, y + s * 0.3),
               (x + s * 0.88, y + s * 0.88), (x + s * 0.62, y + s * 0.88)], fill=(255, 255, 255))
    d.polygon([(x + s * 0.62, y + s * 0.08), (x + s * 0.88, y + s * 0.3),
               (x + s * 0.88, y + s * 0.88), (x + s * 0.62, y + s * 0.88)],
              outline=c, width=4)
    for wy in (0.22, 0.42, 0.62):
        for wx in (0.24, 0.42):
            d.rectangle([x + s * wx, y + s * wy, x + s * (wx + 0.09), y + s * (wy + 0.1)],
                        fill=(255, 255, 255))
    d.polygon([(x + s * 0.66, y + s * 0.92), (x + s * 0.78, y + s * 0.78),
               (x + s * 0.9, y + s * 0.92)], fill=c)


def icon_flame(d, x, y, s, c):
    d.polygon([(x + s * 0.5, y + s * 0.02), (x + s * 0.72, y + s * 0.26),
               (x + s * 0.88, y + s * 0.52), (x + s * 0.82, y + s * 0.78),
               (x + s * 0.62, y + s * 0.94), (x + s * 0.38, y + s * 0.94),
               (x + s * 0.18, y + s * 0.78), (x + s * 0.12, y + s * 0.52),
               (x + s * 0.28, y + s * 0.26)], fill=c)
    d.polygon([(x + s * 0.5, y + s * 0.44), (x + s * 0.66, y + s * 0.62),
               (x + s * 0.6, y + s * 0.82), (x + s * 0.4, y + s * 0.82),
               (x + s * 0.34, y + s * 0.62)], fill=(255, 255, 255))


def icon_drone(d, x, y, s, c):
    d.rectangle([x + s * 0.38, y + s * 0.38, x + s * 0.62, y + s * 0.62], fill=c)
    for ax, ay in ((0.12, 0.12), (0.88, 0.12), (0.12, 0.88), (0.88, 0.88)):
        d.line([x + s * 0.5, y + s * 0.5, x + s * ax, y + s * ay], fill=c, width=5)
        d.ellipse([x + s * (ax - 0.12), y + s * (ay - 0.12),
                   x + s * (ax + 0.12), y + s * (ay + 0.12)], outline=c, width=5)
    d.ellipse([x + s * 0.46, y + s * 0.46, x + s * 0.54, y + s * 0.54],
              fill=(255, 255, 255))


def icon_factory(d, x, y, s, c):
    d.polygon([(x + s * 0.06, y + s * 0.88), (x + s * 0.06, y + s * 0.5),
               (x + s * 0.3, y + s * 0.3), (x + s * 0.54, y + s * 0.5),
               (x + s * 0.78, y + s * 0.3), (x + s * 0.94, y + s * 0.46),
               (x + s * 0.94, y + s * 0.88)], fill=c)
    d.rectangle([x + s * 0.14, y + s * 0.1, x + s * 0.24, y + s * 0.48], fill=c)
    for wx in (0.18, 0.42, 0.66):
        d.rectangle([x + s * wx, y + s * 0.62, x + s * (wx + 0.1), y + s * 0.74],
                    fill=(255, 255, 255))
    for cx, cy, r in ((0.3, 0.16, 0.07), (0.44, 0.08, 0.05)):
        d.ellipse([x + s * (cx - r), y + s * (cy - r),
                   x + s * (cx + r), y + s * (cy + r)], fill=c)


ICONS = {
    "globe": icon_globe,
    "ship": icon_ship,
    "block": icon_block,
    "flame": icon_flame,
    "drone": icon_drone,
    "factory": icon_factory,
}

# ---------------------------------------------------------------- stories
# (icon, accent, kicker, headline lines, sub)
STORIES = [
    ("globe", (30, 122, 76), "CLIMATE \u00b7 WORLD",
     ["COP31 ENDS", "WITH NO DEAL"],
     "Nearly 200 nations leave Antalya with no agreement on fossil fuels or climate finance."),
    ("ship", (140, 90, 43), "WAR AT SEA \u00b7 LIBYA",
     ["RUSSIAN WARSHIP", "HIT IN BENGHAZI"],
     "Suspected Ukrainian sea drones strike the corvette Merkury at a Libyan naval base."),
    ("block", (169, 50, 38), "WAR \u00b7 UKRAINE",
     ["DRONE FLATTENS", "FLATS NEAR KYIV"],
     "A strike on a five-storey block in Dymer kills 2; 14 people are missing, two of them children."),
    ("flame", (91, 94, 166), "MIDDLE EAST \u00b7 WEST BANK",
     ["SETTLER ARSON", "IN WEST BANK"],
     "Settlers burn 12 cars in four West Bank villages; Eisenkot calls it \u201cJewish terrorism\u201d."),
    ("drone", (15, 110, 124), "AFRICA \u00b7 SUDAN",
     ["DRONES STRIKE", "KHARTOUM, UN HIT"],
     "Drones hit homes and a UN building in the Sudanese capital; 4 people are killed."),
    ("factory", (200, 90, 23), "ASIA \u00b7 DISASTER",
     ["FACTORY FIRE", "3 DEAD, 37 MISSING"],
     "Rescuers search the ruins of a candy plant in Cikande, Indonesia; 37 workers are still unaccounted for."),
]

FOOTER = "Every story above happened or was first reported on 22 November 2026."


def draw_card(d, x, y, w, h, story):
    icon_name, accent, kicker, headline, sub = story
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=BORDER, width=1)
    d.rectangle([x, y, x + w, y + 6], fill=accent)
    ICONS[icon_name](d, x + 20, y + 30, 92, accent)
    kf = font(BOLD, 20)
    d.text((x + 128, y + 34), kicker, font=kf, fill=accent)
    max_head = w - 128 - 20
    longest = max(headline, key=len)
    hf = fit_font(BOLD, longest, 32, max_head)
    hy = y + 62
    for line in headline:
        d.text((x + 128, hy), line, font=hf, fill=INK)
        hy += int(hf.size * 1.18)
    sf = font(REG, 23)
    lines = wrap(d, sub, sf, w - 40)
    assert len(lines) <= 3, (sub, lines)
    sy = y + 152
    for line in lines:
        d.text((x + 20, sy), line, font=sf, fill=SUB)
        sy += 30


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 140], fill=NAVY)
    date_font = fit_font(BOLD, "22 NOVEMBER 2026", 88, W - 80)
    d.text((W // 2, 18), "22 NOVEMBER 2026", font=date_font, fill=(255, 255, 255),
           anchor="ma")
    kick_font = font(BOLD, 24)
    draw_tracked(d, W // 2, 102, "SUNDAY \u00b7 THE WORLD IN ONE IMAGE",
                 kick_font, KICKER_SUB, tracking=7)

    # Grid of six cards
    margin, gutter, top, footer_h = 18, 14, 156, 42
    col_w = (W - 2 * margin - gutter) // 2
    row_h = (H - footer_h - top - 2 * gutter) // 3
    for i, story in enumerate(STORIES):
        cx = margin + (i % 2) * (col_w + gutter)
        cy = top + (i // 2) * (row_h + gutter)
        draw_card(d, cx, cy, col_w, row_h, story)

    # Footer
    ff = font(REG, 22)
    d.text((W // 2, H - 34), FOOTER, font=ff, fill=(107, 101, 88), anchor="ma")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
