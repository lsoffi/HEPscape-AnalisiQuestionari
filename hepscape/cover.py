"""PDF cover with the actual analysis scope, using the HEPscape palette."""

from xml.sax.saxutils import escape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph


def draw_cover(canvas, kit, location, event, count, pages):
    canvas.setFillColorRGB(0.094, 0.188, 0.310)
    canvas.rect(0, 0, 1008, 756, fill=1, stroke=0)
    canvas.setFillColorRGB(0.482, 0.729, 0.282)
    canvas.rect(64, 647, 110, 7, fill=1, stroke=0)
    canvas.setFillColorRGB(1, 1, 1)
    canvas.setFont("Helvetica-Bold", 46)
    canvas.drawString(64, 678, "HEPscape!")
    canvas.setFont("Helvetica", 21)
    canvas.drawString(64, 604, "Analisi dei questionari")
    y = 546
    for label, value in [
        ("KIT", kit),
        ("LOCATION DELL'EVENTO", location),
        ("RACCOLTA", event),
    ]:
        canvas.setFillColorRGB(0.482, 0.729, 0.282)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(64, y, label)
        size = 32 if label != "RACCOLTA" else 19
        while True:
            paragraph = Paragraph(
                escape(str(value)),
                ParagraphStyle(
                    "cover",
                    fontName="Helvetica-Bold",
                    fontSize=size,
                    leading=size * 1.2,
                    textColor="white",
                ),
            )
            width, height = paragraph.wrap(880, 100)
            if height <= 88 or size <= 9:
                break
            size -= 1
        paragraph.drawOn(canvas, 64, y - 18 - height)
        y -= max(118, height + 48)
    canvas.setFillColorRGB(1, 1, 1)
    canvas.setFont("Helvetica", 14)
    canvas.drawString(64, 88, f"{count} questionari nella selezione")
    canvas.setFont("Helvetica", 10)
    canvas.drawString(64, 61, "Risultati descrittivi relativi all'attività HEPscape!")
    canvas.drawRightString(945, 30, f"1 / {pages}")
