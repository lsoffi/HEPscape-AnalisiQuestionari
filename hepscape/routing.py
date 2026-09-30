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
    if kit is None and city is None:
        return rows
    selected = [
        r
        for r in rows
        if (kit is None or normalize(r[13]) == normalize(kit))
        and (city is None or normalize(r[12]) == normalize(city))
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
    if kit is None:
        if not sys.stdin.isatty():
            raise ValueError(
                "Per l’analisi automatica specificare --kit Roma (o un altro kit), --kit tutti, oppure --out."
            )
        kit = input(
            "Quale kit vuoi analizzare? (Roma, Bari, Perugia, Pisa, Padova, tutti): "
        )
    canonical = {normalize(k): k for k in KITS}
    canonical.update({"tutti": None, "all": None})
    if normalize(kit) not in canonical:
        raise ValueError("Kit ammessi: " + ", ".join(KITS) + ", tutti")
    kit = canonical[normalize(kit)]
    if city is None and not args.all_locations and sys.stdin.isatty():
        from .workbook import read_workbook

        rows = select_rows(read_workbook(args.workbook), kit=kit)
        locations = sorted(
            {normalize(r[12]): " ".join(r[12].split()) for r in rows}.values(),
            key=normalize,
        )
        print(
            "Location disponibili per " + ("kit " + kit if kit else "tutti i kit") + ":"
        )
        print("  0. Tutte le location / tutti i dati")
        for number, name in enumerate(locations, 1):
            print(f"  {number}. {name}")
        choice = input("Scegli il numero della location oppure 0 per tutte: ").strip()
        if not choice.isdigit() or not 0 <= int(choice) <= len(locations):
            raise ValueError(
                "Selezione location non valida: usare uno dei numeri elencati."
            )
        city = locations[int(choice) - 1] if int(choice) else None
    slug = "tutte-le-citta"
    if city is not None:
        city = " ".join(city.split())
        if not city:
            raise ValueError("La città dell’evento non può essere vuota.")
        slug = (
            unicodedata.normalize("NFKD", city.replace("’", "-"))
            .encode("ascii", "ignore")
            .decode()
            .lower()
        )
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        if not slug:
            raise ValueError("Nome città non utilizzabile per la cartella.")
    root = Path("kits") / kit.lower() if kit else Path("reports/tutti-i-kit")
    output = args.out or (root / slug / datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    return output, kit, city
