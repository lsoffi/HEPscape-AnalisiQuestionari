"""Explicit, auditable human review. Empty correction means keep proposal."""

import copy
import csv
import hashlib
import json
from pathlib import Path
from .schema import QUESTIONS, validate, validate_answer


def csv_text(value):
    text = str(value)
    return "'" + text if text.startswith(("=", "+", "-", "@", "\t", "\r")) else text


def fingerprint(record, q):
    payload = [
        record["id"],
        q,
        record["answers"][q],
        record.get("source_sha256"),
        record.get("issues", {}).get(q),
    ]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False).encode()).hexdigest()


def export_review(data, path):
    validate(data)
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "domanda",
                "foto",
                "proposta",
                "motivo",
                "correzione",
                "confermato",
                "controllo",
            ],
        )
        writer.writeheader()
        for r in data["records"]:
            for q in QUESTIONS:
                writer.writerow(
                    dict(
                        id=r["id"],
                        domanda=q,
                        foto=csv_text(r.get("source", "")),
                        proposta=(
                            "__BLANK__"
                            if r["answers"][q] is None
                            else csv_text(r["answers"][q])
                        ),
                        motivo=csv_text(
                            r.get("issues", {}).get(
                                q, "Verificare anche le letture apparentemente chiare"
                            )
                        ),
                        correzione="",
                        confermato="SI" if r["reviewed"][q] else "",
                        controllo=fingerprint(r, q),
                    )
                )


def apply_review(data, path):
    result = copy.deepcopy(validate(data))
    records = {r["id"]: r for r in result["records"]}
    seen = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = row["id"], row["domanda"]
            if key in seen or key[0] not in records or key[1] not in QUESTIONS:
                raise ValueError(f"Riga di revisione duplicata o sconosciuta: {key}")
            seen.add(key)
            r, q = records[key[0]], key[1]
            if row["controllo"] != fingerprint(r, q):
                raise ValueError(
                    f"Revisione obsoleta: {key}. Rigenerare il CSV dalla bozza corretta."
                )
            confirmation = row["confermato"].strip().upper()
            if confirmation not in ("", "SI", "SÌ", "YES", "NO"):
                raise ValueError(f"{key}: confermato deve essere SI o vuoto.")
            if confirmation not in ("SI", "SÌ", "YES"):
                r["reviewed"][q] = False
                continue
            correction = row["correzione"].strip()
            previous = r["answers"][q]
            if correction:
                value = (
                    None
                    if correction == "__BLANK__"
                    else correction if q == "Q2" else int(correction)
                )
            else:
                if (
                    previous is None
                    and q in r.get("issues", {})
                    and r.get("statuses", {}).get(q) != "blank"
                ):
                    raise ValueError(
                        f"{key}: lettura incerta senza proposta; inserire codice/testo oppure __BLANK__."
                    )
                value = previous
            validate_answer(q, value)
            r["answers"][q] = value
            r["reviewed"][q] = True
            r.setdefault("review_log", []).append(
                {"question": q, "previous": previous, "value": value}
            )
    expected = {(r["id"], q) for r in result["records"] for q in QUESTIONS}
    if seen != expected:
        raise ValueError(
            "CSV incompleto: conservare tutte le righe, anche quelle già confermate."
        )
    return validate(result)
