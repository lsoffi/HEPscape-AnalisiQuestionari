"""Import a chat transcription locally; every answer still needs human review."""

import csv
from pathlib import Path
from .schema import QUESTIONS, OPTIONS, validate, save
from .review import export_review
from .workbook import export_workbook


def import_chat(source, output, *, city, kit, event):
    if not all(v.strip() for v in (city, kit, event)):
        raise ValueError("Città, kit ed evento sono obbligatori.")
    with Path(source).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"ID", "Foto", *QUESTIONS}
        if (
            not reader.fieldnames
            or len(reader.fieldnames) != len(set(reader.fieldnames))
            or not required.issubset(reader.fieldnames)
        ):
            raise ValueError("CSV atteso: ID,Foto,Q1,...,Q11 (intestazioni uniche).")
        records = []
        for row in reader:
            if None in row:
                raise ValueError(
                    "Riga CSV con colonne extra: racchiudere tra virgolette testi con virgole."
                )
            r = dict(
                id=row["ID"],
                source=row["Foto"],
                city=city.strip(),
                kit=kit.strip(),
                answers={},
                originals={},
                reviewed={},
                issues={},
                notes={},
                provenance={"method": "Trascrizione in chat, importazione locale"},
            )
            for q in QUESTIONS:
                raw = (row[q] or "").strip()
                if not raw or raw == "DA_VERIFICARE":
                    value = None
                    r["issues"][
                        q
                    ] = "Da verificare sulla foto; indicare un valore o __BLANK__ nella revisione."
                elif raw == "999":
                    value = None
                elif q == "Q2":
                    value = raw
                else:
                    try:
                        value = int(raw)
                    except ValueError as exc:
                        raise ValueError(
                            f"{r['id']} {q}: codice non valido {raw!r}"
                        ) from exc
                r["answers"][q] = value
                r["originals"][q] = (
                    raw
                    if q == "Q2" or value is None
                    else OPTIONS[q][value] if 0 <= value < len(OPTIONS[q]) else raw
                )
                r["reviewed"][q] = False
            records.append(r)
    data = validate(dict(version=1, event=event.strip(), records=records))
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("La cartella di importazione deve essere nuova o vuota.")
    output.mkdir(parents=True, exist_ok=True)
    save(data, output / "bozza.json")
    export_review(data, output / "revisione.csv")
    export_workbook(data, output / "bozza.xlsx", draft=True)
    return data
