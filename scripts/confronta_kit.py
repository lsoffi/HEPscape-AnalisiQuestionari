"""Confronto descrittivo di tutte le domande chiuse fra due o tre kit."""

import argparse
import csv
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from hepscape.workbook import read_workbook
from hepscape.schema import OPTIONS
from hepscape.cover import draw_cover

TITLES = {
    "Q1": "Gradimento",
    "Q3": "Apprendimento dichiarato",
    "Q4": "Curiosità",
    "Q5": "Interesse per la ricerca",
    "Q6": "Facilità di partecipazione",
    "Q7": "Occasioni di partecipazione",
    "Q8": "Già stato/a nel luogo",
    "Q9": "Genere",
    "Q10": "Età",
    "Q11": "Residente nella città",
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("workbook")
    p.add_argument("--kits", nargs="+", default=["Roma", "Bari", "Pisa"])
    p.add_argument("--out", default="reports/confronto-roma-bari-pisa/ERN2026")
    p.add_argument("--event", default="Evento ERNEST - ERN 2026")
    args = p.parse_args()
    if len(args.kits) not in (2, 3) or len(set(k.casefold() for k in args.kits)) != len(
        args.kits
    ):
        p.error("Scegli due o tre kit distinti.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = read_workbook(args.workbook)
    groups = [
        [r for r in rows if r[13].casefold() == kit.casefold()] for kit in args.kits
    ]
    if not all(groups):
        raise ValueError("Ogni kit deve avere questionari.")
    from hepscape.comparison import kit_colors

    colors = kit_colors(args.kits)
    center = (len(groups) - 1) / 2
    step = 0.78 / len(groups)
    navy = "#18304F"
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "text.color": navy,
            "axes.labelcolor": navy,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    figures = []
    table = []
    questions = list(TITLES)
    for start in range(0, len(questions), 4):
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        for ax, q in zip(axes.flat, questions[start : start + 4]):
            idx = int(q[1:])
            labels = OPTIONS[q]
            y = np.arange(len(labels))
            for j, (kit, rs) in enumerate(zip(args.kits, groups)):
                vals = [r[idx] for r in rs if r[idx] != 999]
                n = len(vals)
                counts = [vals.count(k) for k in range(len(labels))]
                pct = [100 * c / n if n else 0 for c in counts]
                ax.barh(
                    y + (j - center) * step,
                    pct,
                    height=step * 0.9,
                    color=colors[j],
                    label=f"{kit}: n={n}, vuote={len(rs)-n}",
                )
                for k, (count, pc) in enumerate(zip(counts, pct)):
                    ax.text(
                        pc + 1,
                        y[k] + (j - center) * step,
                        f"{pc:.1f}%",
                        va="center",
                        fontsize=8,
                    )
                    table.append([q, kit, labels[k], count, n, len(rs) - n, pc])
            ax.set_yticks(y, labels)
            ax.invert_yaxis()
            ax.set_xlim(0, 115)
            ax.set_xticks([0, 25, 50, 75, 100])
            ax.set_xlabel("% delle risposte valide del kit")
            ax.set_title(q + " · " + TITLES[q], loc="left", fontweight="bold")
            ax.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.19),
                fontsize=8,
                frameon=False,
            )
        for ax in list(axes.flat)[len(questions[start : start + 4]) :]:
            ax.set_visible(False)
        fig.suptitle(
            "HEPscape! · " + " e ".join(args.kits),
            fontsize=24,
            fontweight="bold",
            x=0.04,
            ha="left",
        )
        fig.text(
            0.04,
            0.925,
            args.event
            + " | Confronto descrittivo: ogni kit è associato a una sola location in questi dati.",
            fontsize=12,
        )
        fig.text(
            0.04,
            0.02,
            "999 esclusi dai denominatori. Nessun confronto causale; gruppi con pubblico e numerosità diversi.",
            fontsize=10,
        )
        fig.subplots_adjust(
            left=0.17, right=0.96, top=0.85, bottom=0.13, hspace=0.85, wspace=0.6
        )
        name = f"confronto_{start//4+1:02d}"
        fig.savefig(out / (name + ".png"), dpi=160)
        fig.savefig(out / (name + ".svg"))
        plt.close(fig)
        figures.append(out / (name + ".png"))
    fig, ax = plt.subplots(figsize=(16, 10))
    y = np.arange(11)
    for j, (kit, rs) in enumerate(zip(args.kits, groups)):
        pct = [100 * sum(r[q] == 999 for r in rs) / len(rs) for q in range(1, 12)]
        ax.barh(
            y + (j - center) * step,
            pct,
            height=step * 0.9,
            color=colors[j],
            label=f"{kit}: {len(rs)} schede",
        )
        for k, v in enumerate(pct):
            ax.text(v + 1, y[k] + (j - center) * step, f"{v:.1f}%", va="center")
    ax.set_yticks(y, [f"Q{i}" for i in range(1, 12)])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.legend()
    ax.set_xlabel("% di risposte vuote su tutte le schede del kit")
    ax.set_title("HEPscape! · Risposte mancanti, inclusa Q2", fontsize=23, pad=25)
    fig.tight_layout(pad=3)
    fig.savefig(out / "mancanti.png", dpi=160)
    fig.savefig(out / "mancanti.svg")
    plt.close(fig)
    figures.append(out / "mancanti.png")
    with (out / "confronto_risposte.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        w = csv.writer(f)
        w.writerow(
            [
                "domanda",
                "kit",
                "risposta",
                "conteggio",
                "validi",
                "vuote",
                "percentuale_validi",
            ]
        )
        w.writerows(table)
    from hepscape.comparison import generate

    figures.extend(generate(groups, args.kits, out, args.event))
    pdf = out / "HEPscape_confronto_kit.pdf"
    c = canvas.Canvas(str(pdf), pagesize=(1008, 756))
    loc = "; ".join(
        kit + ": " + ", ".join(sorted({r[12] for r in rs}))
        for kit, rs in zip(args.kits, groups)
    )
    draw_cover(
        c,
        " vs ".join(args.kits),
        loc,
        args.event,
        sum(map(len, groups)),
        len(figures) + 1,
    )
    c.showPage()
    for i, path in enumerate(figures, 2):
        c.drawImage(
            str(path),
            0,
            25,
            width=1008,
            height=710,
            preserveAspectRatio=True,
            anchor="c",
        )
        c.setFont("Helvetica", 9)
        c.drawRightString(980, 12, f"{i} / {len(figures)+1}")
        c.showPage()
    c.save()
    print(pdf)


if __name__ == "__main__":
    main()
