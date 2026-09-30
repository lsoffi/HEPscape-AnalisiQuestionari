"""Command line entry point; no network except the explicit 'extract' command."""

import argparse
import json
import os
import re
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
    ex = sub.add_parser(
        "extract", help="Legge le foto tramite OpenAI, produce bozza e revisione"
    )
    ex.add_argument(
        "images", nargs="+", help="File JPG/PNG/WEBP o cartelle (non ricorsive)"
    )
    ex.add_argument("--out", type=Path, required=True)
    ex.add_argument("--city", required=True)
    ex.add_argument("--kit", required=True)
    ex.add_argument("--event", default="Evento ERNEST - ERN 2026")
    ex.add_argument(
        "--prefix",
        required=True,
        help="Prefisso univoco per il lotto, es. ROMA-2026-01",
    )
    ex.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL"),
        help="Modello con vision e structured outputs disponibile nel proprio account",
    )
    ex.add_argument(
        "--send-to-openai",
        action="store_true",
        help="Autorizza invio delle foto all’API OpenAI e relativi costi",
    )
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
    if args.command == "extract":
        from .photos import expand_paths, extract

        if not all(v.strip() for v in (args.city, args.kit, args.event)):
            raise ValueError("Città, kit ed evento non possono essere vuoti.")
        if not args.send_to_openai:
            raise ValueError(
                "Per leggere le foto con l’API aggiungere --send-to-openai. Foto inviate a OpenAI; uso a pagamento."
            )
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.prefix):
            raise ValueError(
                "Il prefisso deve contenere solo lettere ASCII, numeri, punti, trattini o underscore, iniziando con lettera/numero."
            )
        if not args.model:
            raise ValueError(
                "Specificare --model oppure OPENAI_MODEL (vision + structured outputs)."
            )
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "Impostare OPENAI_API_KEY nel proprio ambiente; non inserirla nel repository."
            )
        paths = expand_paths(args.images)
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ValueError(
                'Installare il supporto vision: pip install -e ".[vision]"'
            ) from exc
        # Bounded timeouts and standard SDK retries for transient network errors.
        with OpenAI(timeout=120.0, max_retries=2) as client:
            data, errors = extract(
                client,
                paths,
                args.out,
                city=args.city,
                kit=args.kit,
                event=args.event,
                prefix=args.prefix,
                model=args.model,
            )
        if data["records"]:
            export_review(data, args.out / "revisione.csv")
            export_workbook(data, args.out / "bozza.xlsx", draft=True)
        print(
            f"Trascritte {len(data['records'])} schede; {len(errors)} foto escluse/in errore. Controllare errori.json e revisione.csv."
        )
        return 2 if errors else 0
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
