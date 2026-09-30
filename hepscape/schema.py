"""Single source of truth for the 11-question Italian ERNEST questionnaire."""

import json
import re
from pathlib import Path

QUESTIONS = {
    "Q1": "Quanto ti è piaciuta l’attività?",
    "Q2": "Scegli due o tre parole per descrivere la tua esperienza nell’escape room.",
    "Q3": "Hai imparato qualcosa di nuovo sulla scienza, sulla ricerca o sui ricercatori?",
    "Q4": "Dopo l’escape room, sei più curioso/a di scoprire cose sulla scienza?",
    "Q5": "Dopo l’escape room, sei più interessato/a a scoprire cosa fanno le ricercatrici e i ricercatori?",
    "Q6": "È stato facile per te partecipare all’attività?",
    "Q7": "Quanto spesso hai la possibilità di partecipare a un’escape room scientifica come questa?",
    "Q8": "Prima di oggi, eri mai stato/a in questo luogo per un’attività didattica?",
    "Q9": "Qual è il tuo genere?",
    "Q10": "Quanti anni hai?",
    "Q11": "Vivi nella stessa città in cui si svolge questa escape room?",
}
OPTIONS = {
    "Q1": ["Mi è piaciuta tantissimo", "Mi è piaciuta", "Non mi è piaciuta molto"],
    "Q3": ["Sì, molto", "Sì, un po’", "No, per niente"],
    "Q4": ["Più curioso/a", "Curioso/a come prima", "Meno curioso/a"],
    "Q5": ["Più interessato/a", "Interessato/a come prima", "Meno interessato/a"],
    "Q6": ["Sì, molto", "In parte", "No"],
    "Q7": ["Spesso", "A volte", "Mai"],
    "Q8": ["No", "Sì"],
    "Q9": ["Femminile", "Maschile", "Altro", "Preferisco non rispondere"],
    "Q10": [
        "Meno di 11",
        "11–14",
        "15–18",
        "19–25",
        "26–40",
        "41–60",
        "Più di 60",
        "Preferisco non rispondere",
    ],
    "Q11": ["No", "Sì"],
}
MISSING = 999


def validate_answer(q, value):
    if value is None:
        return
    if q == "Q2":
        if not isinstance(value, str) or not value.strip() or value == "999":
            raise ValueError("Q2 deve essere testo non vuoto oppure null (mancante).")
    elif type(value) is not int or not 0 <= value < len(OPTIONS[q]):
        raise ValueError(f"{q}: codice non valido {value!r}")


def validate(data, require_review=False):
    if data.get("version") != 1 or not str(data.get("event", "")).strip():
        raise ValueError("Versione o nome evento mancante.")
    records = data.get("records", [])
    if not records:
        raise ValueError("Nessun questionario.")
    ids = set()
    for r in records:
        if (
            not isinstance(r.get("id"), str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", r["id"])
            or r["id"] in ids
        ):
            raise ValueError("ID mancanti o duplicati.")
        ids.add(r["id"])
        if not r.get("city") or not r.get("kit"):
            raise ValueError(f"{r['id']}: città e kit sono obbligatori.")
        for field in ("answers", "reviewed"):
            if set(r.get(field, {})) != set(QUESTIONS):
                raise ValueError(
                    f"{r['id']}: {field} deve contenere tutte le 11 domande."
                )
        for q, value in r["answers"].items():
            validate_answer(q, value)
            if type(r["reviewed"][q]) is not bool:
                raise ValueError(f"{r['id']} {q}: reviewed deve essere booleano.")
            if require_review and not r["reviewed"][q]:
                raise ValueError(
                    f"{r['id']} {q}: revisione non completata. Correggere/confermare il CSV."
                )
    return data


def load(path, require_review=False):
    return validate(json.loads(Path(path).read_text(encoding="utf-8")), require_review)


def save(data, path):
    validate(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temp.replace(path)


def coded(q, value):
    return MISSING if value is None else value.upper() if q == "Q2" else value
