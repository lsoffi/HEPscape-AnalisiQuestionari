"""Opening sample-size table for comparison PDFs."""

from collections import Counter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


def sample_counts(groups, events):
    """Count selected questionnaire rows by kit, city and source event."""
    counts = Counter()
    for rows, event in zip(groups, events, strict=True):
        counts.update((row[13], row[12], event) for row in rows)
    return [(*key, count) for key, count in counts.items()]


def draw_sample_summary(canvas, samples, pages):
    """Draw page 2; counts include questionnaires with individual blanks."""
    navy = colors.HexColor("#18304F")
    canvas.setFillColor(navy)
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawString(55, 680, "Questionari analizzati")
    canvas.setFont("Helvetica", 14)
    canvas.drawString(55, 645, "Numero di schede per configurazione kit e città")
    data = [["Kit", "Città", "Raccolta", "Questionari"],
            *[list(row) for row in samples],
            ["Totale", "", "", sum(row[3] for row in samples)]]
    table = Table(data, colWidths=[170, 220, 360, 148], rowHeights=42)
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 15),
        ("TEXTCOLOR", (0, 0), (-1, -1), navy),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#234A8C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F0F4FA")]),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#7BBA48")),
        ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    _, height = table.wrap(898, 500)
    table.drawOn(canvas, 55, 600 - height)
    canvas.setFont("Helvetica", 12)
    canvas.drawString(55, 570 - height, "La tabella conta le schede incluse nel confronto, anche se contengono risposte vuote.")
    canvas.drawString(55, 548 - height, "Nei grafici, il numero di risposte valide può variare da una domanda all'altra.")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(980, 12, f"2 / {pages}")
