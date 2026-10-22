"""Aggregate the two canonical collections, without kit or city comparisons."""

import hashlib
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hepscape.plots import generate
from hepscape.schema import QUESTIONS
from hepscape.workbook import read_workbook


def main():
    sources = [ROOT / "data/ern2026/questionari.xlsx", ROOT / "data/LIC2026/questionari.xlsx"]
    output = ROOT / "reports/complessivo"
    rows, provenance = [], []
    for source in sources:
        selected = read_workbook(source)
        rows.extend(selected)
        provenance.append({
            "path": str(source.relative_to(ROOT)),
            "questionnaires": len(selected),
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        })
    if len({row[0] for row in rows}) != len(rows):
        raise ValueError("ID duplicati tra le raccolte: verificare prima dell'aggregazione.")
    # The temporary interchange contains each canonical row exactly once.
    with TemporaryDirectory() as temp:
        workbook = Path(temp) / "questionari_complessivi.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.title = "Dati codificati"
        ws.append(["ID", *QUESTIONS, "Città", "Origine del kit"])
        for row in rows:
            ws.append(row)
        wb.save(workbook)
        assert read_workbook(workbook) == rows
        generate(workbook, output, "ERN2026 e Lucania is comics - dati complessivi",
                 compare_kits=False, compare_cities=False,
                 source_description="data/ern2026/questionari.xlsx e data/LIC2026/questionari.xlsx")
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["sources"] = provenance
    manifest["unique_questionnaire_ids"] = len(rows)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Report complessivo: {len(rows)} questionari")


if __name__ == "__main__":
    main()
