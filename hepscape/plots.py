import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import json, re, csv, zipfile, textwrap
from pathlib import Path
from collections import Counter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageOps, ImageDraw


def generate(
    workbook,
    output,
    event="Raccolta HEPscape",
    *,
    kit=None,
    city=None,
    compare_kits=False,
):
    base = Path(output)
    out = base / "grafici"
    from .workbook import read_workbook

    from .routing import select_rows

    rows = select_rows(read_workbook(workbook), kit, city)
    out.mkdir(parents=True, exist_ok=True)
    N = len(rows)
    labels = {
        1: ["Tantissimo", "Piaciuta", "Non molto"],
        3: ["Sì, molto", "Sì, un po’", "No, per niente"],
        4: ["Più curioso/a", "Come prima", "Meno curioso/a"],
        5: ["Più interessato/a", "Come prima", "Meno interessato/a"],
        6: ["Sì, molto", "In parte", "No"],
        7: ["Spesso", "A volte", "Mai"],
        8: ["No", "Sì"],
        9: ["Femminile", "Maschile", "Altro", "Non risponde"],
        10: [
            "Meno di 11",
            "11-14",
            "15-18",
            "19-25",
            "26-40",
            "41-60",
            "Più di 60",
            "Non risponde",
        ],
        11: ["No", "Sì"],
    }
    titles = {
        1: "Gradimento",
        3: "Apprendimento dichiarato",
        4: "Curiosità per la scienza",
        5: "Interesse per la ricerca",
        6: "Facilità di partecipazione",
        7: "Occasioni di escape room scientifiche",
        8: "Già stato qui per attività didattiche",
        9: "Genere",
        10: "Età",
        11: "Residente nella stessa città",
    }
    colors = ["#335BA6", "#7BBA48", "#18304F"]
    navy = "#18304F"
    neutral = ["#234A8C", "#5F8FC4", "#7BBA48", "#B6B3C4"]
    from matplotlib.colors import LinearSegmentedColormap

    hep_cmap = LinearSegmentedColormap.from_list(
        "HEPscape", ["#F4F7FC", "#5F8FC4", "#234A8C"]
    )
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "bold",
            "axes.labelcolor": navy,
            "text.color": navy,
            "axes.edgecolor": "#BECBD5",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "svg.fonttype": "none",
        }
    )
    figs = []
    tables = []

    def valid(q, subset=None):
        return [r[q] for r in (rows if subset is None else subset) if r[q] != 999]

    def save(
        fig,
        name,
        title,
        subtitle,
        foot="Percentuali sulle risposte valide; 999 escluso. Analisi descrittiva, non causale.",
    ):
        fig.suptitle(title, x=0.06, ha="left", fontsize=20, fontweight="bold", y=0.975)
        fig.text(0.06, 0.915, subtitle, fontsize=11, color="#56697B")
        fig.text(
            0.06,
            0.046,
            f"HEPscape! | {event} | {N} questionari",
            fontsize=9,
            color=navy,
            fontweight="bold",
        )
        fig.text(0.06, 0.021, foot, fontsize=8.5, color="#56697B")
        fig.subplots_adjust(
            top=0.84,
            bottom=0.13,
            left=0.30 if name == "11_aumenti" else 0.12,
            right=0.96,
            hspace=0.65,
            wspace=0.38,
        )
        fig.savefig(out / (name + ".png"), dpi=160)
        fig.savefig(out / (name + ".svg"))
        plt.close(fig)
        figs.append((name, title, subtitle, foot))

    def bars(ax, q, palette=None):
        v = valid(q)
        counts = [v.count(i) for i in range(len(labels[q]))]
        ax.barh(
            range(len(counts)),
            counts,
            color=(palette or colors)[: len(counts)] if len(counts) <= 4 else "#335BA6",
        )
        ax.set_yticks(range(len(counts)), labels[q])
        ax.invert_yaxis()
        ax.set_xlim(0, max(counts) * 1.35 + 2)
        for i, n in enumerate(counts):
            ax.text(
                n + 0.6,
                i,
                f"{n}  ({(n/len(v) if v else 0):.1%})",
                va="center",
                fontsize=10,
            )
        ax.set_title(
            f"Q{q} · {titles[q]}\nn={len(v)}; mancanti={N-len(v)}",
            loc="left",
            fontsize=11,
            pad=12,
        )
        ax.set_xlabel("Numero di risposte")
        ax.xaxis.grid(True, alpha=0.13)
        ax.set_axisbelow(True)
        for i, n in enumerate(counts):
            tables.append([f"Q{q}", labels[q][i], n, len(v), (n / len(v) if v else 0)])

    f, axs = plt.subplots(2, 3, figsize=(16, 10))
    for ax, q in zip(axs.flat, [1, 3, 4, 5, 6, 7]):
        bars(ax, q)
    save(
        f,
        "01_risposte",
        "Le risposte all’esperienza",
        "Gradimento, apprendimento e cambiamenti dichiarati, insieme a facilità e occasioni di partecipazione.",
    )
    f, axs = plt.subplots(1, 2, figsize=(15, 8))
    bars(axs[0], 10)
    bars(axs[1], 9, neutral)
    save(
        f,
        "02_partecipanti",
        "Chi ha partecipato",
        "Le fasce d’età sono categorie: non vengono trattate come età esatte.",
    )
    f, axs = plt.subplots(1, 3, figsize=(16, 7))
    for ax, q in zip(axs, [7, 8, 11]):
        bars(ax, q, neutral)
    save(
        f,
        "03_accesso",
        "Occasioni, familiarità e provenienza",
        f"Città: {len(set(r[12] for r in rows))}; kit: {len(set(r[13] for r in rows))}. Metadati letti dal workbook.",
    )
    f, ax = plt.subplots(figsize=(14, 7))
    miss = [sum(r[q] == 999 for r in rows) for q in range(1, 12)]
    ax.bar(range(1, 12), miss, color="#7BBA48")
    ax.set_xticks(range(1, 12), [f"Q{i}" for i in range(1, 12)])
    ax.set_ylim(0, max(miss) + 4)
    ax.set_ylabel("Risposte mancanti")
    for q, n in enumerate(miss, 1):
        ax.text(q, n + 0.3, f"{n}\n{n/N:.1%}", ha="center", fontsize=10)
    save(
        f,
        "04_mancanti",
        "Dove mancano le risposte",
        "Q2 è la domanda aperta. I mancanti sono esclusi dai denominatori delle altre tavole.",
        f"999 indica un dato mancante; percentuali sul totale di {N} schede.",
    )

    def grouped(ax, q, g):
        cats = [i for i in range(len(labels[g])) if any(r[g] == i for r in rows)]
        arr = []
        ns = []
        for c in cats:
            v = valid(q, [r for r in rows if r[g] == c])
            ns.append(len(v))
            arr.append(
                [v.count(i) / len(v) * 100 if v else 0 for i in range(len(labels[q]))]
            )
        arr = np.array(arr).reshape((-1, len(labels[q])))
        left = np.zeros(len(cats))
        for k in range(arr.shape[1]):
            ax.barh(
                range(len(cats)),
                arr[:, k],
                left=left,
                color=colors[k],
                label=labels[q][k],
                height=0.65,
            )
            for y, p in enumerate(arr[:, k]):
                if p >= 13:
                    ax.text(
                        left[y] + p / 2,
                        y,
                        f"{p:.0f}%",
                        ha="center",
                        va="center",
                        fontsize=9,
                        color="white" if k != 1 else navy,
                    )
            left += arr[:, k]
        ax.set_yticks(
            range(len(cats)),
            [
                f"{labels[g][c]} · n={n}" + (" *" if n < 10 else "")
                for c, n in zip(cats, ns)
            ],
        )
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.set_xlabel("% risposte valide nel gruppo")
        ax.set_title(f"Q{q} · {titles[q]}", loc="left", fontsize=12)
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.19),
            ncol=3,
            fontsize=8,
            frameon=False,
        )

    for g, slug, title in [
        (10, "05_eta", "Risposte per fascia d’età"),
        (9, "06_genere", "Risposte per genere"),
        (7, "07_frequenza", "Risposte e occasioni di partecipazione"),
    ]:
        f, axs = plt.subplots(2, 2, figsize=(16, 12))
        for ax, q in zip(axs.flat, [1, 3, 4, 5]):
            grouped(ax, q, g)
        save(
            f,
            slug,
            title,
            "Ogni barra totalizza il 100%. n varia per domanda; * segnala un gruppo con meno di 10 risposte valide.",
            "Esclusi i 999 in entrambe le variabili. Differenze descrittive; gruppi piccoli instabili.",
        )
    f, axs = plt.subplots(2, 2, figsize=(16, 10))
    for ax, q, g in zip(axs.flat, [1, 4, 1, 4], [8, 8, 11, 11]):
        grouped(ax, q, g)
        ax.set_title(
            f"Q{q} · {titles[q]}\nGruppi: {titles[g]}", loc="left", fontsize=11
        )
    save(
        f,
        "08_familiarita",
        "Familiarità con il luogo e residenza",
        "In alto: precedenti attività didattiche nello stesso luogo. In basso: residenza nella città dell’evento.",
    )

    f, axs = plt.subplots(2, 2, figsize=(16, 12))
    for ax, (a, b) in zip(axs.flat, [(3, 4), (3, 5), (4, 5), (6, 1)]):
        m = np.zeros((len(labels[a]), len(labels[b])), int)
        for r in rows:
            if r[a] != 999 and r[b] != 999:
                m[r[a], r[b]] += 1
        n = m.sum()
        p = (
            np.divide(
                m,
                m.sum(axis=1, keepdims=True),
                out=np.zeros_like(m, dtype=float),
                where=m.sum(axis=1, keepdims=True) != 0,
            )
            * 100
        )
        ax.imshow(p, cmap=hep_cmap, vmin=0, vmax=100, aspect="auto")
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                ax.text(
                    j,
                    i,
                    f"{m[i,j]}\n{p[i,j]:.0f}%",
                    ha="center",
                    va="center",
                    color="white" if p[i, j] > 45 else navy,
                )
        ax.set_xticks(range(len(labels[b])), labels[b], fontsize=9)
        ax.set_yticks(
            range(len(labels[a])),
            [f"{x}\nn={m[i].sum()}" for i, x in enumerate(labels[a])],
            fontsize=9,
        )
        ax.set_xlabel(titles[b])
        ax.set_ylabel(titles[a])
        ax.set_title(f"Q{a} × Q{b} · coppie valide: {n}", loc="left")
    save(
        f,
        "09_relazioni",
        "Come si combinano le risposte",
        "Ogni cella mostra il conteggio e la percentuale sulla propria riga. Colore: 0-100% sulla riga.",
    )
    f, axs = plt.subplots(1, 2, figsize=(16, 9))
    grouped(axs[0], 6, 10)
    grouped(axs[1], 6, 7)
    save(
        f,
        "10_facilita",
        "Per chi è stato facile partecipare?",
        "Facilità per età e per frequenza delle occasioni; * = meno di 10 risposte valide.",
        "Esclusi 999 in entrambe le variabili. Q6 riguarda la partecipazione, non la difficoltà degli enigmi.",
    )
    joint = Counter()
    for r in rows:
        if r[4] != 999 and r[5] != 999:
            joint[(r[4] == 0, r[5] == 0)] += 1
    names = [
        "Più curiosità e più interesse",
        "Solo più curiosità",
        "Solo più interesse",
        "Nessuno dei due aumenti",
    ]
    keys = [(1, 1), (1, 0), (0, 1), (0, 0)]
    ns = [joint[k] for k in keys]
    total = sum(ns)
    f, ax = plt.subplots(figsize=(14, 7))
    ax.barh(names, ns, color=[colors[0], "#5F8FC4", "#7BBA48", "#B6B3C4"])
    ax.invert_yaxis()
    ax.set_xlim(0, max(1, max(ns)) * 1.3)
    ax.set_xlabel("Numero di partecipanti")
    for i, n in enumerate(ns):
        ax.text(n + 0.7, i, f"{n} ({(n/total if total else 0):.1%})", va="center")
    save(
        f,
        "11_aumenti",
        "Curiosità e interesse: aumenti dichiarati insieme",
        f"{total} schede con Q4 e Q5 valide. “Nessuno” comprende risposte uguali o inferiori a prima.",
        "Dichiarazioni dopo l’attività; non sono misure prima/dopo né stime di effetti causali.",
    )

    texts = [r[2] for r in rows if r[2] != 999]
    stop = set(
        "E È DI A DA IN CON PER CHE IL LO LA I GLI LE UN UNA UNO MOLTO STATA STATO ESPERIENZA ALLA HO MA NN NON PO TROPPO".split()
    )
    tokens = [
        set(
            t
            for t in re.findall(r"[A-ZÀÈÉÌÒÙ]+", re.sub(r"\[[^]]*\]", "", s.upper()))
            if t not in stop and len(t) > 1
        )
        for s in texts
    ]
    mapping = {
        "BELLA": "BELLO/BELLA",
        "BELLO": "BELLO/BELLA",
        "ISTRUTTIVA": "ISTRUTTIVO/A",
        "ISTRUTTIVO": "ISTRUTTIVO/A",
        "EDUCATIVA": "EDUCATIVO/A",
        "EDUCATTIVA": "EDUCATIVO/A",
        "EDUCATIVO": "EDUCATIVO/A",
        "FORMATIVA": "FORMATIVO/A",
        "FORMATIVO": "FORMATIVO/A",
        "SIMPATICO": "SIMPATICO/A",
        "SIMPATICA": "SIMPATICO/A",
        "GIOCOSA": "GIOCOSO/A",
        "GIOCOSO": "GIOCOSO/A",
        "UNICA": "UNICO/A",
        "UNICO": "UNICO/A",
        "INTERATTIVA": "INTERATTIVO/A",
        "INTERATTIVO": "INTERATTIVO/A",
    }
    norm = [set(mapping.get(t, t) for t in ts) for ts in tokens]

    def wordsplot(ts, name, title):
        # Deterministic alphabetical tie-break, independent of Python's hash seed.
        counts = Counter(t for s in ts for t in sorted(s))
        counts = Counter(
            dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
        )
        top = counts.most_common(18)
        f, ax = plt.subplots(figsize=(14, 10))
        ax.barh([t for t, n in top], [n for t, n in top], color="#335BA6")
        ax.invert_yaxis()
        ax.set_xlim(0, max([1] + [n for t, n in top]) * 1.3)
        ax.set_xlabel("Schede che contengono la parola (una volta per scheda)")
        for i, (t, n) in enumerate(top):
            ax.text(n + 0.35, i, f"{n} ({n/len(texts):.1%})", va="center")
        save(
            f,
            name,
            title,
            f"{len(texts)} risposte testuali su {N}. Escluse parole funzionali e annotazioni tra parentesi quadre.",
            "Presenza per scheda, non numero totale di occorrenze; le percentuali non sommano a 100%.",
        )
        return counts

    exact = wordsplot(tokens, "12_parole_esatte", "Le parole di Q2: forme esatte")
    normal = wordsplot(norm, "13_parole_accorpate", "Le parole di Q2: forme accorpate")
    top = [t for t, n in normal.most_common(10)]
    m = np.array([[sum(a in s and b in s for s in norm) for b in top] for a in top])
    f, ax = plt.subplots(figsize=(14, 11))
    ax.imshow(m if len(top) else np.zeros((1, 1)), cmap=hep_cmap)
    ax.set_xticks(range(len(top)), top, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(top)), top, fontsize=9)
    if not top:
        ax.text(0, 0, "Nessuna risposta testuale", ha="center", va="center")
    for i in range(len(top)):
        for j in range(len(top)):
            ax.text(
                j,
                i,
                str(m[i, j]),
                ha="center",
                va="center",
                color="white" if m[i, j] > m.max() * 0.55 else navy,
                fontsize=10,
            )
    save(
        f,
        "14_parole_insieme",
        "Quali parole compaiono insieme?",
        f"Fino a 10 forme accorpate. Celle = schede che contengono entrambe le parole; diagonale = frequenza della parola.",
        "Co-presenza nella stessa risposta; non implica una relazione semantica o causale.",
    )

    # Add comparisons only when more than one city/kit is actually present.
    for g, slug, name in [(12, "15_citta", "città"), (13, "16_kit", "origine del kit")]:
        if g == 13 and not compare_kits:
            continue
        categories = sorted(set(r[g] for r in rows))
        if len(categories) < 2:
            continue
        for page, start in enumerate(range(0, len(categories), 8), 1):
            groups = categories[start : start + 8]
            f, axs = plt.subplots(2, 2, figsize=(16, 12))
            for ax, q in zip(axs.flat, [1, 3, 4, 5]):
                counts = [valid(q, [r for r in rows if r[g] == cat]) for cat in groups]
                ns_group = [len(v) for v in counts]
                left = np.zeros(len(groups))
                for k, label in enumerate(labels[q]):
                    pct = np.array(
                        [v.count(k) / len(v) * 100 if v else 0 for v in counts]
                    )
                    ax.barh(
                        range(len(groups)), pct, left=left, color=colors[k], label=label
                    )
                    for y, pct_value in enumerate(pct):
                        if pct_value >= 13:
                            ax.text(
                                left[y] + pct_value / 2,
                                y,
                                f"{pct_value:.0f}%",
                                ha="center",
                                va="center",
                                color="white" if k != 1 else navy,
                                fontsize=9,
                            )
                    left += pct
                ax.set_yticks(
                    range(len(groups)),
                    [
                        f"{cat} · n={n}" + (" *" if n < 10 else "")
                        for cat, n in zip(groups, ns_group)
                    ],
                    fontsize=9,
                )
                ax.invert_yaxis()
                ax.set_xlim(0, 100)
                ax.set_xlabel("% risposte valide nel gruppo")
                ax.set_title(f"Q{q} · {titles[q]}", loc="left")
                ax.legend(
                    loc="upper center",
                    bbox_to_anchor=(0.5, -0.19),
                    ncol=3,
                    fontsize=8,
                    frameon=False,
                )
            save(
                f,
                f"{slug}_{page}",
                f"Risposte per {name}",
                f"Gruppi {start+1}-{min(start+8,len(categories))} di {len(categories)}. * = meno di 10 risposte valide.",
                "Confronti descrittivi: le differenze possono dipendere dalla composizione dei partecipanti.",
            )

    with (out / "frequenze_risposte.csv").open("w") as h:
        w = csv.writer(h)
        w.writerow(["domanda", "risposta", "conteggio", "validi", "quota_validi"])
        w.writerows(dict.fromkeys(tuple(r) for r in tables))
    with (out / "frequenze_parole.csv").open("w") as h:
        w = csv.writer(h)
        w.writerow(["tipo", "parola", "schede", "risposte_Q2_valide"])
        w.writerows(
            (typ, t, n, len(texts))
            for typ, c in [("esatta", exact), ("accorpata", normal)]
            for t, n in c.most_common()
        )
    method = f"""HEPscape! - Analisi descrittiva di {N} questionari | {event}\nIl campione riguarda esclusivamente HEPscape!, non tutte le attività dell’evento ERNEST.\nPalette dal sito https://web.infn.it/hepscape/: blu #234A8C / #335BA6, azzurro #5F8FC4, verde #7BBA48.\nFonte: {Path(workbook).name}, foglio Dati codificati.\nUna riga per scheda. Città e origine kit sono lette dalle rispettive colonne del workbook.\nI codici sono categorie, non punteggi su cui calcolare medie. 999 escluso dai denominatori validi.\nNei confronti si escludono le schede mancanti in una delle due variabili. n è indicato per gruppo.\nNon sono stati effettuati test di significatività, selezioni di risultati in base a p-value o inferenze causali.\nGruppi piccoli (<10 risposte) contrassegnati da asterisco; risultati esplorativi non generalizzabili automaticamente.\nQ4 e Q5 misurano cambiamenti dichiarati: non esistono misure pre-attività.\nQ2: conteggio di presenza per scheda; BELLA BELLA conta una volta. Rimosse annotazioni editoriali tra parentesi quadre e stopword.\nLe forme esatte non correggono refusi. Nelle forme accorpate si uniscono solo le voci della mappa sotto; EDUCATTIVA è ricondotta a EDUCATIVO/A.\nI dati originali non sono stati modificati. Nessuna classificazione automatica di sentiment.\n"""
    (out / "metodo.txt").write_text(
        method
        + "\nStopword: "
        + ", ".join(sorted(stop))
        + "\n\nAccorpamenti:\n"
        + json.dumps(mapping, ensure_ascii=False, indent=2)
    )
    import shutil
    from .wordwall import generate_wordwall

    generate_wordwall(base, event, len(texts))
    for ext in ["png", "svg"]:
        shutil.copyfile(
            base / ("HEPscape_Q2_word_wall." + ext), out / ("12b_word_wall." + ext)
        )
    figs.insert(12, ("12b_word_wall", "Q2 - Word wall", "", ""))
    pdf = base / "HEPscape_raccolta_grafici.pdf"
    c = canvas.Canvas(str(pdf), pagesize=(1008, 756))
    from .cover import draw_cover

    kit_label = kit or "Tutti i kit"
    location_label = city or "Tutte le location"
    draw_cover(c, kit_label, location_label, event, N, len(figs) + 2)
    c.showPage()
    for i, (name, title, subtitle, foot) in enumerate(figs, 2):
        im = Image.open(out / (name + ".png"))
        w, h = im.size
        scale = min(984 / w, 708 / h)
        c.drawImage(
            ImageReader(im),
            (1008 - w * scale) / 2,
            (756 - h * scale) / 2,
            width=w * scale,
            height=h * scale,
        )
        c.setFont("Helvetica", 8)
        c.drawRightString(985, 12, f"{i} / {len(figs)+2}")
        c.showPage()
    c.setFont("Helvetica-Bold", 18)
    c.drawString(48, 704, "Metodo e lettura dei grafici")
    c.setFont("Helvetica", 11)
    y = 675
    for paragraph in (
        method
        + "\nAccorpamenti Q2: "
        + ", ".join(k + " -> " + v for k, v in mapping.items())
    ).splitlines():
        for line in textwrap.wrap(paragraph, width=135):
            c.drawString(48, y, line.replace("’", "'"))
            y -= 17
        y -= 8
    c.setFont("Helvetica", 8)
    c.drawRightString(985, 12, f"{len(figs)+2} / {len(figs)+2}")
    c.save()
    thumbs = []
    for name, *_ in figs:
        im = Image.open(out / (name + ".png")).convert("RGB")
        im.thumbnail((600, 450))
        tile = Image.new("RGB", (620, 480), "white")
        tile.paste(im, ((620 - im.width) // 2, 15))
        ImageDraw.Draw(tile).text((10, 460), name, fill="black")
        thumbs.append(tile)
    sheet = Image.new("RGB", (620 * 3, 480 * ((len(thumbs) + 2) // 3)), "#E7EAF0")
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % 3) * 620, (i // 3) * 480))
    sheet.save(out / "controllo.png")
    with zipfile.ZipFile(
        base / "HEPscape_grafici_e_tabelle.zip", "w", zipfile.ZIP_DEFLATED
    ) as z:
        generated = [
            out / (name + ext) for name, *_ in figs for ext in (".png", ".svg")
        ]
        generated += [
            out / n
            for n in ("frequenze_risposte.csv", "frequenze_parole.csv", "metodo.txt")
        ]
        for p in generated:
            z.write(p, p.name)
    (base / "manifest.json").write_text(
        json.dumps(
            {
                "event": event,
                "selection": {"kit": kit, "city": city},
                "compare_kits": compare_kits,
                "cover": {"kit": kit_label, "location": location_label},
                "questionnaires": N,
                "figures": [name for name, *_ in figs],
                "files": [str(p.relative_to(base)) for p in generated],
                "workbook": Path(workbook).name,
                "missing": miss,
                "valid_Q2": len(texts),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "grafici": len(figs),
                "pdf": str(pdf),
                "Q2_validi": len(texts),
                "mancanti": miss,
                "aumenti_congiunti": ns,
                "n_congiunti": total,
                "parole": normal.most_common(5),
            },
            ensure_ascii=False,
        )
    )
