# Lucania is comics — LIC2026

Raccolta trascritta: **81 foto distinte**: 63 del primo lotto e 18 aggiunte l’11 ottobre 2026 (IMG_2423.JPG–IMG_2440.JPG, numeri manoscritti 65–82). Il primo lotto comprendeva 63 foto rispetto alle 64 inizialmente previste; non è stata inventata la scheda mancante.

Nel nuovo lotto Q2 è vuota nelle schede 67 e 77, Q6 nella 67 e Q5 nella 65. Il commento a margine della scheda 71, «TROPPO VELOCE COI BIMBI», è conservato nelle note.

- Città: **Potenza**
- Origine del kit: **Roma** (stessa denominazione degli altri dataset)
- evento: **Lucania is comics**
- Workbook: [questionari.xlsx](questionari.xlsx), con la struttura di `../ern2026/questionari.xlsx`.
- Dati riutilizzabili: [questionari.json](questionari.json).
- ID univoci `LIC2026-IMG<n>` associati alle fotografie; la numerazione manoscritta è conservata nelle note.

Trascrizione completata e chiarimenti applicati. Correzioni confermate dall’utente:

- Scheda 2, Q10: «Meno di 11» (nella foto sono marcate due età).
- Scheda 17, Q3: «Sì, molto» (segni multipli nella foto).
- Scheda 30, Q2: mantenere solo «Luminosa».
- Foto IMG_2366.JPG: numero 64 assegnato alla scheda senza numero visibile.
- Foto IMG_2396.JPG: numero 45 confermato.

I numeri 45 e 64 compaiono su due schede ciascuno: le fotografie e gli ID sono distinti, quindi tutte le risposte sono conservate. Non è stata aggiunta una riga fittizia per raggiungere 64 questionari.

Grafici, tabelle e report: [Roma / Potenza / LIC2026](../../kits/roma/potenza/LIC2026/).

Per rigenerare il report dalla radice del repository:

```sh
hepscape plots data/LIC2026/questionari.xlsx --kit Roma --city Potenza --event "Lucania is comics" --out kits/roma/potenza/LIC2026
```

La colonna `evento` è presente sia in **Dati codificati** sia in **Risposte originali**. Per la raccolta ERN2026 il valore è `ern2026`.
Le risposte dubbie devono essere verificate; `999` indica solo risposte effettivamente vuote. Le fotografie originali restano fuori dal repository pubblico.
