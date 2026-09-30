"""Choose kit/event-city output and select matching workbook records."""

import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

KITS = ("Roma", "Bari", "Perugia", "Pisa", "Padova")


def normalize(value):
    return " ".join(value.strip().casefold().split())


def select_rows(rows, kit=None, city=None):
    if (kit is None) != (city is None):
        raise ValueError("Specificare insieme kit e città dell’evento.")
    if kit is None:
        return rows
    selected = [
        r
        for r in rows
        if normalize(r[13]) == normalize(kit) and normalize(r[12]) == normalize(city)
    ]
    if not selected:
        raise ValueError(
            f"Nessuna scheda per kit {kit}, evento a {city}. Controllare le colonne dell’Excel."
        )
    return selected


def destination(args):
    # Explicit output alone keeps the existing all-workbook batch workflow.
    if args.out is not None and args.kit is None and args.city is None:
        return args.out, None, None
    kit, city = args.kit, args.city
    if not kit or not city:
        if not sys.stdin.isatty():
            raise ValueError(
                "Per l’analisi automatica specificare --kit e --city, oppure --out per analizzare tutto il workbook."
            )
        if not kit:
            kit = input(
                "Di quale città è il tuo kit? (Roma, Bari, Perugia, Pisa, Padova): "
            )
        if not city:
            city = input("In quale città si è svolto l’evento? ")
    canonical = {normalize(k): k for k in KITS}
    if normalize(kit) not in canonical:
        raise ValueError("Kit ammessi: " + ", ".join(KITS))
    kit, city = canonical[normalize(kit)], " ".join(city.split())
    if not city:
        raise ValueError("La città dell’evento non può essere vuota.")
    slug = (
        unicodedata.normalize("NFKD", city.replace("’", "-")).encode("ascii", "ignore").decode().lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    if not slug:
        raise ValueError("Nome città non utilizzabile per la cartella.")
    output = args.out or (
        Path("kits") / kit.lower() / slug / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    )
    return output, kit, city
