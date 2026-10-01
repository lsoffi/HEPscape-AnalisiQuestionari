# Provenienza e riproducibilità

## Lotto iniziale

109 schede del questionario ERNEST relative all’attività HEPscape!, trascritte e verificate con le correzioni confermate dal titolare dei dati. Città: Avezzano; origine del kit: Roma. La denominazione generale delle figure è «HEPscape! · Evento ERNEST – ERN 2026».

- `data/ern2026/questionari.xlsx` è ora il workbook unico dei lotti Roma, Bari, Pisa e Perugia/Terni (276 schede); conserva risposte e codici delle 109 schede Roma.
- `data/ern2026/trascrizione_storica.json` conserva risposte, annotazioni e storia delle verifiche della sessione, con i percorsi personali ridotti ai soli nomi dei file.
- `data/ern2026/lotti/roma.json` conserva il lotto Roma nel formato del nuovo programma. I codici provengono dal workbook verificato; non da una nuova interpretazione delle foto.
- `kits/roma/HEPscape_ERN2026_slide_originali.pdf` è una copia della raccolta finale della sessione originale.
- `reports/ern2026/HEPscape_raccolta_grafici.pdf`, i PNG/SVG, i CSV, il word wall e il manifest sono rigenerati dal nuovo programma portabile.

La raccolta rigenerata usa gli stessi dati e criteri di quella originale. Nei pareggi delle frequenze lessicali usa un ordinamento alfabetico esplicito; non cambia i conteggi. Il confronto automatico dell’Excel ricreato verifica tutte le righe ID/Q1–Q11/città/kit. La grafica e i metadati interni dei file possono variare con le versioni delle librerie.

## Lotto Bari

98 schede lette visivamente in chat dalla scansione `hepscape_bari_survey1.pdf`, una scheda per pagina. Kit Bari, location Bari, stesso Evento ERNEST - ERN 2026, confermati dall’utente. Gli 11 dubbi A–K sono stati risolti esplicitamente dall’utente il 30 settembre 2026; le altre risposte sono state controllate visivamente in chat, senza conferma umana individuale. Il campo `reviewed` indica il completamento di questo controllo: la provenienza distingue il metodo, e `review_log` conserva le 11 decisioni dell’utente.

- `data/ern2026/lotti/bari.json`: 98 schede con pagina sorgente e storia delle correzioni.
- `data/ern2026/questionari_verificati.json`: unione attuale dei quattro lotti (276 schede).
- `kits/bari/bari/ERN2026/`: report, grafici e tabelle filtrati sul kit Bari e location Bari.
- Le risposte vuote confermate D (pagina 39, Q2) e J (pagina 74, Q8) sono `null` nel JSON e 999 nell’Excel. L’annotazione «PIÙ O MENO» della pagina 74 resta nelle note.

La scansione e i ritagli usati per la revisione non sono pubblicati. I report preesistenti sotto `reports/ern2026/` restano riferiti alle sole 109 schede Roma.

## Lotto Pisa

23 schede da una tabella fornita direttamente dall’utente in chat, kit Pisa e città Pisa, stesso Evento ERNEST - ERN 2026. La fonte è conservata in `data/ern2026/lotti/pisa_tabella_originale.csv`; il dataset convertito è `data/ern2026/lotti/pisa.json`.

Per Q1 e Q3–Q7 si applica esclusivamente la conversione 2→0, 1→1, 0→2. Q8 e Q11: sì→1, no→0. Genere ed età seguono la legenda comune; i vuoti diventano `null` nel JSON e 999 nel workbook. Q2 è convertita in maiuscolo, conservando il testo originale nel foglio delle risposte originali. Il campo `reviewed` indica il controllo della conversione della tabella fornita, non una verifica sulle fotografie.

«INGRESSI BELLO?» (N=11) conserva il punto interrogativo della fonte. N=18 e N=20 sono identiche ma restano due schede distinte, come nella tabella. Sono disponibili il workbook Pisa in `kits/pisa/pisa/ERN2026/questionari_Pisa.xlsx` e il workbook unico in `data/ern2026/questionari.xlsx`. I report Roma/Bari già pubblicati conservano il proprio ambito e non includono Pisa.

## Lotto Perugia / Terni

46 schede trascritte visivamente da `Survey1_Terni.pdf`, una per pagina. Kit Perugia, location Terni e stesso Evento ERNEST - ERN 2026 confermati dall’utente. I punti A–F sono stati risolti in chat il 1 ottobre 2026:

| Punto | Pagina PDF | Domanda | Risposta confermata | Codice |
| --- | --- | --- | --- | --- |
| A | 18 | Q6 | In parte | 1 |
| B | 20 | Q7 | A volte | 1 |
| C | 25 | Q1 | Mi è piaciuta tantissimo | 0 |
| D | 25 | Q6 | Sì, molto | 0 |
| E | 26 | Q10 | 15–18 | 2 |
| F | 46 | Q2 | DIVERTENTE BELLO | Testo |

Le altre risposte sono state controllate visivamente in chat, senza conferma umana individuale; `reviewed` indica il completamento di questo controllo. Il foglio delle risposte originali contiene la trascrizione delle opzioni selezionate e dei testi, non le immagini. `data/ern2026/lotti/perugia_terni.json` conserva i riferimenti alle pagine, l’hash del PDF e le note delle sei decisioni. Le scansioni e i ritagli non sono pubblicati.

I risultati dedicati sono in `kits/perugia/terni/ERN2026/`. Il confronto Roma/Bari/Pisa conserva il proprio ambito di tre kit.

## Nuove foto

Le foto vengono lette nella conversazione dell’utente, seguendo `docs/PROMPT_CHAT.md`. Il programma importa il CSV in locale e imposta tutte le risposte come da revisionare, anche se la chat le ha indicate come sicure. I JSON conservano il nome della foto, la trascrizione importata e la storia delle correzioni. L’importazione non calcola hash delle foto e non rileva automaticamente due scatti della stessa scheda: il controllo resta umano.

Il CSV non conserva tutte le conversazioni: archivia separatamente eventuali annotazioni e chiarimenti. La correttezza dei codici non garantisce l’accuratezza della lettura; confronta ogni scheda con la fotografia.

## Organizzazione del codice

- `schema.py`: domande, opzioni e validazione; unica fonte della codifica.
- `chat_import.py`: importazione locale del CSV ottenuto in chat.
- `review.py`: esportazione/applicazione delle correzioni con controllo della bozza di provenienza.
- `workbook.py`: esportazione Excel e lettura rigorosa dell’Excel per l’analisi.
- `plots.py`: tavole descrittive, conteggi e denominatori calcolati dal workbook.
- `wordwall.py`: disposizione deterministica delle parole per frequenza per scheda.
- `cli.py`: comandi `import-chat`, `review`, `workbook`, `merge`, `plots`.

I file di lavoro nuovi vanno in `work/`, le foto in `photos/`. Entrambe le cartelle sono escluse da Git. Per una nuova pubblicazione verificata, copiare intenzionalmente solo i dati e i risultati da condividere in una nuova sottocartella di `data/` e `reports/`.
