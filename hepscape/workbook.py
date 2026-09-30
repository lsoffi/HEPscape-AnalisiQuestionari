"""Portable Excel interchange: existing workbook layout, codes and originals."""

from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter
from .schema import QUESTIONS, OPTIONS, coded, validate, validate_answer


def put(ws, row, col, value):
    c = ws.cell(row, col, value)
    # Handwritten text that starts with '=' must remain text, never a formula.
    if isinstance(value, str):
        c.data_type = "s"
    c.alignment = Alignment(vertical="top", wrap_text=True)
    c.font = Font(name="Calibri", size=11, color="18304F")
    return c


def export_workbook(data, path, *, draft=False):
    validate(data, require_review=not draft)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Dati codificati"
    raw = wb.create_sheet("Risposte originali")
    n = len(data["records"])
    put(
        ws,
        1,
        1,
        f"HEPscape! | {data['event']} | {n} questionari"
        + (" | BOZZA DA VERIFICARE" if draft else ""),
    )
    ws.merge_cells("A1:N1")
    ws.row_dimensions[1].height = 30
    headers = ["ID", *QUESTIONS, "Città", "Origine del kit"]
    for col, h in enumerate(headers, 1):
        put(ws, 2, col, QUESTIONS.get(h, h))
        legend = "999 = risposta mancante"
        if h in OPTIONS:
            legend = (
                "\n".join(f"{i} = {v}" for i, v in enumerate(OPTIONS[h]))
                + "\n"
                + legend
            )
        elif h == "Q2":
            legend = "Testo in MAIUSCOLO\n" + legend
        else:
            legend = "Metadato della scheda"
        put(ws, 3, col, legend)
        put(ws, 6, col, h)
    ws.row_dimensions[2].height = 105
    ws.row_dimensions[3].height = 165
    raw_headers = [
        "ID",
        *QUESTIONS,
        "Note della scheda",
        "Foto originale",
        "Città",
        "Origine del kit",
        "Revisione",
        "SHA256 foto",
    ]
    for col, h in enumerate(raw_headers, 1):
        put(raw, 1, col, h)
    for index, r in enumerate(data["records"], 7):
        values = [r["id"]]
        for q in QUESTIONS:
            # No 999 for unreadable marks: it is not a verified blank.
            values.append(
                "DA VERIFICARE"
                if draft and q in r.get("issues", {}) and not r["reviewed"][q]
                else coded(q, r["answers"][q])
            )
        values += [r["city"], r["kit"]]
        for col, value in enumerate(values, 1):
            put(ws, index, col, value)
        originals = [r.get("originals", {}).get(q, "") for q in QUESTIONS]
        notes = "\n".join(f"{q}: {v}" for q, v in r.get("notes", {}).items())
        vals = [
            r["id"],
            *originals,
            notes,
            r.get("source", ""),
            r["city"],
            r["kit"],
            "Confermata" if all(r["reviewed"].values()) else "Da verificare",
            r.get("source_sha256", ""),
        ]
        for col, value in enumerate(vals, 1):
            put(raw, index - 5, col, value)
        ws.row_dimensions[index].height = max(34, len(str(values[2])) // 43 * 16 + 20)
        raw.row_dimensions[index - 5].height = max(40, len(notes) // 45 * 16 + 20)
    for sheet, header_row, last_row, last_col in [
        (ws, 6, n + 6, 14),
        (raw, 1, n + 1, 18),
    ]:
        sheet.sheet_view.showGridLines = False
        sheet.freeze_panes = f"B{header_row+1}"
        for col in range(1, last_col + 1):
            sheet.column_dimensions[get_column_letter(col)].width = (
                45 if col == 3 else 25
            )
            cell = sheet.cell(header_row, col)
            cell.fill = PatternFill("solid", fgColor="234A8C")
            cell.font = Font(name="Calibri", bold=True, color="FFFFFF")
        sheet.column_dimensions["A"].width = 23
        table = Table(
            displayName="DatiHEPscape" if sheet == ws else "OriginaliHEPscape",
            ref=f"A{header_row}:{get_column_letter(last_col)}{last_row}",
        )
        table.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium2", showRowStripes=True
        )
        sheet.add_table(table)
    for q in OPTIONS:
        col = get_column_letter(int(q[1:]) + 1)
        dv = DataValidation(
            type="list",
            formula1='"' + ",".join(map(str, range(len(OPTIONS[q])))) + ',999"',
            allow_blank=False,
        )
        dv.errorTitle = "Codice non valido"
        dv.error = "Usare i codici in legenda; 999 solo per una risposta vuota."
        dv.showErrorMessage = True
        ws.add_data_validation(dv)
        dv.add(f"{col}7:{col}{n+6}")
    ws.conditional_formatting.add(
        f"B7:L{n+6}",
        CellIsRule(
            operator="equal",
            formula=["999"],
            fill=PatternFill("solid", fgColor="E8F1DC"),
        ),
    )
    for cell in ws[2] + ws[3]:
        cell.fill = PatternFill("solid", fgColor="F0F4FA")
    wb.save(path)


def read_workbook(path):
    wb = load_workbook(path, data_only=False, read_only=True)
    ws = wb["Dati codificati"]
    if "BOZZA" in str(ws.cell(1, 1).value):
        raise ValueError(
            "Workbook in bozza: completare la revisione prima dell’analisi."
        )
    header = next(
        (
            i
            for i, row in enumerate(ws.iter_rows(values_only=True), 1)
            if list(row[:12]) == ["ID", *QUESTIONS]
        ),
        None,
    )
    if header is None:
        raise ValueError("Intestazioni ID, Q1..Q11 non trovate.")
    hdr = list(next(ws.iter_rows(min_row=header, max_row=header, values_only=True)))
    if "Città" not in hdr or "Origine del kit" not in hdr:
        raise ValueError("Mancano le colonne Città / Origine del kit.")
    rows, ids = [], set()
    for row in ws.iter_rows(min_row=header + 1, values_only=True):
        if all(v is None for v in row):
            continue
        identity = str(row[0])
        if row[0] is None or identity in ids:
            raise ValueError("ID vuoto o duplicato nel workbook.")
        ids.add(identity)
        values = []
        for q, value in zip(QUESTIONS, row[1:12]):
            if value == 999:
                values.append(999)
                continue
            # Reject unreviewed cells, formulas, blank Excel cells and unknown codes.
            if value is None:
                raise ValueError(
                    f"{identity} {q}: cella vuota, usare 999 per un mancante confermato."
                )
            validate_answer(q, value)
            if q == "Q2" and value == "DA VERIFICARE":
                raise ValueError(f"{identity} {q}: revisione incompleta.")
            values.append(value)
        city, kit = row[hdr.index("Città")], row[hdr.index("Origine del kit")]
        if not city or not kit:
            raise ValueError(f"{identity}: metadati mancanti.")
        rows.append((identity, *values, city, kit))
    wb.close()
    if not rows:
        raise ValueError("Workbook senza risposte.")
    return rows
