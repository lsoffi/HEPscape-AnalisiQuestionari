"""Local-only questionnaire import, review and analysis."""

import argparse
import json
import sys
from pathlib import Path
from .schema import load, save, validate
from .review import export_review, apply_review
from .workbook import export_workbook


def parser():
    p = argparse.ArgumentParser(
        description="HEPscape! - foto, revisione, Excel, grafici"
    )
    sub = p.add_subparsers(dest="command", required=True)
    chat = sub.add_parser(
        "import-chat",
        help="CSV trascritto in chat -> bozza Excel e revisione, tutto in locale",
    )
    chat.add_argument("source", type=Path)
    chat.add_argument("--out", required=True, type=Path)
    chat.add_argument("--city", required=True)
    chat.add_argument("--kit", required=True)
    chat.add_argument("--event", required=True)
    rev = sub.add_parser("review", help="Esporta o applica un CSV di revisione")
    rev.add_argument("dataset", type=Path)
    group = rev.add_mutually_exclusive_group(required=True)
    group.add_argument("--export", type=Path)
    group.add_argument("--apply", type=Path)
    rev.add_argument(
        "--out", type=Path, help="JSON revisionato (richiesto con --apply)"
    )
    wb = sub.add_parser("workbook", help="JSON verificato -> Excel")
    wb.add_argument("dataset", type=Path)
    wb.add_argument("--out", required=True, type=Path)
    mg = sub.add_parser(
        "merge", help="Unisce lotti dello stesso evento preservando città e kit"
    )
    mg.add_argument("datasets", nargs="+", type=Path)
    mg.add_argument("--out", required=True, type=Path)
    pl = sub.add_parser("plots", help="Excel -> tutti i grafici, word wall e PDF")
    pl.add_argument("workbook", type=Path)
    pl.add_argument(
        "--out",
        type=Path,
        help="Destinazione esplicita; senza filtri analizza tutto il workbook",
    )
    pl.add_argument(
        "--kit",
        help="Kit da analizzare: Roma, Bari, Perugia, Pisa, Padova oppure tutti",
    )
    pl.add_argument("--city", help="Città in cui si è svolto l’evento")
    pl.add_argument(
        "--event",
        default="Tutti gli eventi",
        help="Titolo del report, non un filtro sui dati",
    )
    pl.add_argument(
        "--compare-kits",
        action="store_true",
        help="Aggiunge confronti descrittivi tra kit se sono presenti almeno due kit",
    )
    return p


def merge(datasets):
    if len({d["event"] for d in datasets}) != 1:
        raise ValueError(
            "Gli eventi non coincidono: correggere i metadati prima di unire i lotti."
        )
    hashes = [
        r["source_sha256"]
        for d in datasets
        for r in d["records"]
        if r.get("source_sha256")
    ]
    if len(hashes) != len(set(hashes)):
        raise ValueError("La stessa foto è presente in più lotti.")
    return validate(
        {
            "version": 1,
            "event": datasets[0]["event"],
            "records": [r for d in datasets for r in d["records"]],
        },
        require_review=True,
    )


def run(args):
    if args.command == "import-chat":
        from .chat_import import import_chat

        data = import_chat(
            args.source, args.out, city=args.city, kit=args.kit, event=args.event
        )
        print(
            f"Importate {len(data['records'])} schede. Controllare bozza.xlsx e compilare revisione.csv."
        )
        return 0
    if args.command == "review":
        data = load(args.dataset)
        if args.export:
            args.export.parent.mkdir(parents=True, exist_ok=True)
            export_review(data, args.export)
        else:
            if not args.out:
                raise ValueError("--out obbligatorio con --apply.")
            save(apply_review(data, args.apply), args.out)
        return 0
    if args.command == "workbook":
        export_workbook(load(args.dataset, require_review=True), args.out)
    elif args.command == "merge":
        save(merge([load(p, require_review=True) for p in args.datasets]), args.out)
    elif args.command == "plots":
        from .plots import generate

        from .routing import destination

        output, kit, city = destination(args)
        generate(
            args.workbook,
            output,
            args.event,
            kit=kit,
            city=city,
            compare_kits=args.compare_kits,
        )
        print(f"Risultati salvati in: {output.resolve()}")
    return 0


def main():
    args = parser().parse_args()
    try:
        return run(args)
    except (ValueError, OSError, KeyError, EOFError, json.JSONDecodeError) as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
