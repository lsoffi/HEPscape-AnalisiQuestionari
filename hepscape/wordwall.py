import sys, math, csv, random, html

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def generate_wordwall(output, event, valid_count):
    base = Path(output)
    words = [
        (r["parola"], int(r["schede"]))
        for r in csv.DictReader((base / "grafici/frequenze_parole.csv").open())
        if r["tipo"] == "esatta"
    ]
    words.sort(key=lambda v: (-v[1], v[0]))
    from matplotlib import font_manager

    fontpath = font_manager.findfont(
        font_manager.FontProperties(family="DejaVu Sans", weight="bold")
    )
    W, H = 2600, 1600
    palette = ["#335BA6", "#234A8C", "#5F8FC4", "#7BBA48", "#18304F"]
    for factor in [34, 32, 30, 28, 26, 24, 20, 16, 12, 8]:
        rng = random.Random(43)
        boxes = []
        placed = []
        for word, n in words:
            size = round(factor * math.sqrt(n))
            font = ImageFont.truetype(fontpath, size)
            bbox = font.getbbox(word)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            ok = False
            for j in range(18000):
                angle = j * 0.39
                radius = 1.8 * math.sqrt(j)
                x = int(W / 2 + radius * math.cos(angle) * 6 - tw / 2)
                y = int(850 + radius * math.sin(angle) * 3 - th / 2)
                b = (x - 8, y - 8, x + tw + 8, y + th + 8)
                if b[0] < 75 or b[2] > W - 75 or b[1] < 240 or b[3] > H - 155:
                    continue
                if any(
                    b[0] < a[2] and b[2] > a[0] and b[1] < a[3] and b[3] > a[1]
                    for a in boxes
                ):
                    continue
                boxes.append(b)
                placed.append(
                    (word, n, size, x, y, bbox, palette[len(placed) % len(palette)])
                )
                ok = True
                break
            if not ok:
                break
        if len(placed) == len(words):
            break
    if len(placed) != len(words):
        raise ValueError(
            "Troppe parole per il word wall: nessuna parola viene omessa silenziosamente; aumentare il canvas."
        )
    im = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(im)
    title = "Q2 • LE PAROLE DELL’ESPERIENZA"
    subtitle = f"{len(words)} parole diverse nelle {valid_count} risposte testuali | HEPscape! • {event}"
    footer = "Dimensione crescente con la frequenza per scheda; escluse parole funzionali e annotazioni, come nella tavola 12."
    draw.text((85, 55), title, font=ImageFont.truetype(fontpath, 57), fill="#18304F")
    regular = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans"))
    draw.text((85, 135), subtitle, font=ImageFont.truetype(regular, 29), fill="#586B7B")
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>',
        f'<text x="85" y="110" font-family="DejaVu Sans" font-size="57" font-weight="bold" fill="#18304F">{html.escape(title)}</text>',
        f'<text x="85" y="166" font-family="DejaVu Sans" font-size="29" fill="#586B7B">{html.escape(subtitle)}</text>',
    ]
    if not words:
        draw.text(
            (500, 700),
            "Nessuna risposta testuale",
            font=ImageFont.truetype(regular, 55),
            fill="#18304F",
        )
    for word, n, size, x, y, bbox, color in placed:
        draw.text(
            (x - bbox[0], y - bbox[1]),
            word,
            font=ImageFont.truetype(fontpath, size),
            fill=color,
        )
        svg.append(
            f'<text x="{x}" y="{y+bbox[3]-bbox[1]}" font-family="DejaVu Sans" font-size="{size}" font-weight="bold" fill="{color}"><title>{n} schede</title>{html.escape(word)}</text>'
        )
    draw.text(
        (85, H - 85), footer, font=ImageFont.truetype(regular, 25), fill="#586B7B"
    )
    svg.append(
        f'<text x="85" y="{H-60}" font-family="DejaVu Sans" font-size="25" fill="#586B7B">{html.escape(footer)}</text></svg>'
    )
    im.save(base / "HEPscape_Q2_word_wall.png", dpi=(200, 200))
    (base / "HEPscape_Q2_word_wall.svg").write_text("\n".join(svg))
    c = canvas.Canvas(str(base / "HEPscape_Q2_word_wall.pdf"), pagesize=(1170, 720))
    c.drawImage(ImageReader(im), 0, 0, width=1170, height=720)
    c.save()
    print(
        f"{len(placed)} parole incluse, nessuna sovrapposizione. Scala: dimensione font = {factor} × radice(frequenza)."
    )
