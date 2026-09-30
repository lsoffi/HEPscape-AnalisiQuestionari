"""Single pooled word wall with each word split by its two-kit contribution."""

import csv
import html
import math
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager


def generate(texts, kits, output, event):
    from .comparison import tokens, COLORS

    out = Path(output)
    counts = [Counter(t for text in group for t in tokens(text)) for group in texts]
    words = sorted(
        set(counts[0]) | set(counts[1]), key=lambda w: (-sum(c[w] for c in counts), w)
    )
    fontpath = font_manager.findfont(
        font_manager.FontProperties(family="DejaVu Sans", weight="bold")
    )
    regular = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans"))
    W, H = 2600, 1800
    for factor in [36, 34, 32, 30, 28, 26, 24, 20, 16, 12, 8]:
        boxes = []
        placed = []
        for word in words:
            n = sum(c[word] for c in counts)
            size = round(factor * math.sqrt(n))
            font = ImageFont.truetype(fontpath, size)
            bbox = font.getbbox(word)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            for j in range(22000):
                angle = j * 0.39
                radius = 1.8 * math.sqrt(j)
                x = int(W / 2 + radius * math.cos(angle) * 6 - tw / 2)
                y = int(930 + radius * math.sin(angle) * 3.5 - th / 2)
                b = (x - 9, y - 9, x + tw + 9, y + th + 9)
                if b[0] < 80 or b[2] > W - 80 or b[1] < 330 or b[3] > H - 190:
                    continue
                if any(
                    b[0] < a[2] and b[2] > a[0] and b[1] < a[3] and b[3] > a[1]
                    for a in boxes
                ):
                    continue
                boxes.append(b)
                placed.append((word, n, size, x, y, bbox))
                break
            else:
                break
        if len(placed) == len(words):
            break
    if len(placed) != len(words):
        raise ValueError("Non tutte le parole entrano nel word wall.")
    im = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(im)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>'
    ]

    def text(x, y, s, size, color="#18304F", bold=False):
        f = ImageFont.truetype(fontpath if bold else regular, size)
        draw.text((x, y), s, font=f, fill=color)
        svg.append(
            f'<text x="{x}" y="{y+f.getmetrics()[0]}" font-family="DejaVu Sans" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}">{html.escape(s)}</text>'
        )

    text(
        85,
        55,
        "HEPscape! · LE PAROLE DI " + " E ".join(k.upper() for k in kits),
        56,
        bold=True,
    )
    text(
        85,
        140,
        f"{len(words)} parole diverse · {sum(map(len,texts))} risposte Q2 non vuote · {event}",
        29,
    )
    text(85, 215, f"● {kits[0]}: {len(texts[0])} risposte", 33, COLORS[0], True)
    text(850, 215, f"● {kits[1]}: {len(texts[1])} risposte", 33, COLORS[1], True)
    for i, (word, n, size, x, y, bbox) in enumerate(placed):
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        mask = Image.new("L", (tw, th), 0)
        ImageDraw.Draw(mask).text(
            (-bbox[0], -bbox[1]),
            word,
            font=ImageFont.truetype(fontpath, size),
            fill=255,
        )
        split = round(tw * counts[0][word] / n)
        ink = Image.new("RGB", (tw, th), COLORS[1])
        if split:
            ImageDraw.Draw(ink).rectangle((0, 0, split - 1, th), fill=COLORS[0])
        im.paste(ink, (x, y), mask)
        title = html.escape(
            f"{kits[0]}: {counts[0][word]}; {kits[1]}: {counts[1][word]}; totale: {n}"
        )
        svg.append(
            f'<defs><clipPath id="blue{i}"><rect x="{x}" y="{y}" width="{split}" height="{th}"/></clipPath></defs>'
        )
        for color, clip in [
            (COLORS[1], ""),
            (COLORS[0], f' clip-path="url(#blue{i})"'),
        ]:
            svg.append(
                f'<text x="{x-bbox[0]}" y="{y-bbox[1]+ImageFont.truetype(fontpath,size).getmetrics()[0]}" font-family="DejaVu Sans" font-size="{size}" font-weight="bold" fill="{color}"{clip}><title>{title}</title>{html.escape(word)}</text>'
            )
    text(
        85,
        H - 140,
        "Dimensione = radice del totale di schede che citano la parola; ogni parola conta una volta per scheda.",
        26,
    )
    text(
        85,
        H - 95,
        "Quota blu/verde della larghezza = contributo di ciascun kit al totale. Conteggi grezzi, non percentuali normalizzate.",
        26,
    )
    text(
        85,
        H - 50,
        "Forme esatte, senza stopword né annotazioni editoriali. Le parole condivise compaiono una sola volta.",
        24,
    )
    path = out / "12_word_wall_insieme.png"
    im.save(path, dpi=(200, 200))
    (out / "12_word_wall_insieme.svg").write_text(
        "\n".join(svg) + "</svg>", encoding="utf-8"
    )
    with (out / "word_wall_insieme.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        w = csv.writer(f)
        w.writerow(["parola", *kits, "totale", "quota_kit1"])
        for word in words:
            n = sum(c[word] for c in counts)
            w.writerow([word, counts[0][word], counts[1][word], n, counts[0][word] / n])
    print(f"Word wall: {len(placed)} parole, tutte incluse senza sovrapposizioni.")
    return path
