"""Importa la tabella TSV QID del questionario ERNEST, preservando i testi."""

import argparse
import csv
import hashlib
from pathlib import Path
from hepscape.schema import OPTIONS, QUESTIONS, save

FIELDS = dict(zip(QUESTIONS, ["QID65", "QID59", "QID66", "QID67", "QID68", "QID69", "QID70", "QID71", "QID73", "QID74", "QID75"]))


def normalized(value):
    return " ".join(value.strip().replace("’", "'").replace("–", "-").split()).casefold()


def convert(source, kit, city, event, prefix):
    source = Path(source)
    with source.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    headers = rows[0]
    required = set(FIELDS.values()) | {"QID7", "QID76"}
    if not required.issubset(headers) or len(headers) != len(set(headers)):
        raise ValueError("Intestazioni QID mancanti o duplicate.")
    if len(rows) < 3 or not rows[1][headers.index("QID65")].startswith("1."):
        raise ValueError("Attese due righe di intestazione, poi le risposte.")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    records = []
    for n, row in enumerate(rows[2:], 1):
        if len(row) != len(headers):
            raise ValueError(f"Risposta {n}: numero di colonne non valido.")
        cells = dict(zip(headers, row))
        if normalized(cells["QID7"]) != "sì":
            raise ValueError(f"Risposta {n}: partecipazione non confermata.")
        if normalized(cells["QID76"]) != normalized(f"{city} - HEPscape!"):
            raise ValueError(f"Risposta {n}: location o attività non corrispondente.")
        answers, originals = {}, {}
        for q, field in FIELDS.items():
            raw = cells[field].strip()
            originals[q] = raw
            if not raw:
                answers[q] = None
            elif q == "Q2":
                answers[q] = raw.upper()
            else:
                lookup = {normalized(label): code for code, label in enumerate(OPTIONS[q])}
                if normalized(raw) not in lookup:
                    raise ValueError(f"Risposta {n}, {q}: opzione sconosciuta {raw!r}.")
                answers[q] = lookup[normalized(raw)]
        records.append({
            "id": f"{prefix}-{n:03d}", "city": city, "kit": kit,
            "source": f"{source.name}#risposta={n}", "answers": answers,
            "originals": originals, "reviewed": dict.fromkeys(QUESTIONS, True),
            "issues": {}, "notes": {},
            "provenance": {"method": "Conversione deterministica della tabella testuale fornita dall’utente; nessuna lettura OCR.",
                           "source_sha256": digest, "response_row": n,
                           "participation": cells["QID7"], "activity": cells["QID76"]},
        })
    return {"version": 1, "event": event, "records": records}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    for field in ["kit", "city", "event", "prefix", "out"]:
        p.add_argument(f"--{field}", required=True)
    args = p.parse_args()
    if Path(args.out).exists():
        p.error("Il file di output esiste già: scegliere un nuovo percorso.")
    data = convert(args.source, args.kit, args.city, args.event, args.prefix)
    save(data, args.out)
    print(f"Convertite {len(data['records'])} risposte.")
