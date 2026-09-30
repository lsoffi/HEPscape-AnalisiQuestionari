"""Additional descriptive comparisons. No causal or population-level claims."""

import csv
import math
import re
from collections import Counter
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from .schema import OPTIONS

COLORS = ["#234A8C", "#7BBA48", "#5F8FC4"]


def kit_colors(kits):
    mapping = {"roma": COLORS[0], "bari": COLORS[1], "pisa": COLORS[2]}
    return [mapping.get(k.casefold(), COLORS[i]) for i, k in enumerate(kits)]


OUTCOMES = [
    (1, "Gradimento: tantissimo"),
    (3, "Apprendimento: sì, molto"),
    (4, "Più curiosità"),
    (5, "Più interesse"),
]
STOP = set(
    "E È DI A DA IN CON PER CHE IL LO LA I GLI LE UN UNA UNO MOLTO STATA STATO ESPERIENZA ALLA HO MA NN NON PO TROPPO".split()
)


def tokens(text):
    return {
        t
        for t in re.findall(r"[A-ZÀÈÉÌÒÙ]+", re.sub(r"\[[^]]*\]", "", text.upper()))
        if t not in STOP and len(t) > 1
    }


def wilson(x, n):
    if n == 0:
        return None
    z = 1.959963984540054
    p = x / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, center - half), min(1.0, center + half)


def difference_interval(xa, na, xb, nb):
    """Newcombe independent-proportions interval from Wilson bounds, A minus B."""
    if not na or not nb:
        return None
    a, b = xa / na, xb / nb
    la, ua = wilson(xa, na)
    lb, ub = wilson(xb, nb)
    d = a - b
    return (
        d,
        max(-1.0, d - math.sqrt((a - la) ** 2 + (ub - b) ** 2)),
        min(1.0, d + math.sqrt((ua - a) ** 2 + (b - lb) ** 2)),
    )


def generate(groups, kits, output, event):
    out = Path(output)
    colors = kit_colors(kits)
    center = (len(groups) - 1) / 2
    step = 0.78 / len(groups)
    figures = []
    records = []

    def save(
        fig,
        slug,
        title,
        subtitle,
        foot="999 esclusi; * = meno di 10 risposte valide. Analisi descrittiva, non causale.",
    ):
        fig.suptitle(
            "HEPscape! · " + title,
            fontsize=22,
            fontweight="bold",
            x=0.045,
            ha="left",
            y=0.98,
        )
        fig.text(0.045, 0.93, subtitle, fontsize=11)
        fig.text(0.045, 0.035, foot, fontsize=10)
        fig.text(0.045, 0.014, event + " | " + " vs ".join(kits), fontsize=9)
        fig.savefig(out / (slug + ".png"), dpi=160)
        fig.savefig(out / (slug + ".svg"))
        plt.close(fig)
        figures.append(out / (slug + ".png"))

    def table(kind, q, group, kit, cat, x, n):
        records.append([kind, q, group, kit, cat, x, n, 100 * x / n if n else ""])

    def stratified(g, slug, title, subtitle):
        labels = OPTIONS[f"Q{g}"]
        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        for ax, (q, titleq) in zip(axs.flat, OUTCOMES):
            for j, (kit, rs) in enumerate(zip(kits, groups)):
                for k, label in enumerate(labels):
                    subset = [r for r in rs if r[g] == k and r[q] != 999]
                    n = len(subset)
                    x = sum(r[q] == 0 for r in subset)
                    y = k + (j - center) * step
                    if n:
                        pc = 100 * x / n
                        ax.barh(y, pc, height=step * 0.9, color=colors[j])
                        ax.text(
                            pc + 1,
                            y,
                            f"{pc:.0f}% · n={n}" + (" *" if n < 10 else ""),
                            fontsize=8,
                            va="center",
                        )
                    else:
                        ax.text(
                            1,
                            y,
                            "n=0 · non stimabile",
                            fontsize=8,
                            va="center",
                            color=colors[j],
                        )
                    table(slug, f"Q{q}", label, kit, "codice 0", x, n)
            ax.set_yticks(range(len(labels)), labels, fontsize=9)
            ax.invert_yaxis()
            ax.set_xlim(0, 140)
            ax.set_xticks([0, 25, 50, 75, 100])
            ax.set_xlabel("% della risposta indicata, nel sottogruppo")
            ax.set_title(titleq, loc="left", fontsize=12)
        handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors]
        fig.legend(
            handles,
            kits,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.062),
            ncol=len(kits),
            frameon=False,
        )
        fig.subplots_adjust(
            left=0.16, right=0.97, top=0.85, bottom=0.18, hspace=0.5, wspace=0.48
        )
        save(fig, slug, title, subtitle)

    stratified(
        10,
        "05_eta",
        "Confronto nelle stesse fasce di età",
        "Fasce originali Q10; esclusi i mancanti in età o esito. Nessuna standardizzazione complessiva.",
    )
    # Presence per questionnaire, exact forms, same tokenization as existing report.
    texts = [[r[2] for r in rs if r[2] != 999] for rs in groups]
    counters = [Counter(t for s in ts for t in tokens(s)) for ts in texts]
    vocab = set().union(*counters)
    total = lambda w: sum(c[w] for c in counters)
    words = sorted(vocab, key=lambda w: (-total(w), w))[:20]
    fig, ax = plt.subplots(figsize=(16, 12))
    for j, (kit, ts, c) in enumerate(zip(kits, texts, counters)):
        for i, w in enumerate(words):
            pct = 100 * c[w] / len(ts) if ts else 0
            ax.barh(i + (j - center) * step, pct, height=step * 0.9, color=colors[j])
            ax.text(
                pct + 0.4,
                i + (j - center) * step,
                f"{pct:.1f}% ({c[w]})",
                va="center",
                fontsize=8,
            )
        for w in sorted(vocab):
            table("parole", "Q2", "forme esatte", kit, w, c[w], len(ts))
    ax.set_yticks(range(len(words)), words)
    ax.invert_yaxis()
    ax.set_xlim(
        0,
        max(
            [
                100 * c[w] / len(ts)
                for c, ts in zip(counters, texts)
                if ts
                for w in words
            ]
            or [1]
        )
        * 1.3,
    )
    ax.set_xlabel("% delle risposte Q2 non vuote del kit")
    fig.subplots_adjust(left=0.24, right=0.95, top=0.85, bottom=0.13)
    fig.legend(
        [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors],
        [f"{kit}: Q2 valide={len(ts)}" for kit, ts in zip(kits, texts)],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.065),
        ncol=len(kits),
        frameon=False,
    )
    save(
        fig,
        "06_parole",
        "Le 20 parole più frequenti",
        "Selezione per numero totale di schede; ogni parola conta una volta per scheda. Tra parentesi: conteggi.",
        "Forme esatte; stopword escluse come nei report esistenti. Q2 vuote escluse, refusi non corretti.",
    )
    if all(texts):
        frequencies = lambda w: [100 * c[w] / len(ts) for c, ts in zip(counters, texts)]
        spread = lambda w: max(frequencies(w)) - min(frequencies(w))
        chosen = sorted(
            [w for w in vocab if total(w) >= 3], key=lambda w: (-spread(w), w)
        )[:16]
        fig, ax = plt.subplots(figsize=(16, 12))
        for i, w in enumerate(chosen):
            vals = frequencies(w)
            ax.plot([min(vals), max(vals)], [i, i], color="#BECBD5", lw=2)
            for j, v in enumerate(vals):
                ax.scatter(
                    v,
                    i + (j - center) * 0.18,
                    color=colors[j],
                    s=45,
                    label=kits[j] if i == 0 else None,
                )
        ax.set_yticks(range(len(chosen)), chosen)
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.set_xlabel("% delle risposte Q2 non vuote del kit")
        ax.legend(frameon=False)
        fig.subplots_adjust(left=0.24, right=0.95, top=0.84, bottom=0.16)
        save(
            fig,
            "07_parole_differenze",
            "Parole con maggiore differenza osservata",
            "16 maggiori scarti massimo-minimo tra kit; almeno 3 schede totali. Q2 valide: "
            + ", ".join(f"{k}={len(t)}" for k, t in zip(kits, texts))
            + ".",
            "Selezione esplorativa, non test di significatività né misura di sentiment. Forme esatte separate.",
        )
    fig, ax = plt.subplots(figsize=(16, 10))
    names = [
        "Più curiosità e più interesse",
        "Solo più curiosità",
        "Solo più interesse",
        "Nessuno dei due aumenti",
    ]
    for j, (kit, rs) in enumerate(zip(kits, groups)):
        valid = [r for r in rs if r[4] != 999 and r[5] != 999]
        n = len(valid)
        cnt = Counter((r[4] == 0, r[5] == 0) for r in valid)
        for i, key in enumerate(
            [(True, True), (True, False), (False, True), (False, False)]
        ):
            x = cnt[key]
            pc = 100 * x / n if n else 0
            y = i + (j - center) * step
            ax.barh(
                y,
                pc,
                height=step * 0.9,
                color=colors[j],
                label=f"{kit}: n={n}" if i == 0 else None,
            )
            ax.text(pc + 1, y, f"{pc:.1f}% ({x})", va="center")
            table("aumenti", "Q4+Q5", "coppie valide", kit, names[i], x, n)
    ax.set_yticks(range(4), names)
    ax.invert_yaxis()
    ax.set_xlim(0, 115)
    ax.set_xlabel("% delle schede con Q4 e Q5 valide")
    ax.legend(frameon=False)
    fig.subplots_adjust(left=0.29, right=0.95, top=0.84, bottom=0.15)
    save(
        fig,
        "08_aumenti",
        "Curiosità e interesse insieme",
        "Aumenti dichiarati dopo l’attività; “nessuno” comprende risposte uguali o inferiori a prima.",
    )
    fig, axs = plt.subplots(1, len(kits), figsize=(18, 10))
    for ax, kit, rs in zip(axs, kits, groups):
        matrix = np.zeros((3, 3), dtype=int)
        for r in rs:
            if r[6] != 999 and r[1] != 999:
                matrix[r[6], r[1]] += 1
        ns = matrix.sum(axis=1)
        pct = (
            np.divide(matrix, ns[:, None], out=np.zeros((3, 3)), where=ns[:, None] > 0)
            * 100
        )
        masked = np.ma.array(pct, mask=np.repeat((ns == 0)[:, None], 3, axis=1))
        ax.imshow(
            masked,
            cmap=LinearSegmentedColormap.from_list(
                "hepscape", ["#F4F7FC", "#5F8FC4", "#234A8C"]
            ),
            vmin=0,
            vmax=100,
            aspect="auto",
        )
        for i in range(3):
            for k in range(3):
                ax.text(
                    k,
                    i,
                    f"{pct[i,k]:.1f}%\n({matrix[i,k]}/{ns[i]})" if ns[i] else "n=0",
                    ha="center",
                    va="center",
                    color="white" if pct[i, k] > 55 else "#18304F",
                )
                table(
                    "facilita_gradimento",
                    "Q1",
                    OPTIONS["Q6"][i],
                    kit,
                    OPTIONS["Q1"][k],
                    int(matrix[i, k]),
                    int(ns[i]),
                )
        ax.set_xticks(range(3), ["Tantissimo", "Piaciuta", "Non molto"])
        ax.set_yticks(
            range(3),
            [
                f"{v} · n={n}" + (" *" if n < 10 else "")
                for v, n in zip(OPTIONS["Q6"], ns)
            ],
        )
        ax.set_xlabel("Q1 · Gradimento")
        ax.set_ylabel("Q6 · Facilità di partecipazione")
        ax.set_title(kit)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.82, bottom=0.18, wspace=0.65)
    save(
        fig,
        "09_facilita_gradimento",
        "Facilità e gradimento",
        "Percentuali entro ciascuna risposta Q6, stessa scala 0-100% in tutti i pannelli. Celle: percentuale e conteggio/n.",
        "Q6 riguarda la facilità di partecipazione, non la difficoltà degli enigmi. * n<10; coppie mancanti escluse.",
    )
    stratified(
        7,
        "10_occasioni",
        "Confronto per occasioni di partecipazione",
        "Q7 misura quanto spesso si ha la possibilità di partecipare: non il numero di esperienze già fatte.",
    )
    stratified(
        8,
        "11_familiarita",
        "Confronto per familiarità con il luogo",
        "Q8: già stato/a in questo luogo per un’attività didattica. Non equivale ad aver già fatto HEPscape.",
    )
    from .comparison_wordwall import generate as generate_wordwall

    figures.append(generate_wordwall(texts, kits, out, event))
    with (out / "approfondimenti.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "analisi",
                "domanda",
                "sottogruppo",
                "kit",
                "risposta",
                "conteggio",
                "validi",
                "percentuale",
            ]
        )
        w.writerows(records)
    return figures
