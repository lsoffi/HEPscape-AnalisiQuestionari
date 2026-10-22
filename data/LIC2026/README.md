# Lucania is comics — LIC2026

Raccolta trascritta: **113 questionari distinti**: 63 del primo lotto, 18 aggiunti l’11 ottobre 2026 (IMG_2423.JPG–IMG_2440.JPG, numeri manoscritti 65–82) e 32 aggiunti il 22 ottobre 2026. Il primo lotto comprendeva 63 foto rispetto alle 64 inizialmente previste; non è stata inventata la scheda mancante.

Nel lotto dell’11 ottobre Q2 è vuota nelle schede 67 e 77, Q6 nella 67 e Q5 nella 65. Il commento a margine della scheda 71, «TROPPO VELOCE COI BIMBI», è conservato nelle note.

Il lotto del 22 ottobre comprende 36 fotografie (IMG_2537.JPG–IMG_2572.JPG), tutte registrate nell’[inventario con impronte SHA256](lotto_2026-10-22.csv). Sono escluse le due pagine di sola informativa IMG_2551.JPG e IMG_2552.JPG, la foto duplicata IMG_2567.JPG (stessa scheda 86 di IMG_2566.JPG) e l’intera scheda 85, IMG_2569.JPG, su esplicita istruzione dell’utente. Nessuna risposta della scheda 85 entra nel dataset o nelle analisi.

Le 32 nuove schede hanno tutte le risposte chiuse compilate. Q2 è vuota in IMG_2537, IMG_2550, IMG_2559, IMG_2562, IMG_2563, IMG_2565 e IMG_2572. Il numero di IMG_2568 è leggibile come 80: è conservato senza rinumerarlo. IMG_2572, numero 82, è una scheda distinta dalla precedente IMG_2423, anch’essa numerata 82. Gli ID basati sulle fotografie evitano di confondere numeri manoscritti ripetuti.

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
